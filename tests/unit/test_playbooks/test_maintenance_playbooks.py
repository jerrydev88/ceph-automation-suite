"""
90-maintenance 플레이북 단위 테스트
"""

import pytest
from pathlib import Path
from .test_playbook_runner import TestablePlaybook


class TestPurgeCluster:
    """purge-cluster.yml 플레이북 테스트"""

    @pytest.fixture
    def playbook(self):
        """테스트할 플레이북 인스턴스"""
        playbook_path = Path(__file__).parent.parent.parent.parent / \
            "playbooks/90-maintenance/purge-cluster.yml"
        if not playbook_path.exists():
            pytest.skip(f"Playbook not found: {playbook_path}")
        return TestablePlaybook(playbook_path)

    def test_has_safety_checks(self, playbook):
        """안전 확인 메커니즘이 있는지 검증"""
        runner = playbook.runner

        # purge는 매우 위험한 작업이므로 확인이 필요
        playbook_str = str(runner.playbook)

        # 확인 메커니즘 확인
        safety_keywords = ['confirm', 'prompt', 'pause', 'vars_prompt', 'really', 'sure']
        assert any(keyword in playbook_str.lower() for keyword in safety_keywords), \
            "Purge operation must have safety confirmation"

    def test_targets_all_nodes(self, playbook):
        """모든 노드를 대상으로 하는지 확인"""
        runner = playbook.runner

        if runner.playbook:
            # purge는 일반적으로 모든 노드를 대상으로 함
            hosts_in_plays = [play.get('hosts', '') for play in runner.playbook
                            if isinstance(play, dict)]

            assert any('all' in hosts for hosts in hosts_in_plays), \
                "Purge should target all nodes"

    def test_has_destructive_operations(self, playbook):
        """파괴적인 작업이 포함되어 있는지 확인"""
        runner = playbook.runner
        task_names = runner.get_task_names(play_index=0)

        # purge 관련 태스크가 있어야 함
        destructive_keywords = ['purge', 'remove', 'delete', 'clean', 'destroy', 'zap']
        assert any(any(keyword in name.lower() for keyword in destructive_keywords)
                  for name in task_names), \
            "Purge playbook should have destructive operations"


class TestUndoConfigure:
    """undo-configure 플레이북들 테스트"""

    @pytest.fixture
    def undo_playbooks(self):
        """undo-configure 플레이북들"""
        playbook_dir = Path(__file__).parent.parent.parent.parent / \
            "playbooks/90-maintenance"
        return list(playbook_dir.glob("undo-configure-*.yml"))

    def test_undo_playbooks_exist(self, undo_playbooks):
        """undo 플레이북이 존재하는지 확인"""
        assert len(undo_playbooks) > 0, \
            "Should have undo-configure playbooks"

        # 주요 서비스별 undo 플레이북 확인
        expected_undos = ['rbd', 'cephfs', 'rgw', 'osd']
        undo_names = [p.stem for p in undo_playbooks]

        for service in expected_undos:
            assert any(service in name for name in undo_names), \
                f"Should have undo-configure-{service}.yml"

    def test_undo_operations_are_reversible(self, undo_playbooks):
        """undo 작업이 되돌릴 수 있는지 확인"""
        for playbook_path in undo_playbooks:
            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            # undo는 설정을 되돌리는 작업
            task_names = runner.get_task_names(play_index=0)

            # 제거/삭제 작업이 있어야 함
            undo_keywords = ['remove', 'delete', 'disable', 'stop', 'unset']
            assert any(any(keyword in name.lower() for keyword in undo_keywords)
                      for name in task_names), \
                f"{playbook_path.name} should have undo operations"

    def test_undo_playbooks_have_warnings(self, undo_playbooks):
        """undo 플레이북이 경고를 포함하는지 확인"""
        for playbook_path in undo_playbooks:
            with open(playbook_path, 'r') as f:
                content = f.read()

            # 경고나 주의사항이 있어야 함 (주석이나 태스크 이름에)
            warning_keywords = ['warning', 'caution', 'careful', 'note', '주의', 'will remove', 'will delete']

            has_warning = any(keyword in content.lower() for keyword in warning_keywords)

            if not has_warning:
                pytest.warn(f"{playbook_path.name} should include warnings about undo operations")


