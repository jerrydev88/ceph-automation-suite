#!/bin/bash

# macOS 네이티브 container 플랫폼을 위한 빌드 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="ceph-automation-suite"
TAG="${TAG:-latest}"

echo "🍎 macOS Native Container Build"
echo "================================"
echo ""

# container CLI 확인
if ! command -v container &> /dev/null; then
    echo "❌ macOS container CLI를 찾을 수 없습니다."
    echo "   macOS Sequoia 15.0+ 또는 Xcode 16+가 필요합니다."
    exit 1
fi

echo "✓ Container CLI 버전:"
container --version

# 빌드 준비
cd "$PROJECT_ROOT"

# 이미지 빌드
echo ""
echo "🔨 이미지 빌드 중..."
container build \
    --tag "$IMAGE_NAME:$TAG" \
    --file Dockerfile \
    .

if [ $? -eq 0 ]; then
    echo "✅ 이미지 빌드 성공: $IMAGE_NAME:$TAG"
else
    echo "❌ 이미지 빌드 실패"
    exit 1
fi

# 이미지 확인
echo ""
echo "📦 빌드된 이미지:"
container images | grep "$IMAGE_NAME" || echo "이미지를 찾을 수 없습니다"

echo ""
echo "🚀 컨테이너 실행하기:"
echo "   container run -it $IMAGE_NAME:$TAG bash"
echo ""