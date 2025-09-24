"""
pytest 설정 및 공통 fixtures
"""

import pytest
import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def project_root():
    """프로젝트 루트 디렉토리 반환"""
    return Path(__file__).parent.parent


@pytest.fixture
def version_file(project_root):
    """VERSION 파일 경로 반환"""
    return project_root / "VERSION"


@pytest.fixture
def test_data_dir():
    """테스트 데이터 디렉토리 반환"""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def mock_inventory(test_data_dir, tmp_path):
    """임시 테스트 인벤토리 생성"""
    inventory_content = """
all:
  children:
    mons:
      hosts:
        test-mon1:
          ansible_host: 10.0.0.1
    osds:
      hosts:
        test-osd1:
          ansible_host: 10.0.0.2
    """
    inventory_file = tmp_path / "test_inventory.yml"
    inventory_file.write_text(inventory_content)
    return inventory_file


@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    """테스트 실행 시 프로젝트 루트로 디렉토리 변경"""
    monkeypatch.chdir(request.config.rootdir)


@pytest.fixture
def clean_environment():
    """테스트 환경 초기화"""
    # 환경 변수 백업
    original_env = os.environ.copy()

    yield

    # 환경 변수 복원
    os.environ.clear()
    os.environ.update(original_env)
