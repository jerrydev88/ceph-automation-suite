# macOS Native Container 사용 가이드

## 개요

macOS Sequoia (15.0+) 또는 Xcode 16+에서 제공하는 네이티브 `container` CLI를 사용하여 Docker Desktop 없이 컨테이너를 실행하는 방법입니다.

### 🎉 Container-Compose 지원!

이제 [Container-Compose](https://github.com/Mcrich23/Container-Compose)를 사용하여 Docker Compose와 동일한 방식으로 오케스트레이션할 수 있습니다!

## 🍎 장점

- **네이티브 성능**: Virtualization.framework 직접 사용
- **리소스 효율적**: Docker Desktop보다 훨씬 가벼움
- **무료**: 라이선스 비용 없음
- **통합**: macOS와 완벽한 통합

## 📋 요구사항

- macOS Sequoia 15.0+ 또는
- Xcode 16+ Command Line Tools
- Apple Silicon (M1/M2/M3) 또는 Intel Mac

## 🚀 빠른 시작

### 1. container CLI 확인

```bash
# 설치 확인
container --version

# 설치되지 않은 경우
xcode-select --install
```

### 2. Container-Compose 설치 (선택사항, 권장)

```bash
# 자동 설치
make install-container-compose

# 또는 수동 설치
brew tap mcrich23/container-compose
brew install container-compose
```

### 3. 이미지 빌드

```bash
# 스크립트 사용
./scripts/macos-container-build.sh

# 또는 직접 빌드
container build -t ceph-automation-suite:latest .
```

### 4. 컨테이너 실행

#### Container-Compose 사용 (권장)

```bash
# 서비스 시작
container-compose up -d

# 대화형 쉘
container-compose run --rm ceph-automation bash

# 서비스 중지
container-compose down
```

#### 직접 실행

```bash
# 대화형 쉘
./scripts/macos-container-run.sh

# 또는 직접 실행
container run -it \
  -v ~/ceph-automation/inventory:/opt/ceph-automation/inventory \
  -v ~/.ssh:/home/ansible/.ssh:ro \
  ceph-automation-suite:latest \
  bash
```

## 📖 기본 명령어

### 이미지 관리

```bash
# 이미지 목록
container images

# 이미지 빌드
container build -t <이미지명>:<태그> .

# 이미지 삭제
container images rm <이미지ID>

# 이미지 정보
container images inspect <이미지ID>
```

### 컨테이너 관리

```bash
# 컨테이너 실행
container run [옵션] <이미지> [명령]

# 실행 중인 컨테이너 목록
container list

# 모든 컨테이너 목록
container list --all

# 컨테이너 시작/중지
container start <컨테이너ID>
container stop <컨테이너ID>

# 컨테이너 삭제
container rm <컨테이너ID>

# 컨테이너 로그
container logs <컨테이너ID>

# 실행 중인 컨테이너에 명령 실행
container exec <컨테이너ID> <명령>
```

### 볼륨 관리

```bash
# 볼륨 생성
container volume create <볼륨명>

# 볼륨 목록
container volume list

# 볼륨 삭제
container volume rm <볼륨명>

# 볼륨 정보
container volume inspect <볼륨명>
```

### 네트워크 관리

```bash
# 네트워크 생성
container network create <네트워크명>

# 네트워크 목록
container network list

# 네트워크 삭제
container network rm <네트워크명>

# 네트워크 정보
container network inspect <네트워크명>
```

## 🎯 Ceph Automation Suite 실행

### 완전 배포

```bash
# 컨테이너로 Ansible 플레이북 실행
container run --rm \
  -v $(pwd)/inventory:/opt/ceph-automation/inventory \
  -v ~/.ssh:/home/ansible/.ssh:ro \
  ceph-automation-suite:latest \
  ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/01-deployment/complete-deployment-docker.yml
```

### 검증 실행

```bash
container run --rm \
  -v $(pwd)/inventory:/opt/ceph-automation/inventory \
  ceph-automation-suite:latest \
  ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/04-validation/validate-all.yml
```

### 대화형 디버깅

```bash
# 컨테이너에 쉘 접속
container run -it --rm \
  -v $(pwd)/inventory:/opt/ceph-automation/inventory \
  -v ~/.ssh:/home/ansible/.ssh:ro \
  --name ceph-debug \
  ceph-automation-suite:latest \
  bash

# 다른 터미널에서 실행 중인 컨테이너에 접속
container exec -it ceph-debug bash
```

## 🔧 고급 사용법

### 환경 변수 설정

```bash
container run \
  -e ANSIBLE_VERBOSITY=3 \
  -e ANSIBLE_HOST_KEY_CHECKING=False \
  ceph-automation-suite:latest
```

### 포트 매핑

```bash
# Ceph Dashboard 포트 노출 (예시)
container run -p 8443:8443 ceph-automation-suite:latest
```

### 리소스 제한

```bash
# CPU와 메모리 제한 (container CLI가 지원하는 경우)
container run \
  --cpus="2.0" \
  --memory="2g" \
  ceph-automation-suite:latest
```

## 🆚 Docker와의 차이점

| 기능 | Docker | macOS Container | Container-Compose |
|-----|--------|-----------------|-------------------|
| 명령어 | `docker` | `container` | `container-compose` |
| 이미지 빌드 | `docker build` | `container build` | `container-compose build` |
| 컨테이너 실행 | `docker run` | `container run` | `container-compose run` |
| Compose 지원 | ✅ Docker Compose | ❌ 네이티브 미지원 | ✅ Container-Compose |
| 레지스트리 | Docker Hub | 로컬 또는 사설 | 로컬 또는 사설 |
| 리소스 사용 | 높음 | 낮음 | 낮음 |
| YAML 파일 | docker-compose.yml | - | container-compose.yml |

## 🐛 문제 해결

### container 명령을 찾을 수 없음

```bash
# Xcode Command Line Tools 설치
xcode-select --install

# 또는 Xcode 설치 후
sudo xcode-select -s /Applications/Xcode.app
```

### 권한 오류

```bash
# 사용자를 container 그룹에 추가 (필요한 경우)
sudo dseditgroup -o edit -a $(whoami) -t user container
```

### 볼륨 마운트 실패

```bash
# 절대 경로 사용
container run -v $(pwd)/data:/data ...

# 권한 확인
ls -la ~/path/to/mount
```

## 📚 참고 자료

- [Apple Developer - Container](https://developer.apple.com/documentation/)
- [Virtualization.framework](https://developer.apple.com/documentation/virtualization)

## 💡 팁

1. **별칭 설정**: Docker 명령어에 익숙하다면 별칭 사용
   ```bash
   alias docker='container'
   alias docker-compose='echo "Use container directly"'
   ```

2. **스크립트 활용**: 제공된 스크립트로 복잡한 명령 단순화
   ```bash
   ./scripts/macos-container-build.sh
   ./scripts/macos-container-run.sh
   ```

3. **이미지 캐싱**: 빌드 시간 단축을 위해 레이어 캐싱 활용

4. **로그 모니터링**: 별도 터미널에서 로그 확인
   ```bash
   container logs -f <컨테이너ID>
   ```