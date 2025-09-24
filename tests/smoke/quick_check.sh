#!/bin/bash

# Smoke Test - 핵심 기능 빠른 검증
# 실행 시간: < 30초

echo "💨 Smoke Test 시작"
echo "=================="

# 색상 정의 (터미널 호환성 개선)
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    NC='\033[0m'
else
    GREEN=''
    RED=''
    NC=''
fi

# 테스트 카운터
PASSED=0
FAILED=0

# 빠른 테스트 함수
quick_test() {
    local test_name="$1"
    local test_command="$2"

    if eval "$test_command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $test_name"
        ((PASSED++))
    else
        echo -e "${RED}✗${NC} $test_name"
        ((FAILED++))
    fi
}

# 1. 필수 파일 존재 확인
echo "📁 필수 파일 확인..."
quick_test "VERSION 파일" "test -f VERSION"
quick_test "Dockerfile" "test -f Dockerfile"
quick_test "Makefile" "test -f Makefile"
quick_test "pyproject.toml" "test -f pyproject.toml"
quick_test "ansible.cfg" "test -f ansible.cfg"

# 2. 필수 디렉토리 확인
echo ""
echo "📂 필수 디렉토리 확인..."
quick_test "playbooks/" "test -d playbooks"
quick_test "scripts/" "test -d scripts"
quick_test "inventory/" "test -d inventory"
quick_test "group_vars/" "test -d group_vars"

# 3. 스크립트 실행 권한
echo ""
echo "🔧 스크립트 권한 확인..."
quick_test "bump-version.sh 실행권한" "test -x scripts/bump-version.sh"
quick_test "update-version.sh 실행권한" "test -x scripts/update-version.sh"
quick_test "docker-entrypoint.sh 실행권한" "test -x docker-entrypoint.sh"

# 4. Makefile 기본 타겟
echo ""
echo "🎯 Makefile 타겟 확인..."
quick_test "make help" "make help > /dev/null 2>&1"
quick_test "make version" "make -B version > /dev/null 2>&1"

# 5. 버전 일관성
echo ""
echo "🔢 버전 일관성 확인..."
VERSION=$(cat VERSION)
quick_test "버전 형식 (X.Y.Z)" "echo $VERSION | grep -E '^[0-9]+\.[0-9]+\.[0-9]+$'"

# 결과 출력
echo ""
echo "=================="
echo "결과: ${GREEN}$PASSED 통과${NC} / ${RED}$FAILED 실패${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Smoke Test 통과!${NC}"
    exit 0
else
    echo -e "${RED}❌ Smoke Test 실패${NC}"
    exit 1
fi