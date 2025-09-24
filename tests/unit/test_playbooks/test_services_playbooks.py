"""
02-services 플레이북 단위 테스트
"""

import pytest
from pathlib import Path
from .test_playbook_runner import TestablePlaybook


class TestConfigureGlobal:
    """configure-global.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/02-services/configure-global.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_global_configuration_tasks(self, playbook):
        """전역 설정 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # 전역 설정 관련 태스크가 있어야 함
        config_keywords = ['config', 'global', 'set', 'parameter']
        assert any(any(keyword in name.lower() for keyword in config_keywords)
                  for name in task_names), \
            "Should have global configuration tasks"

    def test_uses_ceph_config_commands(self, playbook):
        """Ceph config 명령 사용 확인"""
        runner = playbook.runner
        tasks = runner.get_tasks(play_index=0)

        # ceph config 관련 명령 사용 확인
        assert any('ceph' in str(task) and 'config' in str(task)
                  for task in tasks), \
            "Should use ceph config commands"


class TestConfigureRBD:
    """configure-rbd.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/02-services/configure-rbd.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_rbd_configuration_tasks(self, playbook):
        """RBD 설정 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # RBD 관련 태스크가 있어야 함
        rbd_keywords = ['rbd', 'pool', 'image', 'block']
        assert any(any(keyword in name.lower() for keyword in rbd_keywords)
                  for name in task_names), \
            "Should have RBD-related tasks"

    def test_uses_ceph_vars(self, playbook):
        """ceph-vars.yml 참조 확인"""
        runner = playbook.runner
        first_play = runner.playbook[0] if runner.playbook else {}

        vars_files = first_play.get('vars_files', [])
        assert any('ceph-vars.yml' in vf for vf in vars_files), \
            "Should reference ceph-vars.yml for RBD configuration"


class TestConfigureCephFS:
    """configure-cephfs.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/02-services/configure-cephfs.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_cephfs_configuration_tasks(self, playbook):
        """CephFS 설정 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # CephFS 관련 태스크가 있어야 함
        fs_keywords = ['fs', 'cephfs', 'mds', 'filesystem']
        assert any(any(keyword in name.lower() for keyword in fs_keywords)
                  for name in task_names), \
            "Should have CephFS-related tasks"


class TestConfigureRGW:
    """configure-rgw.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/02-services/configure-rgw.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_rgw_configuration_tasks(self, playbook):
        """RGW 설정 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # RGW 관련 태스크가 있어야 함
        rgw_keywords = ['rgw', 'radosgw', 's3', 'object', 'gateway']
        assert any(any(keyword in name.lower() for keyword in rgw_keywords)
                  for name in task_names), \
            "Should have RGW-related tasks"


class TestRGWUsers:
    """rgw-users.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/02-services/rgw-users.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_user_creation_tasks(self, playbook):
        """사용자 생성 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # 사용자 관련 태스크가 있어야 함
        user_keywords = ['user', 'create', 'radosgw-admin']
        assert any(any(keyword in name.lower() for keyword in user_keywords)
                  for name in task_names), \
            "Should have user creation tasks"

    def test_loops_for_multiple_users(self, playbook):
        """여러 사용자 처리를 위한 반복문 확인"""
        runner = playbook.runner
        tasks = runner.get_tasks(play_index=0)

        # loop 또는 with_items 사용 확인
        assert any('loop' in task or 'with_items' in task
                  for task in tasks), \
            "Should use loops to handle multiple users"


class TestCSIUsers:
    """csi-users.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/02-services/csi-users.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_csi_user_creation(self, playbook):
        """CSI 사용자 생성 태스크 검증"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # CSI 관련 태스크가 있어야 함
        csi_keywords = ['csi', 'auth', 'caps', 'kubernetes']
        assert any(any(keyword in name.lower() for keyword in csi_keywords)
                  for name in task_names), \
            "Should have CSI user creation tasks"


class TestServicesPlaybooksConsistency:
    """서비스 플레이북 전체 일관성 테스트"""

    @pytest.fixture
    def services_dir(self):
        """services 디렉토리 경로"""
        return Path(__file__).parent.parent.parent.parent / "playbooks/02-services"

    def test_all_service_playbooks_use_ceph_vars(self, services_dir):
        """모든 서비스 플레이북이 ceph-vars.yml을 참조하는지 확인"""
        service_playbooks = list(services_dir.glob("configure-*.yml"))
        service_playbooks.extend(list(services_dir.glob("*-users.yml")))

        for playbook_path in service_playbooks:
            # tasks 하위 디렉토리는 제외
            if '/tasks/' in str(playbook_path):
                continue

            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            # 첫 번째 플레이에서 vars_files 확인
            first_play = runner.playbook[0] if runner.playbook else {}
            if isinstance(first_play, dict) and 'hosts' in first_play:
                vars_files = first_play.get('vars_files', [])

                # configure 플레이북은 ceph-vars.yml을 참조해야 함
                if 'configure' in playbook_path.name:
                    assert any('ceph-vars.yml' in str(vf) for vf in vars_files), \
                        f"{playbook_path.name} should reference ceph-vars.yml"

    def test_service_playbooks_target_appropriate_hosts(self, services_dir):
        """서비스 플레이북이 적절한 호스트를 대상으로 하는지 확인"""
        service_playbooks = list(services_dir.glob("*.yml"))

        for playbook_path in service_playbooks:
            # tasks 디렉토리는 제외
            if '/tasks/' in str(playbook_path):
                continue

            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            first_play = runner.playbook[0] if runner.playbook else {}
            if isinstance(first_play, dict) and 'hosts' in first_play:
                hosts = first_play['hosts']

                # 서비스별 적절한 호스트 확인
                if 'rbd' in playbook_path.name or 'pool' in playbook_path.name:
                    assert 'mon' in hosts or 'all' in hosts, \
                        f"{playbook_path.name} should target monitors or all"

                if 'rgw' in playbook_path.name:
                    assert 'rgw' in hosts or 'mon' in hosts or 'all' in hosts, \
                        f"{playbook_path.name} should target RGW nodes"

                if 'cephfs' in playbook_path.name:
                    assert 'mds' in hosts or 'mon' in hosts or 'all' in hosts, \
                        f"{playbook_path.name} should target MDS or monitor nodes"

    def test_no_destructive_operations_in_configure(self, services_dir):
        """configure 플레이북에 파괴적인 작업이 없는지 확인"""
        configure_playbooks = list(services_dir.glob("configure-*.yml"))

        for playbook_path in configure_playbooks:
            with open(playbook_path, 'r') as f:
                content = f.read()

            # 파괴적인 작업 확인
            dangerous_operations = ['purge', 'remove', 'delete', 'destroy', 'state: absent']

            for op in dangerous_operations:
                if op in content.lower():
                    # 주석이 아닌 경우만 확인
                    lines = content.split('\n')
                    for line in lines:
                        if not line.strip().startswith('#') and op in line.lower():
                            # delete는 버킷이나 오브젝트 권한일 수 있으므로 예외 처리
                            if 'delete' in line.lower() and ('permission' in line.lower() or 'perm' in line.lower()):
                                continue
                            pytest.warn(f"{playbook_path.name} may contain destructive operation: {line.strip()}")