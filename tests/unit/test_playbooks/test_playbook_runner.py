"""
Ansible 플레이북 실행 테스트를 위한 기본 클래스
"""

import pytest
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess


class PlaybookTestRunner:
    """플레이북 테스트를 위한 헬퍼 클래스"""

    def __init__(self, playbook_path):
        self.playbook_path = Path(playbook_path)
        self.playbook = self.load_playbook()
        self.mock_results = {}

    def load_playbook(self):
        """플레이북 YAML 파일 로드"""
        if not self.playbook_path.exists():
            raise FileNotFoundError(f"Playbook not found: {self.playbook_path}")

        with open(self.playbook_path, 'r') as f:
            return yaml.safe_load(f)

    def get_tasks(self, play_index=0):
        """특정 플레이의 태스크 목록 반환"""
        if not self.playbook or play_index >= len(self.playbook):
            return []

        play = self.playbook[play_index]
        return play.get('tasks', [])

    def get_task_names(self, play_index=0):
        """태스크 이름 목록 반환"""
        tasks = self.get_tasks(play_index)
        return [task.get('name', 'unnamed') for task in tasks]

    def get_handlers(self, play_index=0):
        """핸들러 목록 반환"""
        if not self.playbook or play_index >= len(self.playbook):
            return []

        play = self.playbook[play_index]
        return play.get('handlers', [])

    def validate_task_structure(self, task):
        """태스크 구조 검증"""
        errors = []

        # 태스크는 name을 가져야 함
        if 'name' not in task:
            errors.append("Task missing 'name' field")

        # 태스크는 최소 하나의 모듈을 포함해야 함
        module_keys = [k for k in task.keys() if not k.startswith('_') and k not in [
            'name', 'when', 'with_items', 'loop', 'notify', 'register',
            'vars', 'tags', 'become', 'become_user', 'delegate_to'
        ]]

        if not module_keys:
            errors.append(f"Task '{task.get('name', 'unnamed')}' has no module")

        return errors

    def mock_ansible_run(self, check_mode=False, **kwargs):
        """Ansible 실행을 모의"""
        result = {
            'plays': [],
            'stats': {
                'ok': 0,
                'changed': 0,
                'failed': 0,
                'skipped': 0
            }
        }

        for play_idx, play in enumerate(self.playbook):
            play_result = {
                'name': play.get('name', 'unnamed'),
                'hosts': play.get('hosts', 'all'),
                'tasks': []
            }

            for task in self.get_tasks(play_idx):
                task_result = self._mock_task_execution(task, check_mode)
                play_result['tasks'].append(task_result)

                # 통계 업데이트
                if task_result['failed']:
                    result['stats']['failed'] += 1
                elif task_result['changed']:
                    result['stats']['changed'] += 1
                    result['stats']['ok'] += 1
                elif task_result['skipped']:
                    result['stats']['skipped'] += 1
                else:
                    result['stats']['ok'] += 1

            result['plays'].append(play_result)

        return result

    def _mock_task_execution(self, task, check_mode):
        """개별 태스크 실행 모의"""
        task_name = task.get('name', 'unnamed')

        # 기본 결과
        result = {
            'name': task_name,
            'changed': False,
            'failed': False,
            'skipped': False,
            'msg': 'ok'
        }

        # check_mode에서는 변경 사항이 없음
        if check_mode:
            result['changed'] = False
            result['msg'] = 'check mode, no changes made'
        else:
            # 특정 모듈에 따른 동작 모의
            if 'ansible.builtin.package' in str(task):
                result['changed'] = True
                result['msg'] = 'package installed'
            elif 'ansible.builtin.command' in str(task):
                result['changed'] = True
                result['msg'] = 'command executed'
            elif 'ansible.builtin.lineinfile' in str(task):
                result['changed'] = True
                result['msg'] = 'line modified'
            elif 'ansible.builtin.user' in str(task):
                result['changed'] = True
                result['msg'] = 'user updated'
            elif 'ansible.builtin.service' in str(task):
                result['changed'] = True
                result['msg'] = 'service restarted'

        # when 조건 처리
        if 'when' in task:
            # 간단한 when 조건 평가 모의
            result['skipped'] = True
            result['msg'] = 'conditional check skipped'

        return result


class TestablePlaybook:
    """테스트 가능한 플레이북 래퍼"""

    def __init__(self, playbook_path, inventory_path=None):
        self.playbook_path = playbook_path
        self.inventory_path = inventory_path or "tests/fixtures/ansible_inventory.yml"
        self.runner = PlaybookTestRunner(playbook_path)

    def syntax_check(self):
        """문법 검사 실행"""
        cmd = [
            ".venv/bin/ansible-playbook",
            "--syntax-check",
            "-i", self.inventory_path,
            str(self.playbook_path)
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.returncode == 0

    def dry_run(self):
        """드라이런 (--check) 실행"""
        return self.runner.mock_ansible_run(check_mode=True)

    def get_required_vars(self):
        """플레이북에서 요구하는 변수 목록 추출"""
        required_vars = set()

        for play in self.runner.playbook:
            # vars_files에서 참조하는 파일
            vars_files = play.get('vars_files', [])
            for vf in vars_files:
                if 'secret.yml' in vf:
                    required_vars.add('root_password')
                if 'ceph-vars.yml' in vf:
                    required_vars.add('ceph')

            # 태스크에서 사용하는 변수
            for task in self.runner.get_tasks():
                task_str = str(task)
                if '{{' in task_str and '}}' in task_str:
                    # 간단한 변수 추출 (정규식 대신 단순 파싱)
                    import re
                    vars_in_task = re.findall(r'{{\s*(\w+)', task_str)
                    required_vars.update(vars_in_task)

        return list(required_vars)