class TestMaintenancePlaybooksConsistency:
    """유지보수 플레이북 전체 일관성 테스트"""

    @pytest.fixture
    def maintenance_dir(self):
        """maintenance 디렉토리 경로"""
        return Path(__file__).parent.parent.parent.parent / "playbooks/90-maintenance"

    def test_all_maintenance_playbooks_require_privilege(self, maintenance_dir):
        """모든 유지보수 플레이북이 권한을 요구하는지 확인"""
        maintenance_playbooks = list(maintenance_dir.glob("*.yml"))

        for playbook_path in maintenance_playbooks:
            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            # 유지보수 작업은 권한이 필요
            for play in runner.playbook:
                if isinstance(play, dict) and 'hosts' in play:
                    assert play.get('become', False) is True, \
                        f"{playbook_path.name} should run with privilege"

    def test_maintenance_playbooks_have_clear_names(self, maintenance_dir):
        """유지보수 플레이북이 명확한 이름을 가지는지 확인"""
        maintenance_playbooks = list(maintenance_dir.glob("*.yml"))

        for playbook_path in maintenance_playbooks:
            playbook = TestablePlaybook(playbook_path)
            runner = playbook.runner

            if not runner.playbook:
                continue

            for play in runner.playbook:
                if isinstance(play, dict) and 'hosts' in play:
                    assert 'name' in play, \
                        f"{playbook_path.name} should have descriptive play names"

                    # 이름이 작업을 명확히 설명하는지 확인
                    if 'name' in play:
                        name = play['name']
                        # 유지보수 작업은 특히 명확해야 함
                        action_keywords = ['undo', 'remove', 'purge', 'clean', 'maintenance', 'restore']
                        assert any(keyword in name.lower() for keyword in action_keywords), \
                            f"{playbook_path.name}: Play name should clearly indicate maintenance action"

    def test_no_maintenance_playbooks_in_production_without_guard(self, maintenance_dir):
        """유지보수 플레이북이 프로덕션 가드를 가지는지 확인"""
        maintenance_playbooks = list(maintenance_dir.glob("*.yml"))

        for playbook_path in maintenance_playbooks:
            # purge나 undo 같은 위험한 작업
            if any(x in playbook_path.name for x in ['purge', 'undo', 'remove', 'delete']):
                with open(playbook_path, 'r') as f:
                    content = f.read()

                # 프로덕션 환경 체크가 있는지 확인
                production_guards = [
                    'environment',
                    'production',
                    'confirm',
                    'i_really_really_mean_it',
                    'force',
                    'vars_prompt'
                ]

                has_guard = any(guard in content.lower() for guard in production_guards)

                if not has_guard:
                    pytest.warn(f"{playbook_path.name} should have production environment guards")

    def test_maintenance_playbooks_document_impact(self, maintenance_dir):
        """유지보수 플레이북이 영향도를 문서화하는지 확인"""
        maintenance_playbooks = list(maintenance_dir.glob("*.yml"))

        for playbook_path in maintenance_playbooks:
            with open(playbook_path, 'r') as f:
                lines = f.readlines()

            # 파일 시작 부분에 주석으로 영향도 설명이 있는지 확인
            first_10_lines = ''.join(lines[:10])

            # 영향도 설명 키워드
            impact_keywords = ['impact', 'warning', 'caution', 'note', 'description', 'purpose', '주의']

            has_documentation = any(keyword in first_10_lines.lower() for keyword in impact_keywords)

            if not has_documentation:
                pytest.warn(f"{playbook_path.name} should document its impact in header comments")