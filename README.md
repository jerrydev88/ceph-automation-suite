# Ceph Automation Suite

Ceph 클러스터 운영을 위한 고급 Ansible 플레이북 모음으로, cephadm-ansible을 확장한 커스텀 운영 워크플로우를 제공합니다.

## 📋 개요

Ceph Automation Suite는 다음과 같은 프로덕션 준비된 Ansible 플레이북을 제공합니다:
- 완전 자동화된 클러스터 배포
- 스토리지 서비스 구성 (CephFS, RGW, RBD)
- 운영 작업 및 유지보수
- 자동화된 검증 및 테스트
- Kubernetes 통합을 위한 CSI 사용자 관리

## 🔧 지원 버전 및 요구사항

### 호환성 매트릭스

| 구성요소 | 지원 버전 | 비고 |
|---------|----------|------|
| **Ceph** | Pacific (16.x), Quincy (17.x), Reef (18.x), Squid (19.x) | Reef 권장 |
| **cephadm-ansible** | 3.1.0+ | 필수 의존성 |
| **Ansible** | 2.9, 2.10, 2.11, 2.12, 2.13+ | 2.11+ 권장 |
| **Python** | 3.6, 3.7, 3.8, 3.9, 3.10+ | 3.8+ 권장 |

### 운영체제 지원

| OS | 버전 | 상태 | 비고 |
|----|------|------|------|
| **RHEL/CentOS** | 8.x | ✅ 완전 지원 | |
| **RHEL/Rocky/AlmaLinux** | 9.x | ✅ 완전 지원 | |
| **Ubuntu** | 20.04 LTS (Focal) | ✅ 완전 지원 | |
| **Ubuntu** | 22.04 LTS (Jammy) | ✅ 완전 지원 | |
| **Ubuntu** | 24.04 LTS (Noble) | ✅ 완전 지원 | fix-ubuntu24.yml 필요 |
| **Debian** | 11 (Bullseye) | ⚠️ 제한적 지원 | 테스트 필요 |

## 🚀 빠른 시작

### 전제 조건

#### 옵션 1: Docker 사용 (cephadm-ansible 포함)
```bash
# Docker/Container로 모든 의존성 자동 해결
make build
make run
```

#### 옵션 2: 로컬 설치
```bash
# cephadm-ansible 설치 (필수)
git clone https://github.com/ceph/cephadm-ansible.git
cd cephadm-ansible
pip install -r requirements.txt
```

#### 🍎 macOS 사용자를 위한 Container-Compose
```bash
# macOS 네이티브 container + Container-Compose 사용
make install-container-compose
container-compose up -d
```

### 설치

```bash
# 프로젝트 클론
git clone https://github.com/yourusername/ceph-automation-suite.git
cd ceph-automation-suite

# 의존성 설치
pip install -r requirements.txt

# 인벤토리 템플릿 복사
cp inventory/hosts-scalable.yml.example inventory/hosts-scalable.yml
```

### 사용법

#### 완전 자동화 배포

단일 명령으로 전체 Ceph 클러스터 배포:

```bash
ansible-playbook -i inventory/hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml
```

#### 서비스 구성

스토리지 서비스 구성:

```bash
# CephFS 파일시스템
ansible-playbook -i inventory/hosts-scalable.yml playbooks/02-services/configure-cephfs.yml

# RGW (S3 호환 객체 스토리지)
ansible-playbook -i inventory/hosts-scalable.yml playbooks/02-services/configure-rgw.yml

# RBD 블록 스토리지
ansible-playbook -i inventory/hosts-scalable.yml playbooks/02-services/configure-rbd.yml
```

#### 검증

자동화된 검증 실행:

```bash
ansible-playbook -i inventory/hosts-scalable.yml playbooks/04-validation/validate-all.yml
```

## 📁 프로젝트 구조

```
ceph-automation-suite/
├── playbooks/
│   ├── 00-preparation/     # 배포 전 준비 작업
│   ├── 01-deployment/       # 클러스터 배포
│   ├── 02-services/         # 서비스 구성
│   ├── 03-operations/       # 운영 작업
│   ├── 04-validation/       # 자동화 검증
│   └── 90-maintenance/      # 유지보수 작업
├── inventory/               # 인벤토리 설정
├── group_vars/              # 그룹 변수
├── docs/                    # 문서
└── roles/                   # 커스텀 Ansible 역할
```

## 📚 플레이북 카테고리

### 00-preparation (준비 작업)
- `fix-ubuntu24.yml` - Ubuntu 24.04 호환성 수정
- `configure-ansible-env.yml` - Ansible 환경 설정

### 01-deployment (배포)
- `complete-deployment.yml` - 전체 클러스터 자동 배포
- `bootstrap.yml` - 클러스터 초기 부트스트랩
- `post-bootstrap.yml` - 부트스트랩 후 구성
- `distribute-ssh-key.yml` - SSH 키 배포

### 02-services (서비스 구성)
- `configure-global.yml` - Ceph 전역 설정
- `configure-cephfs.yml` - CephFS 파일시스템 구성
- `configure-rgw.yml` - RGW (S3) 객체 스토리지 구성
- `configure-rbd.yml` - RBD 블록 스토리지 구성
- `csi-users.yml` - Kubernetes용 CSI 사용자 생성
- `rgw-users.yml` - RGW 사용자 관리
- `rgw-buckets.yml` - S3 버킷 관리

