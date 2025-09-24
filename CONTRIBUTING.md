# Contributing to Ceph Automation Suite

이 문서는 Ceph Automation Suite 프로젝트에 기여하려는 개발자를 위한 가이드입니다.

## 📋 목차

- [개발 환경 설정](#개발-환경-설정)
- [프로젝트 구조](#프로젝트-구조)
- [개발 워크플로우](#개발-워크플로우)
- [Makefile 타겟 가이드](#makefile-타겟-가이드)
- [버전 관리](#버전-관리)
- [테스트](#테스트)
- [컨트리뷰션 가이드라인](#컨트리뷰션-가이드라인)

## 개발 환경 설정

### 사전 요구사항

- Python 3.8+ (3.11 권장)
- Docker 또는 macOS Container Runtime
- UV (Python 패키지 매니저)
- Git

### 초기 설정

```bash
# 1. 저장소 클론
git clone https://github.com/jerrydev88/ceph-automation-suite.git
cd ceph-automation-suite

# 2. UV 설치 (아직 설치되지 않은 경우)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 3. 개발 환경 초기화
make init
```

### macOS 사용자를 위한 추가 설정

```bash
# Container-Compose 설치 (Docker Compose 대체)
make install-container-compose

# Container 런타임 확인
make help  # 감지된 런타임 확인
```

## 프로젝트 구조

```
ceph-automation-suite/
├── playbooks/               # Ansible 플레이북
│   ├── 00-preparation/      # 준비 작업
│   ├── 01-deployment/       # 클러스터 배포
│   ├── 02-services/         # 서비스 구성
│   ├── 03-operations/       # 운영 작업
│   ├── 04-validation/       # 검증 스위트
│   └── 90-maintenance/      # 유지보수 작업
├── inventory/               # Ansible 인벤토리
├── group_vars/              # 그룹 변수
├── scripts/                 # 유틸리티 스크립트
│   ├── bump-version.sh      # 버전 증가 스크립트
│   └── update-version.sh    # 버전 동기화 스크립트
├── docs/                    # 프로젝트 문서
├── tests/                   # 테스트 파일
├── Dockerfile               # Alpine Linux 기반 이미지
├── Makefile                 # 빌드 및 운영 자동화
├── pyproject.toml           # Python 프로젝트 설정
├── VERSION                  # 버전 정보 (Single Source of Truth)
└── CLAUDE.md                # AI 지원 문서 (한국어 우선)
```

## 개발 워크플로우

### 1. Feature 브랜치 생성

```bash
# 항상 feature 브랜치에서 작업
git checkout -b feature/your-feature-name
```

### 2. 개발 작업

```bash
# 코드 변경 후 테스트
make test

# 코드 포매팅
make format

# 린팅 검사
make lint
```

### 3. Docker 이미지 빌드 및 테스트

```bash
# 이미지 빌드
make build

# 컨테이너 실행 및 테스트
make run

# 이미지 크기 확인
make size
```

### 4. 버전 관리 및 릴리스

```bash
# 버전 증가 (개발 중)
make bump-patch  # 버그 수정: 0.0.1 → 0.0.2
make bump-minor  # 기능 추가: 0.0.1 → 0.1.0
make bump-major  # 주요 변경: 0.0.1 → 1.0.0

# 릴리스 준비 (자동 commit + tag)
make release-patch
make release-minor
make release-major

# 푸시
git push && git push --tags
```

## Makefile 타겟 가이드

### 🐳 컨테이너 관련

| 타겟 | 설명 | 사용 예시 |
|------|------|----------|
| `build` | Docker 이미지 빌드 (buildx 사용) | `make build` |
| `build-cache` | 캐시를 사용한 빌드 | `make build-cache` |
| `run` | 컨테이너 대화형 실행 | `make run` |
| `shell` | 실행 중인 컨테이너 쉘 접속 | `make shell` |
| `deploy` | Ceph 클러스터 배포 | `make deploy` |
| `validate` | 클러스터 검증 실행 | `make validate` |

### 📦 개발 환경

| 타겟 | 설명 | 사용 예시 |
|------|------|----------|
| `init` | 프로젝트 초기화 | `make init` |
| `install` | UV를 사용한 의존성 설치 | `make install` |
| `install-uv` | UV 패키지 매니저 설치 | `make install-uv` |
| `venv` | Python 가상환경 생성 | `make venv` |
| `deps` | 프로젝트 의존성 설치 | `make deps` |
| `deps-dev` | 개발 의존성 설치 | `make deps-dev` |

### 🔍 코드 품질

| 타겟 | 설명 | 사용 예시 |
|------|------|----------|
| `lint` | 코드 린팅 실행 | `make lint` |
| `format` | 코드 자동 포매팅 | `make format` |
| `test` | 테스트 스위트 실행 | `make test` |

### 📊 유틸리티

| 타겟 | 설명 | 사용 예시 |
|------|------|----------|
| `check-deps` | 설치된 의존성 확인 | `make check-deps` |
| `update-deps` | 의존성 업데이트 | `make update-deps` |
| `size` | Docker 이미지 크기 확인 | `make size` |
| `clean` | 캐시 및 임시 파일 정리 | `make clean` |
| `clean-docker` | Docker 리소스 정리 | `make clean-docker` |

### 🔢 버전 관리

| 타겟 | 설명 | 사용 예시 |
|------|------|----------|
| `version` | 현재 버전 표시 | `make version` |
| `bump-patch` | 패치 버전 증가 (0.0.x) | `make bump-patch` |
| `bump-minor` | 마이너 버전 증가 (0.x.0) | `make bump-minor` |
| `bump-major` | 메이저 버전 증가 (x.0.0) | `make bump-major` |
| `release-patch` | 패치 릴리스 (bump + commit + tag) | `make release-patch` |
| `release-minor` | 마이너 릴리스 | `make release-minor` |
| `release-major` | 메이저 릴리스 | `make release-major` |
| `tag` | 현재 버전으로 Git 태그 생성 | `make tag` |

### 🍎 macOS Container 전용

| 타겟 | 설명 | 사용 예시 |
|------|------|----------|
| `import-to-container` | Docker 이미지를 Container로 가져오기 | `make import-to-container` |
| `install-container-compose` | Container-Compose 설치 | `make install-container-compose` |
| `compose-up` | Container-Compose 서비스 시작 | `make compose-up` |
| `compose-down` | Container-Compose 서비스 중지 | `make compose-down` |

## 버전 관리

### VERSION 파일

`VERSION` 파일이 프로젝트의 버전 관리에서 **Single Source of Truth**로 작동합니다.

```bash
# 현재 버전 확인
cat VERSION
# 출력: 0.0.1
```

### 버전 변경 워크플로우

#### 자동화된 버전 변경

```bash
# 1. 버그 수정 (Patch Release)
make bump-patch
# VERSION: 0.0.1 → 0.0.2
# 자동 업데이트: pyproject.toml, Dockerfile, README.md

# 2. 새로운 기능 추가 (Minor Release)
make bump-minor
# VERSION: 0.0.2 → 0.1.0

# 3. 주요 변경/호환성 깨짐 (Major Release)
make bump-major
# VERSION: 0.1.0 → 1.0.0
```

#### 릴리스 워크플로우

```bash
# 개발 완료 후 릴리스
make release-patch  # 또는 release-minor, release-major

# 자동으로 수행되는 작업:
# 1. 버전 증가
# 2. 모든 파일 업데이트 (VERSION, pyproject.toml, Dockerfile, README.md)
# 3. Git commit 생성
# 4. Git tag 생성

# 수동으로 푸시
git push origin feature/your-feature
git push --tags
```

### 버전 관리 파일 동기화

VERSION 파일 변경 시 다음 파일들이 자동으로 업데이트됩니다:

- `pyproject.toml`: `version = "X.Y.Z"`
- `Dockerfile`: `ARG VERSION=X.Y.Z` 및 `LABEL version="X.Y.Z"`
- `README.md`: `**버전**: X.Y.Z`

## 테스트

### 로컬 테스트

```bash
# Python 테스트 실행
make test

# Ansible 플레이북 구문 검사
make lint
```

### Docker 컨테이너 테스트

```bash
# 이미지 빌드
make build

# 컨테이너에서 테스트 실행
make run
# 컨테이너 내부에서
ansible-playbook -i inventory/hosts-scalable.yml playbooks/04-validation/validate-all.yml
```

## 컨트리뷰션 가이드라인

### 코드 스타일

1. **Python 코드**: PEP 8 준수
   ```bash
   make format  # 자동 포매팅
   ```

2. **Ansible 플레이북**:
   - YAML 들여쓰기: 2 스페이스
   - 태스크 이름: 명확한 설명 포함
   - 변수: snake_case 사용

3. **Shell 스크립트**:
   - Bash 사용 (`#!/bin/bash`)
   - 에러 처리 포함
   - 명확한 주석 추가

### 커밋 메시지 형식

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포매팅
- `refactor`: 코드 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드 프로세스 등 기타 변경

**예시:**
```
feat: add RGW user management playbook

- Added playbooks/02-services/rgw-users.yml
- Supports creating multiple S3 users
- Includes quota configuration

Resolves: #123
```

### Pull Request 프로세스

1. **브랜치 생성**
   ```bash
   git checkout -b feature/description
   ```

2. **변경사항 커밋**
   ```bash
   git add .
   git commit -m "feat: your feature description"
   ```

3. **테스트 실행**
   ```bash
   make test
   make lint
   make build
   ```

4. **PR 생성**
   - 명확한 제목과 설명 작성
   - 관련 이슈 링크
   - 테스트 결과 포함

5. **코드 리뷰**
   - 리뷰어 피드백 반영
   - CI/CD 통과 확인

### 이슈 보고

버그 리포트나 기능 요청 시 다음 정보를 포함해주세요:

**버그 리포트:**
- 환경 정보 (OS, Docker/Container 버전)
- 재현 단계
- 예상 동작
- 실제 동작
- 로그 또는 에러 메시지

**기능 요청:**
- 사용 케이스 설명
- 제안하는 해결책
- 대안 고려사항

## 도움말 및 지원

- **문서**: [docs/](docs/) 디렉토리 참조
- **이슈**: [GitHub Issues](https://github.com/jerrydev88/ceph-automation-suite/issues)
- **토론**: [GitHub Discussions](https://github.com/jerrydev88/ceph-automation-suite/discussions)

## 라이선스

이 프로젝트는 Apache-2.0 라이선스 하에 배포됩니다. 기여하신 코드도 동일한 라이선스가 적용됩니다.