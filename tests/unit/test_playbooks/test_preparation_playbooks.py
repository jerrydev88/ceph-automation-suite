"""
00-preparation 플레이북 단위 테스트
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from .test_playbook_runner import TestablePlaybook, PlaybookTestRunner


class TestSetupRootSSH:
    """setup-root-ssh.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/00-preparation/setup-root-ssh.yml"
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
        # 플레이북은 2개의 플레이를 포함해야 함
        assert len(runner.playbook) == 2, \
            "setup-root-ssh.yml should have 2 plays"

        # 첫 번째 플레이: Setup Environment
        first_play = runner.playbook[0]
        assert first_play['name'] == "Setup Environment"
        assert first_play['hosts'] == "all"
        assert first_play['become'] is True

        # 두 번째 플레이: Enable SSH Access
        second_play = runner.playbook[1]
        assert "Enable SSH Access" in second_play['name']
        assert second_play['hosts'] == "all"
        assert second_play['become'] is True

    def test_first_play_tasks(self, runner):
        """첫 번째 플레이의 태스크 검증"""
        tasks = runner.get_tasks(play_index=0)
        task_names = runner.get_task_names(play_index=0)

        expected_tasks = [
            "Ensure pip is installed",
            "Ensure virtualenv is installed",
            "Create a virtual environment",
            "Install passlib in the virtual environment"
        ]

        for expected in expected_tasks:
            assert expected in task_names, \
                f"Task '{expected}' not found in first play"

    def test_second_play_tasks(self, runner):
        """두 번째 플레이의 태스크 검증"""
        tasks = runner.get_tasks(play_index=1)
        task_names = runner.get_task_names(play_index=1)

        expected_tasks = [
            "Ensure PermitRootLogin is set to yes in sshd_config",
            "Ensure PasswordAuthentication is enabled in sshd_config",
            "Update root user password"
        ]

        for expected in expected_tasks:
            assert expected in task_names, \
                f"Task '{expected}' not found in second play"

    def test_handlers(self, runner):
        """핸들러 검증"""
        handlers = runner.get_handlers(play_index=1)
        assert len(handlers) > 0, "No handlers defined in second play"

        handler_names = [h.get('name', '') for h in handlers]
        assert "restart sshd" in handler_names, \
            "Handler 'restart sshd' not found"

    def test_vars_files(self, runner):
        """vars_files 참조 검증"""
        second_play = runner.playbook[1]
        vars_files = second_play.get('vars_files', [])

        assert len(vars_files) > 0, "No vars_files defined in second play"
        assert any('secret.yml' in vf for vf in vars_files), \
            "secret.yml not referenced in vars_files"

    def test_task_validation(self, runner):
        """모든 태스크 구조 검증"""
        for play_idx in range(len(runner.playbook)):
            tasks = runner.get_tasks(play_idx)
            for task in tasks:
                errors = runner.validate_task_structure(task)
                assert not errors, \
                    f"Task validation errors: {', '.join(errors)}"

    def test_dry_run(self, playbook):
        """드라이런 테스트"""
        result = playbook.dry_run()

        assert 'plays' in result
        assert 'stats' in result
        assert result['stats']['failed'] == 0, \
            "Dry run should not have failures"

    def test_required_variables(self, playbook):
        """필수 변수 확인"""
        required_vars = playbook.get_required_vars()

        # root_password는 필수
        assert 'root_password' in required_vars, \
            "root_password should be a required variable"

    def test_idempotency_indicators(self, runner):
        """멱등성 보장 요소 확인"""
        tasks = runner.get_tasks(play_index=0)

        # 'creates' 인자를 가진 command 태스크 확인
        venv_task = next((t for t in tasks if 'Create a virtual environment' in t.get('name', '')), None)
        assert venv_task is not None
        assert 'args' in venv_task or 'creates' in str(venv_task), \
            "Virtual environment task should have 'creates' argument for idempotency"


class TestPrepareDisks:
    """prepare-disks.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/00-preparation/prepare-disks.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_playbook_structure(self, playbook):
        """플레이북 기본 구조 검증"""
        runner = playbook.runner

        # 플레이북이 로드되었는지 확인
        assert runner.playbook is not None
        assert len(runner.playbook) > 0

        # 첫 번째 플레이 검증
        first_play = runner.playbook[0]
        assert 'hosts' in first_play
        assert first_play.get('become', False) is True, \
            "Disk preparation should run with privilege"


class TestFixUbuntu24:
    """fix-ubuntu24.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/00-preparation/fix-ubuntu24.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_ubuntu_specific_tasks(self, playbook):
        """Ubuntu 24 특정 태스크 검증"""
        runner = playbook.runner
        tasks = runner.get_tasks(play_index=0)

        # Ubuntu 버전 확인 태스크가 있어야 함
        task_names = runner.get_task_names(play_index=0)

        # Ubuntu 24 관련 수정 사항이 포함되어야 함
        assert any('ubuntu' in name.lower() or '24' in name for name in task_names), \
            "Should have Ubuntu 24 specific tasks"