#!/bin/bash

# 전체 테스트 스위트 실행 스크립트
# 모든 테스트를 순차적으로 실행하고 결과를 요약합니다

set +e  # 개별 테스트 실패시에도 계속 진행

echo "🚀 Ceph Automation Suite 전체 테스트 시작"
echo "=========================================="
echo ""

# 색상 정의
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    BLUE=''
    NC=''
fi

# 테스트 결과 저장
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# 프로젝트 루트로 이동
cd "$(dirname "$0")/.." || exit 1

# 테스트 실행 함수
run_test() {
    local test_name="$1"
    local test_command="$2"

    echo -e "${BLUE}▶ $test_name${NC}"
    echo "----------------------------------------"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    if eval "$test_command" > /tmp/test_output.txt 2>&1; then
        echo -e "${GREEN}✅ $test_name 통과${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))

        # pytest 출력에서 통계 추출
        if grep -q "passed" /tmp/test_output.txt; then
            stats=$(grep -E "[0-9]+ passed" /tmp/test_output.txt | tail -1)
            echo "   $stats"
        fi
    else
        echo -e "${RED}❌ $test_name 실패${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))

        # 실패 원인 출력
        echo "   실패 내용:"
        tail -10 /tmp/test_output.txt | sed 's/^/   /'
    fi

    echo ""
}

# 1. 스모크 테스트
run_test "스모크 테스트" "make test-smoke"

# 2. 버전 관리 테스트
run_test "버전 관리 테스트" ".venv/bin/pytest tests/unit/test_version.py -q"

# 3. Ansible 플레이북 문법 테스트
run_test "플레이북 문법 테스트" ".venv/bin/pytest tests/unit/test_playbooks/test_syntax.py::TestPlaybookSyntax::test_yaml_syntax -q"

# 4. Ansible 플레이북 구조 테스트
run_test "플레이북 구조 테스트" ".venv/bin/pytest tests/unit/test_playbooks/test_syntax.py::TestPlaybookSyntax::test_playbook_structure -q"

# 5. Preparation 플레이북 테스트
run_test "Preparation 플레이북 테스트" ".venv/bin/pytest tests/unit/test_playbooks/test_preparation_playbooks.py::TestSetupRootSSH -q"

# 6. Validation 플레이북 테스트
run_test "Validation 플레이북 테스트" ".venv/bin/pytest tests/unit/test_playbooks/test_validation_playbooks.py::TestValidateClusterHealth -q"

# 7. Ansible 검증 (ansible-lint 포함)
run_test "Ansible 종합 검증" "./tests/ansible/test_validate_playbooks.sh"

# 8. 전체 단위 테스트
run_test "전체 단위 테스트" ".venv/bin/pytest tests/unit/ -q"

# 결과 요약
echo "=========================================="
echo "📊 테스트 결과 요약"
echo "=========================================="
echo -e "전체 테스트: $TOTAL_TESTS"
echo -e "${GREEN}통과: $PASSED_TESTS${NC}"
echo -e "${RED}실패: $FAILED_TESTS${NC}"
echo -e "${YELLOW}건너뜀: $SKIPPED_TESTS${NC}"
echo ""

# 성공률 계산
if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "성공률: ${SUCCESS_RATE}%"

    # 진행 바 표시
    BAR_LENGTH=50
    FILLED_LENGTH=$((SUCCESS_RATE * BAR_LENGTH / 100))

    echo -n "["
    for ((i=0; i<$FILLED_LENGTH; i++)); do
        echo -n "="
    done
    for ((i=$FILLED_LENGTH; i<$BAR_LENGTH; i++)); do
        echo -n " "
    done
    echo "] ${SUCCESS_RATE}%"
fi

echo ""

# 최종 결과
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🎉 모든 테스트 통과!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  일부 테스트 실패${NC}"
    echo "상세 내용은 개별 테스트 출력을 확인하세요."
    exit 1
fi