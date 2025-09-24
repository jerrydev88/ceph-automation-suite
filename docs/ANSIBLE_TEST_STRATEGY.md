# Ansible 플레이북 테스트 전략

## 개요
Ceph Automation Suite의 Ansible 플레이북을 위한 포괄적인 테스트 전략입니다.

## 테스트 레벨

### 1. 문법 검증 (Syntax Validation)
- **도구**: ansible-playbook --syntax-check
- **목적**: YAML 문법 및 Ansible 구문 검증
- **실행 시간**: < 5초
- **커버리지**: 100% 플레이북

### 2. 린팅 (Linting)
- **도구**: ansible-lint, yamllint
- **목적**: 베스트 프랙티스 준수 확인
- **실행 시간**: < 10초
- **규칙**:
  - 하드코딩된 패스워드 검출
  - deprecated 모듈 사용 금지
  - 태그 일관성
  - 변수 명명 규칙

### 3. 드라이런 테스트 (Dry-Run)
- **도구**: ansible-playbook --check
- **목적**: 실행 시뮬레이션
- **실행 시간**: < 30초
- **검증 항목**:
  - 태스크 실행 순서
  - 조건문 평가
  - 변수 해석

### 4. Molecule 통합 테스트
- **도구**: Molecule + Docker/Podman
- **목적**: 격리된 환경에서 실제 실행
- **실행 시간**: 5-10분
- **시나리오**:
  - 새 설치 (fresh install)
  - 멱등성 (idempotency)
  - 업그레이드
  - 롤백

### 5. 모의 테스트 (Mock Testing)
- **도구**: pytest-ansible
- **목적**: 외부 의존성 없이 로직 검증
- **실행 시간**: < 1분
- **대상**:
  - 커스텀 모듈
  - 필터 플러그인
  - 복잡한 조건문

## 테스트 구조

```
tests/
├── unit/                      # 단위 테스트
│   ├── test_playbooks/        # 플레이북 문법/구조
│   ├── test_roles/            # 역할 테스트
│   └── test_modules/          # 커스텀 모듈
├── integration/               # 통합 테스트
│   ├── molecule/             # Molecule 시나리오
│   └── test_scenarios/       # 엔드투엔드 시나리오
└── fixtures/                 # 테스트 데이터
    ├── inventory/           # 테스트 인벤토리
    └── vars/               # 테스트 변수
```

## 테스트 시나리오

### 배포 플레이북 테스트
```yaml
# molecule/deployment/molecule.yml
---
dependency:
  name: galaxy
driver:
  name: docker
platforms:
  - name: ceph-mon
    image: ubuntu:22.04
    groups:
      - mons
  - name: ceph-osd
    image: ubuntu:22.04
    groups:
      - osds
provisioner:
  name: ansible
  inventory:
    group_vars:
      all:
        container_test: true
verifier:
  name: ansible
```

### 검증 플레이북 테스트
```yaml
# tests/unit/test_playbooks/test_validate_health.py
import pytest
from ansible_playbook_runner import PlaybookRunner

class TestValidateHealth:
    def test_health_check_syntax(self):
        """플레이북 문법 검증"""
        runner = PlaybookRunner(
            'playbooks/04-validation/validate-cluster-health.yml'
        )
        assert runner.syntax_check() == 0

    def test_health_check_with_mock_data(self, mock_ceph_status):
        """모의 데이터로 헬스체크 로직 검증"""
        runner = PlaybookRunner(
            'playbooks/04-validation/validate-cluster-health.yml',
            extra_vars={'ceph_status': mock_ceph_status}
        )
        result = runner.run(check=True)
        assert 'HEALTH_OK' in result.stats
```

## 테스트 자동화

### Makefile 타겟
```makefile
test-ansible-syntax:
    @echo "🔍 Ansible 문법 검증..."
    @find playbooks -name "*.yml" -exec \
        ansible-playbook --syntax-check {} \;

test-ansible-lint:
    @echo "🔍 Ansible 린팅..."
    @ansible-lint playbooks/

test-ansible-dry:
    @echo "🔍 Dry-run 테스트..."
    @ansible-playbook -i tests/fixtures/inventory/test.yml \
        playbooks/04-validation/validate-all.yml --check

test-molecule:
    @echo "🧪 Molecule 테스트..."
    @cd tests/integration/molecule && \
        molecule test --all
```

