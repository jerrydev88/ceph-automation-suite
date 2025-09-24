#!/bin/bash

# Container-Compose 설치 스크립트
# https://github.com/Mcrich23/Container-Compose

set -e

echo "🍎 Container-Compose 설치 스크립트"
echo "===================================="
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# OS 확인
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ 이 스크립트는 macOS 전용입니다.${NC}"
    exit 1
fi

# Homebrew 확인
if ! command -v brew &> /dev/null; then
    echo -e "${YELLOW}⚠️  Homebrew가 설치되어 있지 않습니다.${NC}"
    echo "Homebrew를 설치하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" == "y" ]]; then
        echo "🍺 Homebrew 설치 중..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    else
        echo "Container-Compose 설치를 위해 Homebrew가 필요합니다."
        exit 1
    fi
fi

# Container-Compose 설치 확인
if command -v container-compose &> /dev/null; then
    echo -e "${GREEN}✅ Container-Compose가 이미 설치되어 있습니다.${NC}"
    echo "   버전: $(container-compose --version)"
    echo ""
    echo "업데이트하시겠습니까? (y/n)"
    read -r response
    if [[ "$response" != "y" ]]; then
        exit 0
    fi
fi

# Container-Compose 설치
echo "📦 Container-Compose 설치 중..."

# 옵션 1: Homebrew tap 사용 (권장)
echo "설치 방법을 선택하세요:"
echo "1) Homebrew (권장)"
echo "2) 직접 빌드"
echo "3) 바이너리 다운로드"
read -p "선택 [1-3]: " choice

case $choice in
    1)
        echo "🍺 Homebrew로 설치..."
        brew tap mcrich23/container-compose
        brew install container-compose
        ;;
    2)
        echo "🔨 소스에서 빌드..."
        # Swift가 필요함
        if ! command -v swift &> /dev/null; then
            echo -e "${RED}❌ Swift가 필요합니다. Xcode를 설치하세요.${NC}"
            exit 1
        fi

        # 임시 디렉토리에서 빌드
        TEMP_DIR=$(mktemp -d)
        cd "$TEMP_DIR"
        git clone https://github.com/Mcrich23/Container-Compose.git
        cd Container-Compose
        swift build -c release
        sudo cp .build/release/container-compose /usr/local/bin/
        cd -
        rm -rf "$TEMP_DIR"
        ;;
    3)
        echo "⬇️  바이너리 다운로드..."
        # GitHub Releases에서 최신 버전 다운로드
        LATEST_VERSION=$(curl -s https://api.github.com/repos/Mcrich23/Container-Compose/releases/latest | grep '"tag_name":' | sed -E 's/.*"([^"]+)".*/\1/')

        if [[ -z "$LATEST_VERSION" ]]; then
            echo -e "${RED}❌ 최신 버전을 찾을 수 없습니다.${NC}"
            exit 1
        fi

        echo "   최신 버전: $LATEST_VERSION"

        # 아키텍처 확인
        ARCH=$(uname -m)
        if [[ "$ARCH" == "arm64" ]]; then
            BINARY_NAME="container-compose-macos-arm64"
        else
            BINARY_NAME="container-compose-macos-x86_64"
        fi

        # 다운로드
        curl -L -o /tmp/container-compose \
            "https://github.com/Mcrich23/Container-Compose/releases/download/$LATEST_VERSION/$BINARY_NAME"

        chmod +x /tmp/container-compose
        sudo mv /tmp/container-compose /usr/local/bin/container-compose
        ;;
    *)
        echo -e "${RED}❌ 잘못된 선택입니다.${NC}"
        exit 1
        ;;
esac

# 설치 확인
if command -v container-compose &> /dev/null; then
    echo ""
    echo -e "${GREEN}✅ Container-Compose 설치 완료!${NC}"
    echo "   버전: $(container-compose --version)"
    echo ""
    echo "사용법:"
    echo "  container-compose up -d      # 서비스 시작"
    echo "  container-compose ps         # 상태 확인"
    echo "  container-compose logs       # 로그 보기"
    echo "  container-compose down       # 서비스 중지"
    echo ""
    echo "Ceph Automation Suite 실행:"
    echo "  container-compose run ceph-automation bash"
else
    echo -e "${RED}❌ 설치에 실패했습니다.${NC}"
    exit 1
fi

# 별칭 설정 제안
echo ""
echo "💡 팁: Docker Compose와 유사하게 사용하려면 별칭을 설정하세요:"
echo ""
echo "  echo 'alias docker-compose=\"container-compose\"' >> ~/.zshrc"
echo "  source ~/.zshrc"
echo ""