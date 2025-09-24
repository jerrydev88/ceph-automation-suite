# Docker를 사용한 Ceph Automation Suite 실행

## 개요

이 문서는 cephadm-ansible 의존성을 Docker 컨테이너로 격리하여 Ceph Automation Suite를 실행하는 방법을 설명합니다.

## 장점

- **의존성 격리**: cephadm-ansible과 모든 Python 패키지를 컨테이너에 격리
- **버전 관리**: cephadm-ansible 버전을 고정하여 일관된 실행 환경 보장
- **로컬 환경 보호**: 호스트 시스템에 패키지 설치 불필요
- **쉬운 배포**: Docker만 있으면 어디서든 실행 가능

## 빠른 시작

### 1. Docker 이미지 빌드

```bash
docker-compose build
```

### 2. 인벤토리 파일 준비

```bash
cp inventory/hosts-scalable.yml.example inventory/hosts-scalable.yml
# inventory/hosts-scalable.yml 편집하여 실제 호스트 정보 입력
```

### 3. SSH 키 설정

Docker 컨테이너는 호스트의 `~/.ssh` 디렉토리를 읽기 전용으로 마운트합니다.
대상 호스트들에 SSH 키 기반 인증이 설정되어 있어야 합니다.

### 4. 배포 실행

#### 대화형 쉘 시작
```bash
docker-compose run --rm ceph-automation bash
```

#### 직접 플레이북 실행
```bash
# 전체 배포 (Docker 버전)
docker-compose run --rm ceph-automation \
  ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/01-deployment/complete-deployment-docker.yml

# 검증 실행
docker-compose run --rm ceph-automation \
  ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/04-validation/validate-all.yml
```

## 상세 사용법

### Docker Compose 명령어

```bash
# 컨테이너 시작 (대화형 모드)
docker-compose run --rm ceph-automation bash

# 백그라운드 실행
docker-compose up -d

# 실행 중인 컨테이너 접속
docker-compose exec ceph-automation bash

# 로그 확인
docker-compose logs -f

# 컨테이너 중지 및 제거
docker-compose down
```

### Ansible 명령어 실행

컨테이너 내부에서:
```bash
# 플레이북 실행
ansible-playbook -i inventory/hosts-scalable.yml playbooks/[플레이북].yml

# 특정 태그만 실행
ansible-playbook -i inventory/hosts-scalable.yml playbooks/[플레이북].yml --tags "tag1,tag2"

# Dry run
ansible-playbook -i inventory/hosts-scalable.yml playbooks/[플레이북].yml --check

# Verbose 모드
ansible-playbook -i inventory/hosts-scalable.yml playbooks/[플레이북].yml -vvv
```

### 볼륨 마운트

docker-compose.yml에서 마운트되는 디렉토리:

| 호스트 경로 | 컨테이너 경로 | 용도 | 모드 |
|------------|--------------|------|------|
| `./inventory` | `/opt/ceph-automation/inventory` | 인벤토리 파일 | RO |
| `~/.ssh` | `/root/.ssh` | SSH 키 | RO |
| `./logs` | `/var/log/ansible` | 로그 저장 | RW |
| `./ceph-vars.yml` | `/opt/ceph-automation/ceph-vars.yml` | 변수 파일 | RO |

### 환경 변수

Docker 컨테이너에 설정된 환경 변수:

- `ANSIBLE_HOST_KEY_CHECKING=False`
- `ANSIBLE_GATHERING=smart`
- `ANSIBLE_FACT_CACHING=jsonfile`
- `ANSIBLE_STDOUT_CALLBACK=yaml`

추가 환경 변수가 필요한 경우 docker-compose.yml의 `environment` 섹션에 추가

## 문제 해결

### 1. SSH 연결 실패

```bash
# 컨테이너 내부에서 SSH 연결 테스트
docker-compose run --rm ceph-automation bash
ssh mocomsys@10.10.2.91
```

### 2. 권한 문제

```bash
# SSH 키 권한 확인
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
```

### 3. cephadm-ansible 버전 변경

Dockerfile에서 특정 버전 지정:
```dockerfile
RUN git clone --branch v3.1.0 https://github.com/ceph/cephadm-ansible.git /opt/cephadm-ansible
```

### 4. 네트워크 연결 문제

대상 호스트와 같은 네트워크에 있어야 하는 경우:
```yaml
# docker-compose.yml에서
network_mode: host  # bridge 대신 host 네트워크 사용
```

## 기존 방식과의 차이점

| 항목 | 기존 방식 | Docker 방식 |
|-----|----------|------------|
| cephadm-ansible 설치 | 수동 클론 필요 | Docker 이미지에 포함 |
| Python 패키지 | 호스트에 설치 | 컨테이너에 격리 |
| 플레이북 경로 | `../../cephadm-preflight.yml` | `/opt/cephadm-ansible/cephadm-preflight.yml` |
| 실행 명령 | `ansible-playbook` | `docker-compose run ceph-automation ansible-playbook` |

## 고급 설정

### 사용자 정의 이미지 빌드

특정 버전이나 추가 도구가 필요한 경우:

```dockerfile
# Dockerfile.custom
FROM ceph-automation-suite:latest

# 추가 도구 설치
RUN apt-get update && apt-get install -y \
    jq \
    kubectl \
    && rm -rf /var/lib/apt/lists/*
```

### 다중 환경 관리

```bash
# 개발 환경
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# 운영 환경
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up
```

## 보안 고려사항

1. **SSH 키**: 읽기 전용으로 마운트되며, 컨테이너 내부에서 수정 불가
2. **시크릿 관리**: secret.yml 파일은 Git에 커밋하지 않음
3. **네트워크 격리**: 기본적으로 bridge 네트워크 사용
4. **권한 제한**: 컨테이너는 root로 실행되지만, 호스트 파일 시스템 접근 제한

## 라이선스

Apache-2.0 라이선스