### 03-operations (운영 작업)
- `save-fsid.yml` - 클러스터 FSID 저장
- `sync-time.yml` - 시간 동기화
- `create-rbd-snapshot.yml` - RBD 스냅샷 생성
- `remove-rbd-snapshot.yml` - RBD 스냅샷 제거
- `list-rbd-images.yml` - RBD 이미지 목록 조회
- `list-rbd-snapshots.yml` - RBD 스냅샷 목록 조회

### 04-validation (검증)
- `validate-all.yml` - 전체 검증 스위트
- `validate-cluster-health.yml` - 클러스터 상태 검사
- `validate-cephfs.yml` - CephFS 검증
- `validate-rgw.yml` - RGW 검증
- `validate-rbd.yml` - RBD 검증
- `validate-csi-users.yml` - CSI 사용자 검증

### 90-maintenance (유지보수)
- `purge-cluster.yml` - 클러스터 완전 제거
- `undo-configure-cephfs.yml` - CephFS 구성 제거
- `undo-configure-rgw.yml` - RGW 구성 제거
- `undo-configure-rbd.yml` - RBD 구성 제거

## ⚙️ 구성 설정

### 인벤토리 구성

`inventory/hosts-scalable.yml` 편집:

```yaml
all:
  children:
    mons:
      hosts:
        mon1:
          ansible_host: 10.10.2.91
        mon2:
          ansible_host: 10.10.2.92
        mon3:
          ansible_host: 10.10.2.93
    osds:
      children:
        mons: {}  # Reuse monitor hosts as OSDs
    mgrs:
      children:
        mons: {}  # Reuse monitor hosts as managers
    admin:
      hosts:
        mon1: {}  # First monitor as admin node
```

### 서비스 구성

서비스 정의를 위해 `ceph-vars.yml` 편집:

```yaml
ceph:
  global:
    mon_max_pg_per_osd: 300
  cephfs:
    - name: fs-prod
      mds:
        count: 1
  rgw:
    - realm: default
      service_name: rgw-prod
      count: 1
  rbd:
    - pool_name: rbd-prod
      pool_pg_num: 16
  csi:
    - cluster_name: "k8s-prod"
      ceph_csi_user: "csi-rbd-user"
```

## 🔧 고급 사용법

### 사용자 정의 변수로 완전 배포

```bash
ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/01-deployment/complete-deployment.yml \
  -e dashboard_user=admin \
  -e dashboard_password="SecurePass123" \
  -e ceph_release=reef
```

### 선택적 실행

```bash
# 특정 호스트에서만 실행
ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/02-services/configure-cephfs.yml \
  --limit mons

# 특정 작업 건너뛰기
ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/01-deployment/complete-deployment.yml \
  --skip-tags preflight
```

### 사용자 정의 검사로 검증

```bash
# 특정 검증 실행
ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/04-validation/validate-cluster-health.yml \
  -e min_osds=3 \
  -e min_mons=3
```

## 📊 통합

### cephadm-ansible과 함께 사용

이 도구 모음은 cephadm-ansible을 다음과 같이 보완합니다:
1. cephadm-ansible preflight 및 bootstrap 실행
2. 커스텀 구성 및 운영을 위해 이 도구 모음 사용
3. 테스트를 위한 검증 플레이북 활용

### Kubernetes와 통합

Kubernetes를 위한 CSI 통합:

```bash
# CSI 사용자 생성
ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/02-services/csi-users.yml

# CSI 구성 검증
ansible-playbook -i inventory/hosts-scalable.yml \
  playbooks/04-validation/validate-csi-users.yml
```

## 🚨 문제 해결

### 일반적인 문제

1. **Ubuntu 24.04 호환성**
   ```bash
   ansible-playbook -i inventory/hosts-scalable.yml \
     playbooks/00-preparation/fix-ubuntu24.yml
   ```

2. **시간 동기화**
   ```bash
   ansible-playbook -i inventory/hosts-scalable.yml \
     playbooks/03-operations/sync-time.yml
   ```

3. **검증 실패**
   - 특정 검증 플레이북 출력 확인
   - `/var/log/ceph/`의 로그 검토
   - 실패한 컴포넌트에 대한 선택적 검증 실행

## 📝 문서

- [플레이북 문서](docs/playbooks/)
- [구성 가이드](docs/configuration/)
- [문제 해결 가이드](docs/operations/troubleshooting.md)
- [모범 사례](docs/development/best-practices.md)

## 🤝 기여하기

기여를 환영합니다! 다음 절차를 따라주세요:
1. 저장소 포크
2. 기능 브랜치 생성
3. 새 플레이북에 대한 테스트 추가
4. 풀 리퀘스트 제출

## 📄 라이선스

이 프로젝트는 Apache-2.0 라이선스로 배포됩니다.

## 🔗 관련 프로젝트

- [cephadm-ansible](https://github.com/ceph/cephadm-ansible) - Ansible을 사용한 핵심 Ceph 배포
- [Ceph](https://github.com/ceph/ceph) - 분산 스토리지 시스템
- [Rook](https://github.com/rook/rook) - Kubernetes 스토리지 오케스트레이션

## 💬 지원

- GitHub 이슈: [버그 신고 또는 기능 요청](https://github.com/yourusername/ceph-automation-suite/issues)
- 문서: [문서 읽기](docs/)

---

**버전**: 1.0.0
**마지막 업데이트**: 2025-09-24
**작성자**: Jerry (jerrydev@mocomsys.com)
**라이선스**: Apache-2.0

### 주요 기능
- ✅ 완전 자동화된 Ceph 클러스터 배포
- ✅ 프로덕션 준비된 검증 시스템
- ✅ Kubernetes CSI 통합 지원
- ✅ Ubuntu 24.04 LTS 완벽 지원
- ✅ 한국어 문서 제공