"""
버전 관리 관련 단위 테스트
"""

import pytest
from pathlib import Path


class TestVersion:
    """버전 파일 및 관리 테스트"""

    def test_version_file_exists(self, version_file):
        """VERSION 파일 존재 확인"""
        assert version_file.exists(), "VERSION 파일이 존재해야 합니다"

    def test_version_format(self, version_file):
        """Semantic Versioning 형식 검증"""
        version = version_file.read_text().strip()

        # 버전이 비어있지 않은지 확인
        assert version, "VERSION 파일이 비어있습니다"

        # Semantic Versioning 형식 확인 (X.Y.Z)
        parts = version.split(".")
        assert len(parts) == 3, f"버전은 X.Y.Z 형식이어야 합니다. 현재: {version}"

        # 각 부분이 숫자인지 확인
        for i, part in enumerate(parts):
            assert part.isdigit(), f"버전의 {i + 1}번째 부분은 숫자여야 합니다: {part}"

    def test_version_consistency_pyproject(self, version_file, project_root):
        """pyproject.toml과 버전 일관성 확인"""
        version = version_file.read_text().strip()

        # pyproject.toml 파일 읽기
        pyproject_path = project_root / "pyproject.toml"
        assert pyproject_path.exists(), "pyproject.toml 파일이 존재해야 합니다"

        pyproject_content = pyproject_path.read_text()

        # 버전 확인
        expected_line = f'version = "{version}"'
        assert expected_line in pyproject_content, f"pyproject.toml에 올바른 버전이 설정되어야 합니다: {expected_line}"

    def test_version_consistency_dockerfile(self, version_file, project_root):
        """Dockerfile과 버전 일관성 확인"""
        version = version_file.read_text().strip()

        # Dockerfile 읽기
        dockerfile_path = project_root / "Dockerfile"
        assert dockerfile_path.exists(), "Dockerfile이 존재해야 합니다"

        dockerfile_content = dockerfile_path.read_text()

        # ARG VERSION 확인
        expected_arg = f"ARG VERSION={version}"
        assert expected_arg in dockerfile_content, (
            f"Dockerfile에 올바른 ARG VERSION이 설정되어야 합니다: {expected_arg}"
        )

    def test_version_consistency_readme(self, version_file, project_root):
        """README.md와 버전 일관성 확인"""
        version = version_file.read_text().strip()

        # README.md 읽기
        readme_path = project_root / "README.md"
        assert readme_path.exists(), "README.md가 존재해야 합니다"

        readme_content = readme_path.read_text()

        # 버전 확인
        expected_text = f"**버전**: {version}"
        assert expected_text in readme_content, f"README.md에 올바른 버전이 명시되어야 합니다: {expected_text}"


class TestVersionScripts:
    """버전 관리 스크립트 테스트"""

    def test_bump_version_script_exists(self, project_root):
        """bump-version.sh 스크립트 존재 확인"""
        script_path = project_root / "scripts" / "bump-version.sh"
        assert script_path.exists(), "bump-version.sh 스크립트가 존재해야 합니다"

    def test_bump_version_script_executable(self, project_root):
        """bump-version.sh 실행 권한 확인"""
        script_path = project_root / "scripts" / "bump-version.sh"
        assert script_path.exists()

        # 실행 권한 확인 (Unix-like systems)
        import os
        import stat

        st = os.stat(script_path)
        is_executable = bool(st.st_mode & stat.S_IXUSR)
        assert is_executable, "bump-version.sh는 실행 권한이 있어야 합니다"

    def test_update_version_script_exists(self, project_root):
        """update-version.sh 스크립트 존재 확인"""
        script_path = project_root / "scripts" / "update-version.sh"
        assert script_path.exists(), "update-version.sh 스크립트가 존재해야 합니다"

    def test_update_version_script_executable(self, project_root):
        """update-version.sh 실행 권한 확인"""
        script_path = project_root / "scripts" / "update-version.sh"
        assert script_path.exists()

        # 실행 권한 확인 (Unix-like systems)
        import os
        import stat

        st = os.stat(script_path)
        is_executable = bool(st.st_mode & stat.S_IXUSR)
        assert is_executable, "update-version.sh는 실행 권한이 있어야 합니다"
