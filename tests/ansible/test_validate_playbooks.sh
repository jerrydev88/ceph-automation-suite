#!/bin/bash

# Ansible 플레이북 검증 스크립트
# 실행 시간: < 1분

# set -e 제거 - 개별 오류 처리

echo "🔍 Ansible 플레이북 검증 시작"
echo "=============================="

# 색상 정의
if [ -t 1 ]; then
    GREEN='\033[0;32m'
    RED='\033[0;31m'
    YELLOW='\033[1;33m'
    NC='\033[0m'
else
    GREEN=''
    RED=''
    YELLOW=''
    NC=''
fi

# 카운터
PASSED=0
FAILED=0
WARNINGS=0

# 프로젝트 루트 디렉토리
PROJECT_ROOT=$(cd "$(dirname "$0")/../.." && pwd)
PLAYBOOK_DIR="$PROJECT_ROOT/playbooks"
TEST_INVENTORY="$PROJECT_ROOT/tests/fixtures/ansible_inventory.yml"

# Python 환경 설정
if [ -f "$PROJECT_ROOT/.venv/bin/python" ]; then
    PYTHON="$PROJECT_ROOT/.venv/bin/python"
else
    PYTHON="python3"
fi

# 결과 출력 함수
print_result() {
    local status=$1
    local message=$2

    if [ "$status" = "pass" ]; then
        echo -e "${GREEN}✓${NC} $message"
        ((PASSED++))
    elif [ "$status" = "fail" ]; then
        echo -e "${RED}✗${NC} $message"
        ((FAILED++))
    else
        echo -e "${YELLOW}⚠${NC} $message"
        ((WARNINGS++))
    fi
}

# 1. Ansible 설치 확인
echo "📦 환경 확인..."
# venv에서 ansible-playbook 찾기
if [ -f "$PROJECT_ROOT/.venv/bin/ansible-playbook" ]; then
    ANSIBLE_PLAYBOOK="$PROJECT_ROOT/.venv/bin/ansible-playbook"
    print_result "pass" "ansible-playbook 설치됨 (venv)"
elif command -v ansible-playbook >/dev/null 2>&1; then
    ANSIBLE_PLAYBOOK="ansible-playbook"
    print_result "pass" "ansible-playbook 설치됨 (시스템)"
else
    print_result "fail" "ansible-playbook이 설치되지 않음"
    echo "설치: uv pip install ansible"
    exit 1
fi

# 2. YAML 문법 검증
echo ""
echo "📝 YAML 문법 검증..."
yaml_errors=0
for playbook in $(find "$PLAYBOOK_DIR" -name "*.yml" -type f); do
    if $PYTHON -c "import yaml; yaml.safe_load(open('$playbook'))" 2>/dev/null; then
        :  # 성공
    else
        print_result "fail" "YAML 문법 오류: ${playbook#$PROJECT_ROOT/}"
        ((yaml_errors++))
    fi
done

if [ $yaml_errors -eq 0 ]; then
    print_result "pass" "모든 YAML 파일 문법 정상"
fi

# 3. Ansible 문법 검사 (주요 플레이북만)
echo ""
echo "🔍 Ansible 문법 검사..."
ansible_errors=0

# 검증할 주요 플레이북 목록
MAIN_PLAYBOOKS=(
    "04-validation/validate-all.yml"
    "04-validation/validate-cluster-health.yml"
    "02-services/configure-global.yml"
)

for playbook_path in "${MAIN_PLAYBOOKS[@]}"; do
    full_path="$PLAYBOOK_DIR/$playbook_path"
    if [ -f "$full_path" ]; then
        if $ANSIBLE_PLAYBOOK --syntax-check -i "$TEST_INVENTORY" "$full_path" >/dev/null 2>&1; then
            print_result "pass" "문법 검사 통과: $playbook_path"
        else
            print_result "fail" "문법 검사 실패: $playbook_path"
            ((ansible_errors++))
        fi
    else
        print_result "warn" "파일 없음: $playbook_path"
    fi
