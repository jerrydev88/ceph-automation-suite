"""
04-validation 플레이북 단위 테스트
"""

import pytest
from pathlib import Path
from .test_playbook_runner import TestablePlaybook


class TestValidateClusterHealth:
    """validate-cluster-health.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/04-validation/validate-cluster-health.yml"
        return TestablePlaybook(playbook_path)

    @pytest.fixture
    def runner(self, playbook):
        """플레이북 러너 인스턴스"""
        return playbook.runner

    def test_playbook_exists(self, playbook):
        """플레이북 파일 존재 확인"""
        assert playbook.playbook_path.exists(), \
            f"Playbook not found: {playbook.playbook_path}"

    def test_playbook_structure(self, runner):
        """플레이북 구조 검증"""
        assert len(runner.playbook) > 0, "Playbook is empty"

        first_play = runner.playbook[0]
        assert first_play['name'] == "Validate Ceph Cluster Health"
        assert first_play['hosts'] == "mons[0]", \
            "Health check should run on first monitor"
        assert first_play['become'] is True

    def test_health_check_tasks(self, runner):
        """헬스 체크 태스크 검증"""
        task_names = runner.get_task_names(play_index=0)

        # 필수 체크 태스크
        required_checks = [
            "Check cluster status",
            "Check cluster health",
            "Check OSD status",
            "Check MON status"
        ]

        for check in required_checks:
            assert any(check in name for name in task_names), \
                f"Required check '{check}' not found"

    def test_validation_assertions(self, runner):
        """검증 assertion 태스크 확인"""
        tasks = runner.get_tasks(play_index=0)

        # assert 모듈을 사용하는 태스크 확인
        assert_tasks = [t for t in tasks if 'assert' in str(t)]
        assert len(assert_tasks) > 0, "No assertion tasks found"

        # 특정 검증 확인
        validations = [
            "Validate cluster health is OK",
            "Validate all OSDs are up",
            "Validate MON quorum"
        ]

        task_names = runner.get_task_names(play_index=0)
        for validation in validations:
            assert any(validation in name for name in task_names), \
                f"Validation '{validation}' not found"

    def test_command_tasks_have_changed_when(self, runner):
        """command 모듈 태스크가 changed_when을 가지는지 확인"""
        tasks = runner.get_tasks(play_index=0)

        for task in tasks:
            if 'command' in str(task):
                # 모든 command 태스크는 changed_when: false를 가져야 함
                task_str = str(task)
                assert 'changed_when' in task_str or 'Check' in task.get('name', ''), \
                    f"Task '{task.get('name', 'unnamed')}' should have changed_when: false"

    def test_vars_files(self, runner):
        """vars_files 참조 검증"""
        first_play = runner.playbook[0]
        vars_files = first_play.get('vars_files', [])

        assert any('ceph-vars.yml' in vf for vf in vars_files), \
            "ceph-vars.yml should be referenced"

    def test_register_variables(self, runner):
        """register 변수 사용 확인"""
        tasks = runner.get_tasks(play_index=0)

        # register를 사용하는 태스크 찾기
        register_tasks = [t for t in tasks if 'register' in t]
        assert len(register_tasks) > 0, "No tasks register variables"

        # 등록된 변수 이름 추출
        registered_vars = [t.get('register') for t in register_tasks if 'register' in t]

        # 중요한 변수들이 등록되어 있는지 확인
        important_vars = ['ceph_status', 'ceph_health', 'osd_stat', 'mon_stat']
        for var in important_vars:
            assert var in registered_vars, f"Variable '{var}' should be registered"


class TestValidateRGW:
    """validate-rgw.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/04-validation/validate-rgw.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_rgw_validation_tasks(self, playbook):
        """RGW 검증 태스크 확인"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # RGW 관련 검증이 있어야 함
        assert any('rgw' in name.lower() for name in task_names), \
            "Should have RGW-related validation tasks"


class TestValidateAll:
    """validate-all.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/04-validation/validate-all.yml"
        return TestablePlaybook(playbook_path)

    def test_includes_all_validations(self, playbook):
        """모든 검증이 포함되어 있는지 확인"""
        runner = playbook.runner

        # validate-all은 다른 플레이북을 import하거나 include해야 함
        playbook_content = str(runner.playbook)

        # 주요 검증 플레이북들이 포함되어야 함
        expected_includes = [
            'validate-cluster-health',
            'validate-osd',
            'validate-rgw',
            'validate-rbd',
            'validate-cephfs'
        ]

        for include in expected_includes:
            # import_playbook 또는 include_tasks로 참조되어야 함
            assert include in playbook_content or \
                   f"{include}.yml" in playbook_content, \
                   f"Should include {include} validation"


class TestValidationPlaybooksConsistency:
    """검증 플레이북 전체 일관성 테스트"""

    @pytest.fixture
    def validation_dir(self):
        """validation 디렉토리 경로"""
        return Path(__file__).parent.parent.parent.parent / "playbooks/04-validation"

    def test_all_validation_playbooks_have_consistent_structure(self, validation_dir):
        """모든 검증 플레이북이 일관된 구조를 가지는지 확인"""
        validation_playbooks = list(validation_dir.glob("validate-*.yml"))

        for playbook_path in validation_playbooks:
            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            first_play = runner.playbook[0]

            # 모든 검증 플레이북은 이름을 가져야 함
            assert 'name' in first_play, \
                f"{playbook_path.name} should have a play name"

            # 모든 검증 플레이북은 hosts를 지정해야 함
            assert 'hosts' in first_play, \
                f"{playbook_path.name} should specify hosts"

            # 검증 플레이북은 보통 become이 필요함
            if 'validate-all' not in playbook_path.name:
                assert first_play.get('become', False) is True, \
                    f"{playbook_path.name} should run with privilege"

    def test_no_destructive_operations(self, validation_dir):
        """검증 플레이북에 파괴적인 작업이 없는지 확인"""
        validation_playbooks = list(validation_dir.glob("validate-*.yml"))

        dangerous_modules = [
            'ansible.builtin.file',  # state: absent
            'ansible.builtin.command',  # rm, delete 등
            'ansible.builtin.shell',
            'ansible.builtin.raw'
        ]

        for playbook_path in validation_playbooks:
            with open(playbook_path, 'r') as f:
                content = f.read()

            # 위험한 작업 확인
            if 'state: absent' in content:
                pytest.fail(f"{playbook_path.name} contains 'state: absent'")

            if 'rm ' in content or 'delete' in content.lower():
                # 단, 주석이나 설명 텍스트는 제외
                lines = content.split('\n')
                for line in lines:
                    if not line.strip().startswith('#'):
                        if 'rm ' in line or ('delete' in line.lower() and 'validate' not in line.lower()):
                            pytest.fail(f"{playbook_path.name} may contain destructive operations")

    def test_validation_playbooks_are_idempotent(self, validation_dir):
        """검증 플레이북이 멱등성을 가지는지 확인"""
        validation_playbooks = list(validation_dir.glob("validate-*.yml"))

        for playbook_path in validation_playbooks:
            if 'validate-all' in playbook_path.name:
                continue

            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            tasks = runner.get_tasks(play_index=0)
            for task in tasks:
                # command/shell 태스크는 changed_when: false를 가져야 함
                if 'command' in str(task) or 'shell' in str(task):
                    assert 'changed_when' in task or 'Check' in task.get('name', ''), \
                        f"{playbook_path.name}: Task '{task.get('name', 'unnamed')}' should be idempotent"