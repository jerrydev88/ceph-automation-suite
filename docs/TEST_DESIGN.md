# Test Design Document - Ceph Automation Suite

## 📋 목차

1. [개요](#개요)
2. [테스트 전략](#테스트-전략)
3. [테스트 레벨](#테스트-레벨)
4. [테스트 구조](#테스트-구조)
5. [테스트 도구](#테스트-도구)
6. [테스트 구현](#테스트-구현)
7. [CI/CD 통합](#cicd-통합)
8. [품질 메트릭](#품질-메트릭)
9. [구현 로드맵](#구현-로드맵)

## 개요

### 목적
Ceph Automation Suite의 안정성과 신뢰성을 보장하기 위한 포괄적인 테스트 전략 수립

### 범위
- Ansible 플레이북 검증
- Docker 이미지 품질 보증
- Python 스크립트 테스트
- 통합 워크플로우 검증
- 성능 및 보안 테스트

### 핵심 원칙
1. **Shift-Left Testing**: 개발 초기부터 테스트 적용
2. **Test Automation First**: 모든 테스트 자동화 우선
3. **Fast Feedback**: 빠른 피드백 루프 구축
4. **Quality Gates**: 명확한 품질 기준 설정

## 테스트 전략

### 테스트 피라미드

```
         /\
        /  \  E2E Tests (10%)
       /----\
      /      \  Integration Tests (30%)
     /--------\
    /          \  Unit Tests (60%)
   /____________\
```

### 테스트 접근법

| 레벨 | 목적 | 도구 | 실행 시간 |
|------|------|------|-----------|
| Unit | 개별 기능 검증 | pytest | < 1분 |
| Integration | 컴포넌트 간 상호작용 | molecule, docker-compose | < 5분 |
| System | 전체 워크플로우 | bash, ansible | < 10분 |
| Smoke | 핵심 기능 빠른 검증 | make test-smoke | < 30초 |

## 테스트 레벨

### 1. Unit Tests (단위 테스트)

**대상:**
- Python 유틸리티 함수
- 버전 관리 스크립트
- 설정 파일 파서

**예시:**
```python
# tests/unit/test_version.py
def test_version_bump_patch():
    """패치 버전 증가 테스트"""
    assert bump_version("1.0.0", "patch") == "1.0.1"
```

### 2. Integration Tests (통합 테스트)

**대상:**
- Ansible 플레이북 실행
- Docker 이미지 빌드
- 스크립트 간 상호작용

**예시:**
```yaml
# tests/integration/test_playbook.yml
- name: Test Ceph deployment playbook
  hosts: localhost
  tasks:
    - include: ../../playbooks/01-deployment/bootstrap.yml
```

### 3. System Tests (시스템 테스트)

**대상:**
- 전체 배포 프로세스
- 엔드투엔드 시나리오
- 멀티노드 클러스터 시뮬레이션

### 4. Performance Tests (성능 테스트)

**메트릭:**
- Docker 이미지 빌드 시간: < 5분
- 이미지 크기: < 700MB
- 플레이북 실행 시간: 기준선 대비 ±10%

### 5. Security Tests (보안 테스트)

**검사 항목:**
- Docker 이미지 취약점 스캔 (Trivy)
- 비밀 정보 노출 검사
- SAST/DAST 분석

## 테스트 구조

```
tests/
├── unit/                    # 단위 테스트
│   ├── test_version.py      # 버전 관리 테스트
│   ├── test_utils.py        # 유틸리티 함수 테스트
│   └── test_config.py       # 설정 파일 테스트
├── integration/             # 통합 테스트
│   ├── test_docker.py       # Docker 빌드 테스트
│   ├── test_ansible/        # Ansible 플레이북 테스트
│   │   ├── molecule/        # Molecule 시나리오
│   │   └── inventory/       # 테스트 인벤토리
│   └── test_makefile.sh     # Makefile 타겟 테스트
├── system/                  # 시스템 테스트
│   ├── test_deployment.sh   # 전체 배포 테스트
│   └── scenarios/           # 테스트 시나리오
├── fixtures/                # 테스트 데이터
│   ├── mock_inventory.yml   # 모의 인벤토리
│   └── test_configs/        # 테스트 설정 파일
├── conftest.py              # pytest 설정
└── requirements-test.txt    # 테스트 의존성
```

## 테스트 도구

### Python 테스트

```toml
# pyproject.toml
[project.optional-dependencies]
test = [
    "pytest>=7.0",
    "pytest-cov>=4.0",
    "pytest-mock>=3.0",
    "pytest-asyncio>=0.21",
    "pytest-xdist>=3.0",  # 병렬 실행
]
```

### Ansible 테스트

```yaml
# requirements-test.yml
collections:
  - name: community.molecule
  - name: community.docker

python:
  - molecule>=5.0
  - ansible-lint>=6.0
  - yamllint>=1.32
```

### Docker 테스트

```dockerfile
# Dockerfile.test
FROM hadolint/hadolint AS lint
COPY Dockerfile /tmp/
RUN hadolint /tmp/Dockerfile

FROM aquasec/trivy AS security
COPY --from=builder /app /tmp/app
RUN trivy fs /tmp/app
```

## 테스트 구현

### Makefile 타겟 추가

```makefile
# 테스트 타겟
.PHONY: test test-unit test-integration test-system test-all

test: test-unit test-smoke
	@echo "✅ 기본 테스트 완료"

test-unit:
	@echo "🧪 단위 테스트 실행..."
	@pytest tests/unit -v --cov=scripts

test-integration:
	@echo "🔗 통합 테스트 실행..."
	@molecule test
	@./tests/integration/test_makefile.sh

test-system:
	@echo "🎯 시스템 테스트 실행..."
	@./tests/system/test_deployment.sh

test-smoke:
	@echo "💨 스모크 테스트 실행..."
	@./tests/smoke/quick_check.sh

test-security:
	@echo "🔒 보안 테스트 실행..."
	@trivy image ceph-automation-suite:latest
	@hadolint Dockerfile

test-all: test-unit test-integration test-system test-security
	@echo "✅ 전체 테스트 완료"

test-watch:
	@echo "👁️ 테스트 감시 모드..."
	@pytest-watch tests/

test-coverage:
	@echo "📊 커버리지 리포트 생성..."
	@pytest tests/ --cov --cov-report=html
	@open htmlcov/index.html
```

### 샘플 테스트 구현

#### 1. 단위 테스트

```python
# tests/unit/test_version.py
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

def test_version_file_exists():
    """VERSION 파일 존재 확인"""
    version_file = Path("VERSION")
    assert version_file.exists()

def test_version_format():
    """버전 형식 검증 (semantic versioning)"""
    with open("VERSION") as f:
        version = f.read().strip()

    parts = version.split(".")
    assert len(parts) == 3
    assert all(p.isdigit() for p in parts)

def test_version_consistency():
    """모든 파일의 버전 일관성 확인"""
    with open("VERSION") as f:
        version = f.read().strip()

    # pyproject.toml 확인
    import toml
    with open("pyproject.toml") as f:
        pyproject = toml.load(f)
    assert pyproject["project"]["version"] == version

    # Dockerfile 확인
    with open("Dockerfile") as f:
        dockerfile = f.read()
    assert f'ARG VERSION={version}' in dockerfile
```

#### 2. 통합 테스트

```bash
#!/bin/bash
# tests/integration/test_makefile.sh

set -e

echo "🧪 Makefile 통합 테스트"

# 테스트 1: 버전 관리 워크플로우
echo "Test 1: Version management workflow"
make version
make bump-patch
VERSION_AFTER=$(cat VERSION)
git checkout VERSION  # 롤백

# 테스트 2: Docker 빌드 프로세스
echo "Test 2: Docker build process"
make build
docker images | grep ceph-automation-suite

# 테스트 3: 클린업
echo "Test 3: Cleanup process"
make clean

echo "✅ Makefile 통합 테스트 완료"
```

#### 3. 시스템 테스트

```yaml
# tests/system/scenarios/full_deployment.yml
---
- name: Full deployment test scenario
  hosts: localhost
  gather_facts: yes
  vars:
    test_mode: true

  tasks:
    - name: Prepare test environment
      include: prepare_test_env.yml

    - name: Run deployment playbook
      include: ../../../playbooks/01-deployment/complete-deployment.yml

    - name: Validate deployment
      include: ../../../playbooks/04-validation/validate-all.yml

    - name: Cleanup test environment
      include: cleanup_test_env.yml
      when: always
```

### Pre-commit Hooks 설정

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml

  - repo: https://github.com/psf/black
    rev: 23.12.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/ansible/ansible-lint
    rev: v6.22.0
    hooks:
      - id: ansible-lint
        files: \.(yaml|yml)$

  - repo: https://github.com/shellcheck-py/shellcheck-py
    rev: v0.9.0.6
    hooks:
      - id: shellcheck
```

## CI/CD 통합

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Lint code
        run: |
          pip install -r requirements-test.txt
          make lint

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run unit tests
        run: |
          pip install -e ".[test]"
          make test-unit

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml

  integration-tests:
    runs-on: ubuntu-latest
    services:
      docker:
        image: docker:dind
        options: --privileged

    steps:
      - uses: actions/checkout@v4

      - name: Build Docker image
        run: make build

      - name: Run integration tests
        run: make test-integration

  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'ceph-automation-suite:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

## 품질 메트릭

### Coverage Targets

| 컴포넌트 | 목표 | 임계값 |
|---------|------|--------|
| Python Scripts | 80% | 70% |
| Ansible Playbooks | 100% syntax | - |
| Docker Build | 100% success | - |
| Critical Paths | 100% | 95% |

### Performance Benchmarks

| 메트릭 | 목표 | 최대 |
|--------|------|------|
| Unit Test Suite | < 1분 | 2분 |
| Integration Suite | < 5분 | 10분 |
| Full Test Suite | < 15분 | 30분 |
| Docker Build | < 3분 | 5분 |
| Image Size | < 650MB | 700MB |

### Quality Gates

✅ **Required for Merge:**
- All tests passing
- Coverage > 70%
- No critical security issues
- No high-priority bugs
- Documentation updated

⚠️ **Warning Indicators:**
- Coverage decrease > 5%
- Performance regression > 10%
- New security warnings

## 구현 로드맵

### Phase 1: Foundation (Week 1)
- [x] 테스트 전략 문서화
- [ ] 테스트 디렉토리 구조 생성
- [ ] 기본 pytest 설정
- [ ] 첫 단위 테스트 작성

### Phase 2: Unit Testing (Week 2)
- [ ] 버전 관리 테스트
- [ ] 유틸리티 함수 테스트
- [ ] 설정 파일 검증 테스트
- [ ] Coverage 80% 달성

### Phase 3: Integration Testing (Week 3)
- [ ] Molecule 설정
- [ ] Ansible 플레이북 테스트
- [ ] Docker 빌드 테스트
- [ ] Makefile 타겟 테스트

### Phase 4: CI/CD Integration (Week 4)
- [ ] GitHub Actions 설정
- [ ] Pre-commit hooks 구성
- [ ] Security scanning 통합
- [ ] Coverage reporting

### Phase 5: Advanced Testing (Week 5)
- [ ] Performance benchmarking
- [ ] Load testing
- [ ] Chaos testing
- [ ] Documentation

## 리스크 및 완화 전략

### 식별된 리스크

| 리스크 | 영향도 | 확률 | 완화 전략 |
|--------|--------|------|-----------|
| 테스트 실행 시간 과다 | 높음 | 중간 | 병렬 실행, 테스트 분류 |
| 외부 의존성 실패 | 중간 | 낮음 | Mock 사용, 로컬 캐싱 |
| 테스트 복잡도 증가 | 중간 | 높음 | 모듈화, 명확한 문서화 |
| 인프라 테스트 어려움 | 높음 | 높음 | Container 기반 격리 |

### 완화 전략 상세

1. **병렬 실행**
   - pytest-xdist 사용
   - GitHub Actions matrix builds
   - Docker layer caching

2. **테스트 분류**
   - Fast/Slow 구분
   - Critical/Non-critical 구분
   - Smoke test suite 별도 관리

3. **Mock 및 Stub 활용**
   - 외부 API mock
   - 시간 소요 작업 stub
   - Test doubles 사용

## 결론

이 테스트 전략은 Ceph Automation Suite의 품질과 신뢰성을 보장하는 포괄적인 프레임워크를 제공합니다. 단계적 구현을 통해 리스크를 최소화하면서 점진적으로 테스트 커버리지를 확대할 수 있습니다.

### 성공 지표
- 🎯 80% 이상 코드 커버리지
- ⚡ 10분 이내 CI 파이프라인
- 🐛 프로덕션 크리티컬 버그 제로
- 🚀 완전 자동화된 릴리스 프로세스

### 다음 단계
1. 테스트 디렉토리 구조 생성
2. pytest 및 테스트 도구 설정
3. 첫 단위 테스트 작성
4. CI/CD 파이프라인 구성

---

**작성일**: 2024-01-24
**버전**: 1.0.0
**작성자**: Ceph Automation Suite Team