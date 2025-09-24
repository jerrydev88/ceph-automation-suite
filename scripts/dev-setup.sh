#!/bin/bash

# Ceph Automation Suite 개발 환경 설정 스크립트

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "🚀 Ceph Automation Suite 개발 환경 설정"
echo "========================================"

# 1. UV 설치 확인
echo ""
echo "📦 UV 패키지 매니저 확인..."
if command -v uv >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} UV가 이미 설치되어 있습니다 ($(uv --version))"
else
    echo -e "${YELLOW}⚠${NC} UV가 설치되지 않았습니다. 설치를 시작합니다..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
    echo -e "${GREEN}✓${NC} UV 설치 완료"
fi

# 2. Python 버전 확인
echo ""
echo "🐍 Python 버전 확인..."
REQUIRED_PYTHON="3.11"
if python3 --version | grep -q "3.11"; then
    echo -e "${GREEN}✓${NC} Python 3.11이 설치되어 있습니다"
else
    echo -e "${YELLOW}⚠${NC} Python 3.11이 권장됩니다. 현재: $(python3 --version)"
fi

# 3. 가상환경 생성
echo ""
echo "🔮 Python 가상환경 생성..."
if [ -d ".venv" ]; then
    echo -e "${YELLOW}⚠${NC} 기존 가상환경이 있습니다. 삭제하고 재생성하시겠습니까? (y/N)"
    read -r response
    if [[ "$response" =~ ^[Yy]$ ]]; then
        rm -rf .venv
        uv venv .venv --python 3.11
        echo -e "${GREEN}✓${NC} 가상환경 재생성 완료"
    else
        echo -e "${YELLOW}⚠${NC} 기존 가상환경 유지"
    fi
else
    uv venv .venv --python 3.11
    echo -e "${GREEN}✓${NC} 가상환경 생성 완료"
fi

# 4. 가상환경 활성화
echo ""
echo "🔌 가상환경 활성화..."
source .venv/bin/activate
echo -e "${GREEN}✓${NC} 가상환경 활성화됨"

# 5. 의존성 설치
echo ""
echo "📚 의존성 설치..."

echo "  → 기본 의존성 설치 중..."
uv pip install -e . -q
echo -e "  ${GREEN}✓${NC} 기본 의존성 설치 완료"

echo "  → 개발 의존성 설치 중..."
uv pip install -e ".[dev]" -q
echo -e "  ${GREEN}✓${NC} 개발 의존성 설치 완료"

echo "  → 테스트 의존성 설치 중..."
uv pip install -e ".[test]" -q
echo -e "  ${GREEN}✓${NC} 테스트 의존성 설치 완료"

# 6. Pre-commit hooks 설정
echo ""
echo "🪝 Git hooks 설정..."
if [ -d ".git" ]; then
    if command -v pre-commit >/dev/null 2>&1; then
        pre-commit install
        echo -e "${GREEN}✓${NC} Pre-commit hooks 설치 완료"
    else
        uv pip install pre-commit -q
        pre-commit install
        echo -e "${GREEN}✓${NC} Pre-commit 설치 및 hooks 설정 완료"
    fi
else
    echo -e "${YELLOW}⚠${NC} Git 저장소가 아닙니다. Pre-commit 설정 건너뜀"
fi

# 7. 디렉토리 생성
echo ""
echo "📁 필요한 디렉토리 생성..."
mkdir -p logs .ansible-cache
echo -e "${GREEN}✓${NC} 디렉토리 생성 완료"

# 8. 설정 파일 확인
echo ""
echo "⚙️  설정 파일 확인..."

if [ -f ".editorconfig" ]; then
    echo -e "  ${GREEN}✓${NC} .editorconfig"
else
    echo -e "  ${YELLOW}⚠${NC} .editorconfig 없음"
fi

if [ -f ".pre-commit-config.yaml" ]; then
    echo -e "  ${GREEN}✓${NC} .pre-commit-config.yaml"
else
    echo -e "  ${YELLOW}⚠${NC} .pre-commit-config.yaml 없음"
fi

if [ -d ".vscode" ]; then
    echo -e "  ${GREEN}✓${NC} .vscode 설정"
else
    echo -e "  ${YELLOW}⚠${NC} .vscode 설정 없음"
fi

# 9. 테스트 실행
echo ""
echo "🧪 테스트 환경 검증..."
if ./tests/smoke/quick_check.sh >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} 스모크 테스트 통과"
else
    echo -e "${YELLOW}⚠${NC} 스모크 테스트 실패 (정상일 수 있음)"
fi

# 10. 완료 메시지
echo ""
echo "========================================"
echo -e "${GREEN}✅ 개발 환경 설정 완료!${NC}"
echo ""
echo "다음 명령어로 시작하세요:"
echo ""
echo "  # 가상환경 활성화 (새 터미널에서)"
echo "  ${GREEN}source .venv/bin/activate${NC}"
echo ""
echo "  # 테스트 실행"
echo "  ${GREEN}make test${NC}"
echo ""
echo "  # 코드 포매팅"
echo "  ${GREEN}make format${NC}"
echo ""
echo "  # 린팅"
echo "  ${GREEN}make lint${NC}"
echo ""
echo "  # Docker 이미지 빌드"
echo "  ${GREEN}make build${NC}"
echo ""
echo "자세한 사용법은 CONTRIBUTING.md를 참고하세요."
echo "========================================"