done

# 4. 보안 검사 (하드코딩된 패스워드)
echo ""
echo "🔒 보안 검사..."
security_issues=0

# 패스워드 패턴 검색
password_patterns=("password:" "passwd:" "secret:" "token:" "api_key:")
for pattern in "${password_patterns[@]}"; do
    matches=$(grep -r "$pattern" "$PLAYBOOK_DIR" --include="*.yml" 2>/dev/null | grep -v "^#" | grep -v "vault" | grep -v "{{" || true)
    if [ -n "$matches" ]; then
        print_result "warn" "잠재적 보안 이슈 - $pattern 패턴 발견"
        ((security_issues++))
    fi
done

if [ $security_issues -eq 0 ]; then
    print_result "pass" "하드코딩된 인증정보 없음"
fi

# 5. 베스트 프랙티스 검사
echo ""
echo "📋 베스트 프랙티스 검사..."

# name 필드 확인
tasks_without_name=$(grep -r "^\s*-\s*[a-z]" "$PLAYBOOK_DIR" --include="*.yml" 2>/dev/null | grep -v "name:" | wc -l | tr -d ' ' || echo "0")
if [ "$tasks_without_name" -gt 0 ]; then
    print_result "warn" "name 필드 없는 태스크: ${tasks_without_name}개"
else
    print_result "pass" "모든 태스크에 name 필드 있음"
fi

# 6. ansible-lint 실행 (설치되어 있는 경우)
echo ""
echo "🔍 Ansible Lint..."
# venv에서 ansible-lint 찾기
if [ -f "$PROJECT_ROOT/.venv/bin/ansible-lint" ]; then
    ANSIBLE_LINT="$PROJECT_ROOT/.venv/bin/ansible-lint"
elif command -v ansible-lint >/dev/null 2>&1; then
    ANSIBLE_LINT="ansible-lint"
else
    ANSIBLE_LINT=""
fi

if [ -n "$ANSIBLE_LINT" ]; then
    lint_output=$($ANSIBLE_LINT "$PLAYBOOK_DIR" 2>&1 || true)
    lint_errors=$(echo "$lint_output" | grep -c "ERROR" || echo "0")
    lint_warnings=$(echo "$lint_output" | grep -c "WARNING" || echo "0")

    # 숫자만 추출
    lint_errors=$(echo "$lint_errors" | tr -d ' ')
    lint_warnings=$(echo "$lint_warnings" | tr -d ' ')

    if [ "$lint_errors" = "0" ] || [ "$lint_errors" -eq 0 ]; then
        print_result "pass" "ansible-lint 오류 없음"
    else
        print_result "fail" "ansible-lint 오류: ${lint_errors}개"
    fi

    if [ "$lint_warnings" != "0" ] && [ "$lint_warnings" -gt 0 ]; then
        print_result "warn" "ansible-lint 경고: ${lint_warnings}개"
    fi
else
    print_result "warn" "ansible-lint 미설치 (선택사항)"
fi

# 7. 플레이북 구조 검증
echo ""
echo "📂 디렉토리 구조 검증..."
required_dirs=("02-services" "04-validation")
for dir in "${required_dirs[@]}"; do
    if [ -d "$PLAYBOOK_DIR/$dir" ]; then
        count=$(find "$PLAYBOOK_DIR/$dir" -name "*.yml" 2>/dev/null | wc -l | tr -d ' ')
        print_result "pass" "$dir 디렉토리: ${count}개 플레이북"
    else
        print_result "fail" "$dir 디렉토리 없음"
    fi
done

# 결과 요약
echo ""
echo "=============================="
echo "검증 결과 요약"
echo "=============================="
echo -e "${GREEN}통과: $PASSED${NC}"
echo -e "${YELLOW}경고: $WARNINGS${NC}"
echo -e "${RED}실패: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ Ansible 플레이북 검증 성공!${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Ansible 플레이북 검증 실패${NC}"
    exit 1
fi