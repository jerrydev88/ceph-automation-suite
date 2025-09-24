"""
01-deployment 플레이북 단위 테스트
"""

import pytest
from pathlib import Path
from .test_playbook_runner import TestablePlaybook


class TestBootstrap:
    """bootstrap.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/01-deployment/bootstrap.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_playbook_structure(self, playbook):
        """플레이북 기본 구조 검증"""
        runner = playbook.runner
        assert runner.playbook is not None
        assert len(runner.playbook) > 0

        first_play = runner.playbook[0]
        assert 'hosts' in first_play, "Bootstrap playbook should specify hosts"
        assert first_play.get('become', False) is True, \
            "Bootstrap should run with privilege"

    def test_bootstrap_tasks(self, playbook):
        """부트스트랩 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # 부트스트랩 관련 태스크가 있어야 함
        bootstrap_keywords = ['bootstrap', 'cephadm', 'init', 'cluster']
        assert any(any(keyword in name.lower() for keyword in bootstrap_keywords)
                  for name in task_names), \
            "Should have bootstrap-related tasks"


class TestCompleteDeployment:
    """complete-deployment.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/01-deployment/complete-deployment.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_includes_multiple_playbooks(self, playbook):
        """여러 플레이북을 포함하는지 확인"""
        runner = playbook.runner
        playbook_content = str(runner.playbook)

        # import_playbook을 사용하는지 확인
        assert 'import_playbook' in playbook_content or \
               'include' in playbook_content, \
               "Complete deployment should include/import other playbooks"

    def test_deployment_order(self, playbook):
        """배포 순서가 올바른지 확인"""
        runner = playbook.runner

        # complete-deployment는 여러 플레이북을 순서대로 import
        playbook_str = str(runner.playbook)

        # 준비 → 부트스트랩 → 설정 순서 확인
        if 'preparation' in playbook_str and 'bootstrap' in playbook_str:
            prep_idx = playbook_str.index('preparation')
            boot_idx = playbook_str.index('bootstrap')
            assert prep_idx < boot_idx, \
                "Preparation should come before bootstrap"


class TestDistributeSSHKey:
    """distribute-ssh-key.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/01-deployment/distribute-ssh-key.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_ssh_key_tasks(self, playbook):
        """SSH 키 배포 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # SSH 키 관련 태스크가 있어야 함
        ssh_keywords = ['ssh', 'key', 'authorized', 'public']
        assert any(any(keyword in name.lower() for keyword in ssh_keywords)
                  for name in task_names), \
            "Should have SSH key-related tasks"

    def test_uses_authorized_key_module(self, playbook):
        """authorized_key 모듈 사용 확인"""
        runner = playbook.runner
        tasks = runner.get_tasks(play_index=0)

        # authorized_key 또는 관련 모듈 사용 확인
        modules = ['authorized_key', 'ansible.posix.authorized_key',
                  'copy', 'ansible.builtin.copy']

        assert any(any(module in str(task) for module in modules)
                  for task in tasks), \
            "Should use appropriate modules for SSH key distribution"


class TestPostBootstrap:
    """post-bootstrap.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/01-deployment/post-bootstrap.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_post_bootstrap_tasks(self, playbook):
        """부트스트랩 후처리 태스크 검증"""
        runner = playbook.runner

        # post-bootstrap은 부트스트랩 이후 설정을 수행
        first_play = runner.playbook[0] if runner.playbook else {}

        # 일반적으로 모니터나 관리 노드에서 실행
        hosts = first_play.get('hosts', '')
        assert 'mon' in hosts or 'mgr' in hosts or 'all' in hosts, \
            "Post-bootstrap should target appropriate hosts"


class TestDeploymentPlaybooksConsistency:
    """배포 플레이북 전체 일관성 테스트"""

    @pytest.fixture
    def deployment_dir(self):
        """deployment 디렉토리 경로"""
        return Path(__file__).parent.parent.parent.parent / "playbooks/01-deployment"

    def test_all_deployment_playbooks_have_consistent_structure(self, deployment_dir):
        """모든 배포 플레이북이 일관된 구조를 가지는지 확인"""
        deployment_playbooks = list(deployment_dir.glob("*.yml"))

        for playbook_path in deployment_playbooks:
            # complete-deployment 같은 메타 플레이북은 제외
            if 'complete' in playbook_path.name:
                continue

            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            # 배포 플레이북은 적절한 권한을 가져야 함
            for play in runner.playbook:
                if isinstance(play, dict) and 'hosts' in play:
                    # 배포 작업은 보통 권한이 필요
                    if 'distribute-ssh' not in playbook_path.name:
                        assert play.get('become', False) is True, \
                            f"{playbook_path.name} should run with privilege"

    def test_no_test_data_in_deployment(self, deployment_dir):
        """배포 플레이북에 테스트 데이터가 없는지 확인"""
        deployment_playbooks = list(deployment_dir.glob("*.yml"))

        for playbook_path in deployment_playbooks:
            with open(playbook_path, 'r') as f:
                content = f.read()

            # 테스트용 데이터나 더미 값 확인
            test_indicators = ['test', 'dummy', 'example', 'localhost']

            # 주석이 아닌 라인에서 테스트 데이터 확인
            lines = content.split('\n')
            for line in lines:
                if line.strip().startswith('#'):
                    continue

                # localhost는 특수한 경우 허용
                if 'localhost' in line.lower() and 'ansible_connection' not in line:
                    if 'delegate_to' not in line:
                        pytest.warn(f"{playbook_path.name} may contain test data: {line.strip()}")

    def test_deployment_playbooks_have_descriptive_names(self, deployment_dir):
        """배포 플레이북이 설명적인 이름을 가지는지 확인"""
        deployment_playbooks = list(deployment_dir.glob("*.yml"))

        for playbook_path in deployment_playbooks:
            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            for play_idx, play in enumerate(runner.playbook):
                if isinstance(play, dict):
                    # import_playbook이 아닌 일반 플레이는 name을 가져야 함
                    if 'import_playbook' not in play:
                        assert 'name' in play, \
                            f"{playbook_path.name}[{play_idx}] should have a descriptive name"

                        # 이름이 너무 짧거나 일반적이지 않은지 확인
                        if 'name' in play:
                            name = play['name']
                            assert len(name) > 5, \
                                f"{playbook_path.name}[{play_idx}] name too short: '{name}'"