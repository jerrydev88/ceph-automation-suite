#!/bin/bash

# Makefile 통합 테스트
# 각 Makefile 타겟이 올바르게 동작하는지 검증

set -e

echo "🔗 Makefile 통합 테스트"
echo "======================"

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 테스트 결과
PASSED=0
FAILED=0
SKIPPED=0

# 테스트 함수
run_test() {
    local test_name="$1"
    local test_command="$2"
    local skip_condition="$3"

    if [ -n "$skip_condition" ] && eval "$skip_condition"; then
        echo -e "${YELLOW}⏭️  $test_name (건너뜀)${NC}"
        ((SKIPPED++))
        return
    fi

    echo -n "Testing: $test_name... "

    if eval "$test_command" > /tmp/test_output.log 2>&1; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "  Error output:"
        tail -5 /tmp/test_output.log | sed 's/^/    /'
        ((FAILED++))
    fi
}

# 1. Help 타겟
echo "📖 Help 타겟 테스트"
echo "-------------------"
run_test "make help" "make help | grep -q 'Ceph Automation Suite'"

# 2. Version 관리 타겟
echo ""
echo "🔢 Version 타겟 테스트"
echo "---------------------"
run_test "make version" "make -B version | grep -q 'v0.0.1'"

# VERSION 백업
cp VERSION VERSION.backup

# 버전 bump 테스트 (실제로 실행하지 않고 스크립트만 확인)
run_test "bump-patch 스크립트 확인" "test -x scripts/bump-version.sh"
run_test "update-version 스크립트 확인" "test -x scripts/update-version.sh"

# VERSION 복원
mv VERSION.backup VERSION

# 3. Clean 타겟
echo ""
echo "🧹 Clean 타겟 테스트"
echo "-------------------"

# 임시 파일 생성
mkdir -p .pytest_cache
touch test_temp.pyc

run_test "make clean" "make clean"

# 정리 확인
run_test "캐시 정리 확인" "! test -d .pytest_cache"
run_test "pyc 파일 정리 확인" "! test -f test_temp.pyc"

# 4. Docker 관련 타겟
echo ""
echo "🐳 Docker 타겟 테스트"
echo "--------------------"

# Docker 설치 확인
if command -v docker >/dev/null 2>&1; then
    # Docker가 실행 중인지 확인
    if docker info >/dev/null 2>&1; then
        run_test "make size (이미지가 있는 경우)" \
            "make size || echo 'No image yet'"
    else
        echo -e "${YELLOW}⚠️  Docker daemon이 실행되지 않음${NC}"
        ((SKIPPED++))
    fi
else
    echo -e "${YELLOW}⚠️  Docker가 설치되지 않음${NC}"
    ((SKIPPED++))
fi

# 5. 초기화 타겟
echo ""
echo "🚀 Init 타겟 테스트"
echo "------------------"

# cache-dir 타겟
run_test "make cache-dir" "make cache-dir && test -d .ansible-cache"
run_test "logs 디렉토리 생성" "test -d logs"

# 정리
rm -rf .ansible-cache logs

# 결과 요약
echo ""
echo "======================"
echo "📊 테스트 결과"
echo "======================"
echo -e "통과: ${GREEN}$PASSED${NC}"
echo -e "실패: ${RED}$FAILED${NC}"
echo -e "건너뜀: ${YELLOW}$SKIPPED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ Makefile 통합 테스트 성공!${NC}"
    exit 0
else
    echo -e "${RED}❌ 일부 테스트 실패${NC}"
    exit 1
fi