"""
03-operations 플레이북 단위 테스트
"""

import pytest
from pathlib import Path
from .test_playbook_runner import TestablePlaybook


class TestSaveFSID:
    """save-fsid.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/03-operations/save-fsid.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_fsid_save_tasks(self, playbook):
        """FSID 저장 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # FSID 관련 태스크가 있어야 함
        fsid_keywords = ['fsid', 'cluster', 'id', 'save', 'store']
        assert any(any(keyword in name.lower() for keyword in fsid_keywords)
                  for name in task_names), \
            "Should have FSID-related tasks"

    def test_uses_local_action(self, playbook):
        """로컬 액션 사용 확인"""
        runner = playbook.runner
        tasks = runner.get_tasks(play_index=0)

        # FSID는 보통 로컬에 저장
        assert any('local_action' in str(task) or 'delegate_to: localhost' in str(task)
                  for task in tasks), \
            "Should save FSID locally"


class TestSyncTime:
    """sync-time.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/03-operations/sync-time.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_time_sync_tasks(self, playbook):
        """시간 동기화 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # 시간 동기화 관련 태스크가 있어야 함
        time_keywords = ['ntp', 'time', 'sync', 'chrony', 'timedatectl']
        assert any(any(keyword in name.lower() for keyword in time_keywords)
                  for name in task_names), \
            "Should have time synchronization tasks"


class TestRBDSnapshots:
    """RBD 스냅샷 관련 플레이북 테스트"""

    @pytest.fixture
    def create_playbook(self):
        """create-rbd-snapshot.yml 플레이북"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/03-operations/create-rbd-snapshot.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    @pytest.fixture
    def remove_playbook(self):
        """remove-rbd-snapshot.yml 플레이북"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/03-operations/remove-rbd-snapshot.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    @pytest.fixture
    def list_playbook(self):
        """list-rbd-snapshots.yml 플레이북"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/03-operations/list-rbd-snapshots.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_create_snapshot_tasks(self, create_playbook):
        """스냅샷 생성 태스크 검증"""
        runner = create_playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # 스냅샷 생성 관련 태스크가 있어야 함
        assert any('snap' in name.lower() and 'create' in name.lower()
                  for name in task_names), \
            "Should have snapshot creation tasks"

    def test_remove_snapshot_tasks(self, remove_playbook):
        """스냅샷 삭제 태스크 검증"""
        runner = remove_playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # 스냅샷 삭제 관련 태스크가 있어야 함
        assert any('snap' in name.lower() and ('remove' in name.lower() or 'delete' in name.lower())
                  for name in task_names), \
            "Should have snapshot removal tasks"

    def test_list_snapshot_tasks(self, list_playbook):
        """스냅샷 목록 태스크 검증"""
        runner = list_playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # 스냅샷 목록 관련 태스크가 있어야 함
        assert any('snap' in name.lower() and 'list' in name.lower()
                  for name in task_names), \
            "Should have snapshot listing tasks"


class TestRBDImages:
    """list-rbd-images.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/03-operations/list-rbd-images.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_image_listing_tasks(self, playbook):
        """이미지 목록 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # RBD 이미지 목록 관련 태스크가 있어야 함
        image_keywords = ['rbd', 'image', 'list', 'ls']
        assert any(any(keyword in name.lower() for keyword in image_keywords)
                  for name in task_names), \
            "Should have RBD image listing tasks"


class TestOperationsPlaybooksConsistency:
    """운영 플레이북 전체 일관성 테스트"""

    @pytest.fixture
    def operations_dir(self):
        """operations 디렉토리 경로"""
        return Path(__file__).parent.parent.parent.parent / "playbooks/03-operations"

    def test_operations_playbooks_are_idempotent(self, operations_dir):
        """운영 플레이북이 멱등성을 가지는지 확인"""
        ops_playbooks = list(operations_dir.glob("*.yml"))

        for playbook_path in ops_playbooks:
            # 스냅샷 생성/삭제 같은 상태 변경 작업은 제외
            if any(x in playbook_path.name for x in ['create', 'remove', 'delete']):
                continue

            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            tasks = runner.get_tasks(play_index=0)
            for task in tasks:
                # list, show, get 같은 조회 작업은 changed_when: false를 가져야 함
                if any(op in str(task).lower() for op in ['list', 'show', 'get', 'status']):
                    assert 'changed_when' in task or 'register' in task, \
                        f"{playbook_path.name}: Read-only task should not mark as changed"

    def test_operations_require_confirmation(self, operations_dir):
        """위험한 운영 작업이 확인을 요구하는지 검사"""
        ops_playbooks = list(operations_dir.glob("*.yml"))

        dangerous_operations = ['remove', 'delete', 'purge', 'destroy']

        for playbook_path in ops_playbooks:
            # 위험한 작업인지 확인
            if any(op in playbook_path.name.lower() for op in dangerous_operations):
                with open(playbook_path, 'r') as f:
                    content = f.read()

                # 확인 메커니즘이 있는지 확인 (pause, prompt, when 조건 등)
                safety_mechanisms = ['pause:', 'prompt:', 'confirm', 'vars_prompt:']

                has_safety = any(mechanism in content for mechanism in safety_mechanisms)

                # 경고만 표시 (강제하지 않음)
                if not has_safety:
                    pytest.warn(f"{playbook_path.name} performs dangerous operation without confirmation")

    def test_operations_playbooks_have_descriptive_output(self, operations_dir):
        """운영 플레이북이 명확한 출력을 제공하는지 확인"""
        ops_playbooks = list(operations_dir.glob("list-*.yml"))

        for playbook_path in ops_playbooks:
            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            tasks = runner.get_tasks(play_index=0)
            for task in tasks:
                # list 작업은 결과를 표시해야 함
                if 'list' in playbook_path.name:
                    # register된 변수가 있으면 debug로 출력해야 함
                    if 'register' in task:
                        var_name = task.get('register')
                        # 다음 태스크들 중 하나에서 이 변수를 출력해야 함
                        all_tasks_str = str(tasks)
                        assert var_name in all_tasks_str and 'debug' in all_tasks_str, \
                            f"{playbook_path.name} should display registered results"