### CI/CD 파이프라인
```yaml
# .github/workflows/ansible-test.yml
name: Ansible Tests
on: [push, pull_request]
jobs:
  syntax:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Syntax Check
        run: make test-ansible-syntax

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Lint Playbooks
        run: make test-ansible-lint

  molecule:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Molecule Test
        run: make test-molecule
```

## 테스트 데이터 관리

### 모의 인벤토리
```yaml
# tests/fixtures/inventory/test.yml
all:
  children:
    mons:
      hosts:
        test-mon-01:
          ansible_connection: local
    osds:
      hosts:
        test-osd-01:
          ansible_connection: local
```

### 테스트 변수
```yaml
# tests/fixtures/vars/test_vars.yml
ceph_version: pacific
cluster_network: 10.0.0.0/24
public_network: 192.168.1.0/24
test_mode: true
```

## 멱등성 테스트

```python
# tests/integration/test_idempotency.py
def test_playbook_idempotency():
    """플레이북 멱등성 검증"""
    # 첫 번째 실행
    first_run = run_playbook('deploy.yml')
    assert first_run.changed_count > 0

    # 두 번째 실행 (변경 없어야 함)
    second_run = run_playbook('deploy.yml')
    assert second_run.changed_count == 0
```

## 성능 벤치마크

```python
# tests/performance/test_playbook_performance.py
import time

def test_validation_performance():
    """검증 플레이북 성능 테스트"""
    start = time.time()
    run_playbook('validate-all.yml')
    duration = time.time() - start

    assert duration < 60, "Validation should complete within 1 minute"
```

## 보안 테스트

```yaml
# .ansible-lint
exclude_paths:
  - .cache/
  - .github/
skip_list:
  - yaml[line-length]

warn_list:
  - no-changed-when
  - package-latest

rules:
  - no-passwords-in-vars
  - no-secrets-in-code
  - use-vault-for-secrets
```

## 테스트 커버리지 목표

| 테스트 유형 | 목표 커버리지 | 현재 상태 |
|------------|-------------|----------|
| 문법 검증 | 100% | 🟡 구현 필요 |
| 린팅 | 100% | 🟡 구현 필요 |
| 단위 테스트 | 80% | 🔴 미구현 |
| 통합 테스트 | 60% | 🔴 미구현 |
| E2E 테스트 | 40% | 🔴 미구현 |

## 구현 로드맵

### Phase 1: 기본 검증 (1주)
- [ ] ansible-lint 설정
- [ ] yamllint 설정
- [ ] 문법 검증 자동화
- [ ] Makefile 타겟 추가

### Phase 2: Molecule 설정 (2주)
- [ ] Molecule 프레임워크 설치
- [ ] Docker 시나리오 구성
- [ ] 기본 테스트 시나리오 작성
- [ ] CI 통합

### Phase 3: 커스텀 테스트 (2주)
- [ ] pytest-ansible 설정
- [ ] 모의 데이터 생성
- [ ] 커스텀 assertion 개발
- [ ] 성능 벤치마크 구현

### Phase 4: 자동화 및 최적화 (1주)
- [ ] GitHub Actions 워크플로우
- [ ] 테스트 병렬화
- [ ] 리포팅 시스템
- [ ] 문서화

## 모범 사례

1. **테스트 격리**: 각 테스트는 독립적으로 실행 가능해야 함
2. **빠른 피드백**: 문법/린팅 테스트는 1분 이내 완료
3. **점진적 테스트**: commit 시 빠른 테스트, PR 시 전체 테스트
4. **테스트 데이터 버전 관리**: 실제 환경과 동일한 버전 사용
5. **실패 시 명확한 메시지**: 무엇이 왜 실패했는지 명확히 표시

## 도구 체인

- **ansible-lint**: Ansible 베스트 프랙티스 검증
- **yamllint**: YAML 문법 검증
- **molecule**: 통합 테스트 프레임워크
- **pytest-ansible**: Python 기반 Ansible 테스트
- **testinfra**: 인프라 상태 검증
- **ansible-test**: Ansible 공식 테스트 도구