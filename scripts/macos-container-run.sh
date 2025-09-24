#!/bin/bash

# macOS 네이티브 container 플랫폼으로 Ceph Automation Suite 실행

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
IMAGE_NAME="ceph-automation-suite"
TAG="${TAG:-latest}"
CONTAINER_NAME="${CONTAINER_NAME:-ceph-auto}"

# 명령어 파싱
COMMAND="${1:-bash}"
shift || true

echo "🍎 macOS Native Container Runtime"
echo "=================================="
echo ""

# container CLI 확인
if ! command -v container &> /dev/null; then
    echo "❌ macOS container CLI를 찾을 수 없습니다."
    exit 1
fi

# 볼륨 생성 (필요시)
echo "📁 볼륨 준비..."
container volume create ansible-facts 2>/dev/null || true
container volume create ansible-logs 2>/dev/null || true

# 네트워크 생성 (필요시)
echo "🌐 네트워크 준비..."
container network create ceph-net 2>/dev/null || true

# SSH 키 경로 확인
SSH_KEY_PATH="$HOME/.ssh"
if [ ! -d "$SSH_KEY_PATH" ]; then
    echo "⚠️  SSH 키 디렉토리를 찾을 수 없습니다: $SSH_KEY_PATH"
    echo "   SSH 키 없이 계속합니다..."
    SSH_MOUNT=""
else
    SSH_MOUNT="-v $SSH_KEY_PATH:/home/ansible/.ssh:ro"
fi

# 인벤토리 파일 확인
INVENTORY_PATH="$PROJECT_ROOT/inventory"
if [ ! -d "$INVENTORY_PATH" ]; then
    echo "📝 인벤토리 디렉토리 생성..."
    mkdir -p "$INVENTORY_PATH"

    if [ -f "$PROJECT_ROOT/inventory/hosts-scalable.yml.example" ]; then
        cp "$PROJECT_ROOT/inventory/hosts-scalable.yml.example" "$INVENTORY_PATH/hosts-scalable.yml"
        echo "   예제 인벤토리 파일을 복사했습니다."
    fi
fi

# 컨테이너 실행
echo ""
echo "🚀 컨테이너 시작..."

# 기존 컨테이너 확인 및 제거
container list --all | grep "$CONTAINER_NAME" > /dev/null 2>&1 && {
    echo "   기존 컨테이너 제거 중..."
    container stop "$CONTAINER_NAME" 2>/dev/null || true
    container rm "$CONTAINER_NAME" 2>/dev/null || true
}

# 새 컨테이너 실행
container run \
    --name "$CONTAINER_NAME" \
    --hostname "$CONTAINER_NAME" \
    --interactive \
    --tty \
    --rm \
    --network ceph-net \
    -v "$INVENTORY_PATH:/opt/ceph-automation/inventory:rw" \
    $SSH_MOUNT \
    -v ansible-facts:/tmp/ansible-facts \
    -v ansible-logs:/var/log/ansible \
    -w /opt/ceph-automation \
    -e ANSIBLE_HOST_KEY_CHECKING=False \
    -e ANSIBLE_GATHERING=smart \
    -e ANSIBLE_FACT_CACHING=jsonfile \
    -e ANSIBLE_FACT_CACHING_CONNECTION=/tmp/ansible-facts \
    -e ANSIBLE_STDOUT_CALLBACK=yaml \
    "$IMAGE_NAME:$TAG" \
    $COMMAND "$@"

echo ""
echo "✅ 컨테이너 종료됨"