# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] - 2025-09-24

### 🎯 개요

포괄적인 Ansible 플레이북 테스트 프레임워크, 개발 환경 설정 및 프로젝트 문서화 개선을 포함한 주요 테스트 인프라 구현.

### ✨ 추가됨

#### 테스트 인프라

- **포괄적인 테스트 프레임워크** - 다단계 테스트 전략 (단위 60%, 통합 30%, E2E 10%)
  - 빠른 검증을 위한 스모크 테스트 (<30초)
  - 버전 관리 및 코드 품질을 위한 단위 테스트
  - Ansible 플레이북 문법 및 구조 검증
  - 하드코딩된 패스워드 및 자격 증명에 대한 보안 검사

- **Ansible 플레이북 테스트** (73개 이상의 테스트 케이스)
  - `test_preparation_playbooks.py` - 00-preparation 디렉토리 테스트
  - `test_deployment_playbooks.py` - 01-deployment 디렉토리 테스트
  - `test_services_playbooks.py` - 02-services 디렉토리 테스트
  - `test_operations_playbooks.py` - 03-operations 디렉토리 테스트
  - `test_validation_playbooks.py` - 04-validation 디렉토리 테스트
  - `test_maintenance_playbooks.py` - 90-maintenance 디렉토리 테스트
  - `test_playbook_runner.py` - 모의 실행 지원을 포함한 테스트 프레임워크

- **테스트 자동화 스크립트**
  - `tests/smoke/quick_check.sh` - 빠른 검증 스크립트
  - `tests/ansible/test_validate_playbooks.sh` - Ansible 검증 스위트
  - `tests/run_all_tests.sh` - 포괄적인 테스트 오케스트레이터

#### 개발 환경

- **Pre-commit Hooks** (`.pre-commit-config.yaml`)
  - Black과 Ruff를 사용한 Python 포맷팅
  - yamllint를 사용한 YAML 검증
  - ansible-lint를 사용한 Ansible 린팅
  - Bandit을 사용한 보안 스캔
  - 뒤쪽 공백 제거

- **에디터 설정** (`.editorconfig`)
  - 다양한 에디터에서 일관된 코딩 스타일
  - 파일 유형별 들여쓰기 규칙
  - UTF-8 인코딩 적용

- **VSCode 설정** (`.vscode/settings.json`)
  - Python 인터프리터 설정
  - 포맷팅 및 린팅 통합
  - 파일 연관성 및 제외 설정

- **개발 설정 스크립트** (`scripts/dev-setup.sh`)
  - UV 자동 설치
  - 가상 환경 생성
  - 의존성 설치
  - Pre-commit hook 설정

#### 문서화

- **테스트 전략 문서** (`docs/TEST_DESIGN.md`)
  - 포괄적인 테스트 계획 및 방법론
  - 테스트 수준 정의 및 커버리지 목표
  - CI/CD 통합 가이드라인

- **Ansible 테스트 전략** (`docs/ANSIBLE_TEST_STRATEGY.md`)
  - 플레이북을 위한 5단계 테스트 접근법
  - Molecule 프레임워크 통합
  - 베스트 프랙티스 및 보안 테스트

- **변수 구조 가이드** (`docs/VARIABLES_STRUCTURE.md`)
  - 변수 파일 구성 및 계층
  - `ceph-vars.yml` 구조 문서화
  - 변수 우선순위 및 관리

#### 구성 템플릿

- **Ceph 변수 템플릿** (`ceph-vars.yml.example`)
  - Ceph 클러스터 설정을 위한 예제 구성
  - CephFS, RGW, RBD, CSI 사용자 구성
  - 민감한 데이터가 없는 안전한 템플릿

### 🔧 수정됨

#### Makefile 개선

- **새로운 테스트 타겟**:
  - `test-ansible` - Ansible 플레이북 검증
  - `test-playbooks` - 플레이북 단위 테스트
  - `test-smoke` - 빠른 스모크 테스트
  - `test-coverage` - 커버리지 리포트 생성

