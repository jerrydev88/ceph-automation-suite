"""
Ansible 플레이북 문법 검증 테스트
"""

import pytest
import subprocess
from pathlib import Path
import yaml


class TestPlaybookSyntax:
    """플레이북 문법 검증 테스트"""

    @pytest.fixture
    def playbook_dir(self):
        """플레이북 디렉토리 경로"""
        return Path(__file__).parent.parent.parent.parent / "playbooks"

    @pytest.fixture
    def test_inventory(self):
        """테스트용 인벤토리 경로"""
        return Path(__file__).parent.parent.parent / "fixtures" / "ansible_inventory.yml"

    def get_all_playbooks(self, playbook_dir):
        """모든 플레이북 파일 목록 반환"""
        return list(playbook_dir.glob("**/*.yml"))

    def test_playbooks_exist(self, playbook_dir):
        """플레이북 디렉토리 존재 확인"""
        assert playbook_dir.exists(), "playbooks 디렉토리가 존재해야 합니다"
        playbooks = self.get_all_playbooks(playbook_dir)
        assert len(playbooks) > 0, "최소 하나 이상의 플레이북이 있어야 합니다"

    def test_yaml_syntax(self, playbook_dir):
        """YAML 문법 검증"""
        playbooks = self.get_all_playbooks(playbook_dir)
        errors = []

        for playbook in playbooks:
            try:
                with open(playbook, 'r') as f:
                    yaml.safe_load(f)
            except yaml.YAMLError as e:
                errors.append(f"{playbook}: {e}")

        assert not errors, f"YAML 문법 오류:\n" + "\n".join(errors)

    def test_playbook_structure(self, playbook_dir):
        """플레이북 기본 구조 검증"""
        playbooks = self.get_all_playbooks(playbook_dir)
        errors = []

        for playbook in playbooks:
            with open(playbook, 'r') as f:
                content = yaml.safe_load(f)

            if not content:
                continue

            # 플레이북은 리스트여야 함
            if not isinstance(content, list):
                errors.append(f"{playbook}: 플레이북은 리스트 형식이어야 합니다")
                continue

            # 각 플레이 검증
            for i, play in enumerate(content):
                if not isinstance(play, dict):
                    errors.append(f"{playbook}[{i}]: 플레이는 딕셔너리여야 합니다")
                    continue

                # 필수 필드 확인
                if 'hosts' not in play:
                    errors.append(f"{playbook}[{i}]: 'hosts' 필드가 필요합니다")

                if 'tasks' in play and not isinstance(play['tasks'], list):
                    errors.append(f"{playbook}[{i}]: 'tasks'는 리스트여야 합니다")

        assert not errors, f"플레이북 구조 오류:\n" + "\n".join(errors)

    @pytest.mark.skipif(
        not Path("/usr/bin/ansible-playbook").exists() and
        not Path("/usr/local/bin/ansible-playbook").exists(),
        reason="ansible-playbook이 설치되지 않음"
    )
    def test_ansible_syntax_check(self, playbook_dir, test_inventory):
        """Ansible 문법 검사"""
        playbooks = [
            p for p in self.get_all_playbooks(playbook_dir)
            if not p.name.startswith('tasks/')  # tasks 하위는 제외
        ]
        errors = []

        for playbook in playbooks:
            result = subprocess.run(
                ["ansible-playbook", "--syntax-check", str(playbook)],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                errors.append(f"{playbook}:\n{result.stderr}")

        assert not errors, f"Ansible 문법 오류:\n" + "\n".join(errors)


class TestPlaybookBestPractices:
    """플레이북 베스트 프랙티스 검증"""

    @pytest.fixture
    def playbook_dir(self):
        return Path(__file__).parent.parent.parent.parent / "playbooks"

    def test_no_hardcoded_passwords(self, playbook_dir):
        """하드코딩된 패스워드 검출"""
        playbooks = list(playbook_dir.glob("**/*.yml"))
        violations = []

        password_patterns = [
            'password:', 'passwd:', 'pass:',
            'secret:', 'token:', 'api_key:'
        ]

        for playbook in playbooks:
            with open(playbook, 'r') as f:
                lines = f.readlines()

            for i, line in enumerate(lines, 1):
                line_lower = line.lower()
                for pattern in password_patterns:
                    if pattern in line_lower and not line.strip().startswith('#'):
                        # vault 참조는 허용
                        if '!vault' not in line and '{{' not in line:
                            violations.append(
                                f"{playbook}:{i} - 가능한 하드코딩된 인증정보: {line.strip()}"
                            )

        assert not violations, f"보안 위반:\n" + "\n".join(violations)

    def test_use_name_for_tasks(self, playbook_dir):
        """모든 태스크에 name 필드 확인"""
        playbooks = list(playbook_dir.glob("**/*.yml"))
        violations = []

        for playbook in playbooks:
            with open(playbook, 'r') as f:
                try:
                    content = yaml.safe_load(f)
                except:
                    continue

            if not content or not isinstance(content, list):
                continue

            for play_idx, play in enumerate(content):
                if not isinstance(play, dict) or 'tasks' not in play:
                    continue

                for task_idx, task in enumerate(play.get('tasks', [])):
                    if isinstance(task, dict) and 'name' not in task:
                        # block, include_tasks 등은 예외
                        if not any(k in task for k in ['block', 'include_tasks', 'import_tasks']):
                            violations.append(
                                f"{playbook} - Play {play_idx}, Task {task_idx}: name 필드 누락"
                            )

        # 경고만 표시 (실패하지 않음)
        if violations:
            print(f"⚠️  권장사항 위반:\n" + "\n".join(violations[:10]))

    def test_no_become_in_tasks(self, playbook_dir):
        """태스크 레벨 become 사용 검증 (플레이 레벨 권장)"""
        playbooks = list(playbook_dir.glob("**/*.yml"))
        warnings = []

        for playbook in playbooks:
            with open(playbook, 'r') as f:
                try:
                    content = yaml.safe_load(f)
                except:
                    continue

            if not content or not isinstance(content, list):
                continue

            for play in content:
                if not isinstance(play, dict) or 'tasks' not in play:
                    continue

                play_has_become = 'become' in play

                for task in play.get('tasks', []):
                    if isinstance(task, dict) and 'become' in task and not play_has_become:
                        warnings.append(
                            f"{playbook}: 태스크 레벨 become 사용 (플레이 레벨 권장)"
                        )
                        break

        # 경고만 표시
        if warnings:
            print(f"⚠️  베스트 프랙티스 경고:\n" + "\n".join(warnings[:5]))