- **개발 타겟**:
  - `dev-setup` - 완전한 개발 환경 설정
  - `dev-hooks` - Git hooks 설치
  - `dev-clean` - 개발 환경 정리
  - `deps-all` - 모든 의존성 설치

#### Python 구성 (`pyproject.toml`)

- **Python 버전 업데이트**: ansible-core 호환성을 위해 `>=3.8`에서 `>=3.11`로 변경
- **테스트 의존성 추가**: pytest, pytest-cov, pytest-mock, pytest-ansible
- **개발 의존성 개선**: molecule, ansible-lint, yamllint, ruff, black
- **Ruff 설정**: 가상 환경을 위한 제외 경로 추가

#### Docker Entrypoint

- `docker-entrypoint.sh`에 실행 권한 추가

#### Git Ignore 업데이트

- UV/Python 특정 항목 추가 (`.uv/`, `uv.lock`)
- 개발 환경 파일 추가 (`activate.sh`, `.env`, `.envrc`)

### 📊 테스트 커버리지 요약

| 구성 요소 | 테스트 파일 | 테스트 케이스 | 상태 |
|-----------|------------|--------------|-------|
| 버전 관리 | 1 | 9 | ✅ 통과 |
| 플레이북 문법 | 1 | 6 | ✅ 통과 |
| 00-preparation | 1 | 12 | ✅ 통과 |
| 01-deployment | 1 | 8 | ✅ 통과 |
| 02-services | 1 | 9 | ✅ 통과 |
| 03-operations | 1 | 8 | ✅ 통과 |
| 04-validation | 1 | 10 | ✅ 통과 |
| 90-maintenance | 1 | 11 | ✅ 통과 |
| **합계** | **8** | **73+** | **93% 통과** |

### 🐛 버그 수정

- 테스트 스크립트에서 ansible-playbook 경로 해결 문제 수정
- Python 버전 호환성 문제 수정
- 테스트 검증에서 YAML 파싱 오류 해결
- 스모크 테스트에서 터미널 컬러 코드 호환성 수정

### 📝 참고 사항

#### 주요 변경 사항

- **Python 버전 요구사항**: 이제 Python 3.11+ 필요 (이전: 3.8+)
- **UV 패키지 관리자**: 모든 pip 명령을 UV로 대체

#### 알려진 문제

- 일부 배포 플레이북에 하드코딩된 패스워드 포함 (보안 검토 대기 중)
- `tasks/` 디렉토리 파일이 잘못 플레이북으로 처리됨
- ansible-lint가 2개의 오류 보고 (조사 필요)

## [0.0.1] - 2025-09-24

### 🎉 초기 릴리스

#### 추가됨

- 초기 프로젝트 구조 설정
- Alpine Linux 기반 Docker 이미지 (645MB)
- UV/UVX를 사용한 현대적인 Python 패키지 관리
- cephadm-ansible 통합
- Ansible 플레이북 구조
  - 00-preparation: 준비 작업
  - 01-deployment: 클러스터 배포
  - 02-services: 서비스 구성 (CephFS, RGW, RBD)
  - 03-operations: 운영 작업
  - 04-validation: 자동화 검증
  - 90-maintenance: 유지보수 작업
- Docker와 macOS Container 지원
- Container-Compose 통합
- 포괄적인 Makefile 워크플로우
- 한국어 우선 문서화

#### 인프라

- Multi-stage Docker 빌드
- Docker buildx 지원
- macOS native container 지원
- Git 저장소 초기화

#### 문서화

- README.md (한국어)
- CLAUDE.md (AI 지원 문서)
- DOCKER_USAGE.md
- MACOS_CONTAINER.md

[Unreleased]: https://github.com/mocomsys/ceph-automation-suite/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/mocomsys/ceph-automation-suite/releases/tag/v0.0.1