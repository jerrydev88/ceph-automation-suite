# 실제 환경 빠른 시작 가이드 (Real-World Quick Start)

이 가이드는 실제 프로젝트 파일(`hosts-scalable.yml`, `ceph-vars.yml`, `group_vars/all.yml`)을 기반으로 한 실전 워크플로우입니다.

## 📊 환경 구성

### 클러스터 토폴로지
- **Monitor/OSD/Manager 노드**: 3대 (mon1, mon2, mon3)
  - mon1 (10.10.2.91) - Bootstrap & Admin 노드
  - mon2 (10.10.2.92)
  - mon3 (10.10.2.93)
- **모든 노드가 MON, OSD, MGR, MDS 역할 수행** (Converged Infrastructure)
- **Ubuntu 24.04 LTS** with Ceph Squid (19.2.x)

### 스토리지 서비스 구성
- **CephFS**: fs-oa (MDS 1개)
- **RGW**: rgw-oa (S3 게이트웨이 1개)
- **RBD**: rbd-oa 풀 (Kubernetes용)
- **CSI 사용자**: Kubernetes 통합용

## 🚀 배포 옵션

### 옵션 1: 완전 자동화 배포 (권장) 🎯

한 줄의 명령으로 전체 클러스터를 자동 배포합니다:

```bash
# 전체 자동 배포 (Bootstrap 포함) - 새로운 경로
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml

# 또는 기존 경로 (deprecated)
# ansible-playbook -i hosts-scalable.yml complete-deployment.yml
```

이 플레이북은 다음을 자동으로 수행합니다:
1. Ubuntu 24.04 버그 수정
2. Preflight 실행
3. Bootstrap (자동화)
4. Post-Bootstrap 설정 (호스트 추가, OSD 배포)
5. 스토리지 서비스 구성 (CephFS, RGW, RBD)
6. RGW 사용자/버킷 생성
7. Kubernetes CSI 사용자 생성

### 옵션 2: 플레이북 기반 단계별 배포

각 단계를 플레이북으로 실행:

```bash
# Step 1: 사전 준비 및 Ubuntu 24.04 수정
# Ubuntu 24.04 버그 수정 (필요 시)
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/fix-ubuntu24.yml

# Preflight 실행 (원본 사용)
ansible-playbook -i hosts-scalable.yml cephadm-preflight.yml

# 디스크 준비 (필요 시 - 기존 파일시스템이 있는 경우)
# ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/prepare-disks.yml

# Step 2: Bootstrap (자동화된 플레이북)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/bootstrap.yml \
  -e dashboard_user=mocomsys \
  -e dashboard_password="mocomsys1$"

# Step 3: SSH 키 배포 (중요!)
# Ceph가 다른 호스트에 접근할 수 있도록 SSH 키 배포
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/distribute-ssh-key.yml \
  -e admin_node=mon1

# Step 4: Post-Bootstrap 설정 (호스트 추가, OSD 배포)
# FSID 저장
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/save-fsid.yml

# FSID 사용
FSID=$(cat current-cluster-fsid.txt)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/post-bootstrap.yml -e fsid=$FSID

# Step 5: 시간 동기화 (MON_CLOCK_SKEW 해결)
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/sync-time.yml

# Step 6: 스토리지 서비스 구성
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-global.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-cephfs.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rgw.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rbd.yml

# Step 7: RGW 사용자 및 버킷 생성
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-users.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-buckets.yml

# Step 8: Kubernetes CSI 사용자 생성
ansible-playbook -i hosts-scalable.yml playbooks/02-services/csi-users.yml
```

### 옵션 3: 수동 단계별 배포

전통적인 방식의 수동 실행:

#### Step 0: 사전 준비

```bash
# 프로젝트 클론
git clone https://github.com/ceph/cephadm-ansible.git
cd cephadm-ansible

# Python 가상환경 설정
python3 -m venv venv
source venv/bin/activate
pip install ansible netaddr

# sshpass 설치 (macOS)
brew install hudochenkov/sshpass/sshpass

# 또는 SSH 키 설정 (권장)
ssh-keygen -t rsa -N ""
for host in 10.10.2.91 10.10.2.92 10.10.2.93; do
  ssh-copy-id mocomsys@$host
done
```

#### Step 1: Ubuntu 24.04 사전 수정

```bash
# Ubuntu 24.04의 cephadm 패키지 버그 수정
ansible all -i hosts-scalable.yml -m file \
  -a "path=/var/lib/cephadm state=directory mode=0755" --become

# 또는 fix playbook 실행
ansible-playbook -i hosts-scalable.yml fix-cephadm-quick.yml
```

#### Step 2: Preflight 실행

```bash
# 모든 노드에 필요한 패키지 설치 및 준비
ansible-playbook -i hosts-scalable.yml cephadm-preflight.yml

# 실패 시 재시도
ansible-playbook -i hosts-scalable.yml cephadm-preflight.yml --start-at-task="install prerequisites packages"
```

#### Step 3: Ceph 클러스터 Bootstrap

```bash
# mon1 노드에 SSH 접속
ssh mocomsys@10.10.2.91

# Bootstrap 실행 (mon1에서)
sudo cephadm bootstrap \
  --mon-ip 10.10.2.91 \
  --initial-dashboard-user admin \
  --initial-dashboard-password P@ssw0rd123 \
  --dashboard-password-noupdate \
  --allow-fqdn-hostname

# 중요: Bootstrap 출력에서 다음 정보 저장
# - Dashboard URL: https://10.10.2.91:8443
# - Username: admin
# - Password: P@ssw0rd123
# - FSID: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

#### Step 4: SSH 키 배포

```bash
# Ceph SSH 키를 모든 호스트에 배포 (중요!)
ansible-playbook -i hosts-scalable.yml cephadm-distribute-ssh-key.yml \
  -e admin_node=mon1

# 또는 mon1에서 수동으로 배포
sudo ceph cephadm get-pub-key > ~/ceph.pub
ssh-copy-id -f -i ~/ceph.pub root@10.10.2.92
ssh-copy-id -f -i ~/ceph.pub root@10.10.2.93
```

#### Step 5: 추가 호스트 등록

```bash
# FSID 저장 (수동 bootstrap한 경우)
ansible-playbook -i hosts-scalable.yml save-current-fsid.yml

# mon1에서 추가 호스트 등록
sudo ceph orch host add ceph2 10.10.2.92
sudo ceph orch host add ceph3 10.10.2.93

# 라벨 추가 (역할 지정)
sudo ceph orch host label add ceph2 _admin
sudo ceph orch host label add ceph3 _admin

# 상태 확인
sudo ceph orch host ls
```

#### Step 6: OSD 배포

```bash
# 사용 가능한 디스크 확인
sudo ceph orch device ls

# OSD 자동 배포 (모든 사용 가능한 디스크)
sudo ceph orch apply osd --all-available-devices

# 또는 특정 디스크 지정
sudo ceph orch daemon add osd ceph1:/dev/sdb
sudo ceph orch daemon add osd ceph2:/dev/sdb
sudo ceph orch daemon add osd ceph3:/dev/sdb
```

#### Step 7: 스토리지 서비스 구성

```bash
# 전역 설정 적용
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-global.yml

# CephFS 구성 (fs-oa)
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-cephfs.yml

# RGW 구성 (rgw-oa)
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rgw.yml

# RBD 풀 구성 (rbd-oa)
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rbd.yml
```

#### Step 8: RGW 사용자 및 버킷 생성

```bash
# RGW 사용자 및 버킷 생성 (한 번에)
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-objects.yml

# 또는 개별 실행
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-users.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-buckets.yml

# 결과 확인
cat ceph-rgw-users-creation-results.csv
cat ceph-rgw-buckets-creation-results.txt
```

#### Step 9: Kubernetes CSI 사용자 생성

```bash
# CSI 사용자 생성 (csi-rbd-user, csi-rbd-admin)
ansible-playbook -i hosts-scalable.yml playbooks/02-services/csi-users.yml

# 결과 확인
cat ceph-csi-users-creation-results.txt
```

## 🔄 기존 클러스터 제거 및 재설치

기존 클러스터가 있는 경우 완전 제거 후 새로 설치:

```bash
# 완전 제거 후 자동 재설치 (새로운 디렉토리 구조)
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/purge-cluster.yml -e force_purge=true
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml

# 또는 기존 경로 (deprecated)
# ansible-playbook -i hosts-scalable.yml 00.purge-everything.yml -e force_purge=true
```

## 🔍 검증 및 모니터링

### 클러스터 상태 확인

```bash
# mon1에서 실행
sudo ceph -s
sudo ceph health detail
sudo ceph orch ls
sudo ceph osd tree
```

### 서비스별 확인

```bash
# CephFS
sudo ceph fs ls
sudo ceph fs status fs-oa

# RGW
sudo radosgw-admin user list
sudo ceph orch ls | grep rgw
curl http://10.10.2.91:80  # S3 endpoint 테스트

# RBD
sudo ceph osd pool ls
sudo rbd ls rbd-oa
```

### Dashboard 접속
```
URL: https://10.10.2.91:8443
Username: admin
Password: P@ssw0rd123
```

## 📝 중요 파일 구조

```
cephadm-ansible/
├── hosts-scalable.yml              # 인벤토리 (노드 정보)
├── ceph-vars.yml                   # Ceph 서비스 설정
├── group_vars/all.yml              # 전역 변수
├── cephadm-preflight.yml           # 사전 준비 (원본 유지)
│
├── playbooks/
│   ├── 00-preparation/             # 사전 준비
│   │   ├── fix-ubuntu24.yml        # Ubuntu 24.04 수정
│   │   ├── prepare-disks.yml       # 디스크 준비/zapping
│   │   ├── setup-root-ssh.yml      # Root SSH 설정 및 패스워드
│   │   └── add-gpg-keys.yml        # GPG 키 및 저장소 설정
│   │
│   ├── 01-deployment/              # 배포
│   │   ├── complete-deployment.yml # ⭐ 전체 자동 배포 (권장)
│   │   ├── bootstrap.yml           # Bootstrap 자동화
│   │   ├── distribute-ssh-key.yml  # SSH 키 배포 (중요!)
│   │   └── post-bootstrap.yml      # Post-Bootstrap 설정 (OSD 포함)
│   │
│   ├── 02-services/                # 서비스 구성
│   │   ├── configure-global.yml    # Ceph 전역 설정
│   │   ├── configure-cephfs.yml    # CephFS 구성
│   │   ├── configure-rgw.yml       # RGW 구성
│   │   ├── configure-rbd.yml       # RBD 구성
│   │   ├── rgw-objects.yml         # RGW 사용자 및 버킷 통합
│   │   ├── rgw-users.yml           # RGW 사용자 생성
│   │   ├── rgw-buckets.yml         # S3 버킷 생성
│   │   ├── csi-users.yml           # K8s CSI 사용자 생성
│   │   └── tasks/                  # Task include 파일
│   │       ├── rgw_user_creation.yml
│   │       └── rgw_bucket_creation.yml
│   │
│   ├── 03-operations/              # 운영
│   │   ├── save-fsid.yml           # FSID 저장
│   │   ├── sync-time.yml           # 시간 동기화 (MON_CLOCK_SKEW 해결)
│   │   ├── list-rbd-images.yml     # RBD 이미지 목록
│   │   ├── list-rbd-snapshots.yml  # RBD 스냅샷 목록
│   │   ├── create-rbd-snapshot.yml # RBD 스냅샷 생성
│   │   └── remove-rbd-snapshot.yml # RBD 스냅샷 제거
│   │
│   └── 90-maintenance/             # 유지보수
│       ├── purge-cluster.yml       # 클러스터 완전 제거
│       ├── undo-configure-osd.yml  # OSD 서비스 제거
│       ├── undo-configure-cephfs.yml # CephFS 제거
│       ├── undo-configure-rgw.yml  # RGW 제거
│       └── undo-configure-rbd.yml  # RBD 제거
│
└── [Legacy Files - To Be Removed]
    ├── complete-deployment.yml     # → playbooks/01-deployment/
    ├── bootstrap-wrapper.yml       # → playbooks/01-deployment/bootstrap.yml
    ├── 00.configure-global.yml     # → playbooks/02-services/configure-global.yml
    ├── 10.create-ceph-csi-client.yml # → playbooks/02-services/csi-users.yml
    ├── 30.create-rgw-objects.yml   # → playbooks/02-services/rgw-objects.yml
    ├── 30.1.rgw_user_creation.yml  # → playbooks/02-services/tasks/
    ├── 30.2.rgw_bucket_creation.yml # → playbooks/02-services/tasks/
    ├── 41.list-rbd-images.yml      # → playbooks/03-operations/
    ├── 41.list-rbd-snapshots.yml   # → playbooks/03-operations/
    ├── 42.create-rbd-snapshot.yml  # → playbooks/03-operations/
    ├── 49.remove-rbd-snapshot.yml  # → playbooks/03-operations/
    ├── 99.undo-configure-osd.yml   # → playbooks/90-maintenance/
    ├── enable-root-ssh-and-set-password.yml # → playbooks/00-preparation/setup-root-ssh.yml
    └── add-gpg-keys.yml            # → playbooks/00-preparation/
```

## 🎯 플레이북 기능 설명

### 자동화 플레이북

#### 배포 플레이북
- **`complete-deployment.yml`**: 전체 클러스터 배포를 한 번에 수행 (⭐ 권장)
- **`bootstrap.yml`**: cephadm bootstrap을 Ansible로 자동화
- **`distribute-ssh-key.yml`**: Ceph SSH 키를 모든 호스트에 배포 (bootstrap 후 필수!)
- **`post-bootstrap.yml`**: Bootstrap 후 호스트 추가, OSD 배포 자동화

#### 서비스 구성 플레이북
- **`configure-global.yml`**: Ceph 전역 설정 (mon_max_pg_per_osd 등)
- **`configure-cephfs.yml`**: CephFS 파일시스템 생성 및 MDS 배포
- **`configure-rgw.yml`**: RGW (S3/Swift) 게이트웨이 배포
- **`configure-rbd.yml`**: RBD 블록 스토리지 풀 생성 및 초기화
- **`rgw-objects.yml`**: RGW 사용자와 버킷을 한 번에 생성
- **`csi-users.yml`**: Kubernetes CSI를 위한 인증 사용자 생성

#### 운영 플레이북
- **`save-fsid.yml`**: 현재 실행 중인 클러스터의 FSID 저장
- **`sync-time.yml`**: 노드 간 시간 동기화 (MON_CLOCK_SKEW 해결)
- **`list-rbd-images.yml`**: 모든 풀의 RBD 이미지 목록 조회
- **`list-rbd-snapshots.yml`**: 특정 RBD 이미지의 스냅샷 목록 조회
- **`create-rbd-snapshot.yml`**: RBD 이미지 스냅샷 생성
- **`remove-rbd-snapshot.yml`**: RBD 이미지 스냅샷 삭제

#### 유지보수 플레이북
- **`purge-cluster.yml`**: 기존 클러스터 완전 제거
- **`undo-configure-osd.yml`**: OSD 서비스 제거
- **`undo-configure-cephfs.yml`**: CephFS 제거
- **`undo-configure-rgw.yml`**: RGW 서비스 제거
- **`undo-configure-rbd.yml`**: RBD 풀 제거

#### 준비 플레이북
- **`fix-ubuntu24.yml`**: Ubuntu 24.04 cephadm 버그 수정
- **`prepare-disks.yml`**: OSD용 디스크 준비 및 기존 파티션 제거
- **`setup-root-ssh.yml`**: Root 사용자 SSH 접속 및 패스워드 설정
- **`add-gpg-keys.yml`**: Ceph 및 Docker GPG 키와 저장소 추가

### 📌 Phase 1 정리 변경사항 (2025-09-23)

- **파일 확장자 통일**: 모든 `.yaml` 파일을 `.yml`로 변경
- **중복 제거**: `01.configure-osd.yaml` 제거 (기능이 `01.post-bootstrap-setup.yml`에 포함됨)
- **인벤토리 파일명 변경**: `hosts-scalable.yaml` → `hosts-scalable.yml`

### 📌 Phase 2 디렉토리 구조 개선 (2025-09-23) ✅ 완료!

**완료된 마이그레이션 (모든 플레이북 테스트 완료)**:

- **00-preparation**: fix-ubuntu24.yml, prepare-disks.yml, setup-root-ssh.yml, add-gpg-keys.yml
- **01-deployment**: complete-deployment.yml, bootstrap.yml, post-bootstrap.yml, distribute-ssh-key.yml
- **02-services**: configure-global.yml, configure-cephfs.yml, configure-rgw.yml, configure-rbd.yml, rgw-objects.yml, rgw-users.yml, rgw-buckets.yml, csi-users.yml
- **03-operations**: save-fsid.yml, sync-time.yml, list-rbd-images.yml, list-rbd-snapshots.yml, create-rbd-snapshot.yml, remove-rbd-snapshot.yml
- **90-maintenance**: purge-cluster.yml, undo-configure-osd.yml, undo-configure-cephfs.yml, undo-configure-rgw.yml, undo-configure-rbd.yml

**테스트 완료 항목**:

✅ Bootstrap 자동화 (변수 순환 참조 수정)
✅ Post-bootstrap 설정 (SSH 키 배포 → 호스트 추가 → OSD 배포)
✅ 시간 동기화 (MON_CLOCK_SKEW 해결)
✅ CephFS 구성 (fs-oa 생성 및 MDS 배포)
✅ RGW 구성 (rgw-oa 서비스 배포)
✅ RBD 구성 (rbd-oa 풀 생성 및 초기화)

**주요 수정사항**:

1. Bootstrap 변수 순환 참조 수정 (public_network → bootstrap_public_network)
2. 잘못된 --public-network 옵션 제거 (--cluster-network만 유효)
3. ansible_date_time → now() 함수로 변경
4. Ubuntu 24.04용 chrony 서비스명 수정 (chronyd → chrony)
5. 서비스 플레이북 vars 파일 경로 수정 (../../ceph-vars.yml)

### 📂 디렉토리 구조 개선 (완료)

**00-preparation 완료** ✅:

- `fix-cephadm-quick.yml` → `playbooks/00-preparation/fix-ubuntu24.yml`
- `zap-disks-for-osd.yml` → `playbooks/00-preparation/prepare-disks.yml`
- `cephadm-preflight.yml` → 원본 유지 (공식 프로젝트 파일)

**01-deployment 완료** ✅:
- `complete-deployment.yml` → `playbooks/01-deployment/complete-deployment.yml`
- `bootstrap-wrapper.yml` → `playbooks/01-deployment/bootstrap.yml`
- `01.post-bootstrap-setup.yml` → `playbooks/01-deployment/post-bootstrap.yml`

## ⚠️ 주의사항 및 최근 수정사항

### 1. **Ubuntu 24.04 특이사항**
   - cephadm 패키지 버그로 인해 `/var/lib/cephadm` 디렉토리 사전 생성 필요
   - Ceph Squid가 기본 포함되어 있음 (distro origin 사용)

### 2. **네트워크 구성**
   - 모든 노드 간 10.10.2.0/24 네트워크로 통신
   - 방화벽에서 필요한 포트 오픈 확인

### 3. **디스크 준비**
   - OSD용 디스크는 비어있어야 함
   - 기존 파티션이 있으면 `wipefs -a /dev/sdX` 실행

### 4. **플레이북 수정사항 (2025-09-23)**
   - **vars_files 경로 수정**: 모든 플레이북에서 `../../ceph-vars.yml` 형태로 상대 경로 수정
   - **delegate_to localhost 권한**: `become: false` 추가로 sudo 권한 문제 해결
   - **RGW realm 생성 추가**: `configure-rgw.yml`에 realm, zonegroup, zone 생성 단계 추가
   - **필수 Python 패키지**: `jmespath`, `boto3`, `botocore` 설치 필요

## 🔄 재시작 및 복구

### 전체 클러스터 재시작

```bash
# 모든 노드에서
sudo systemctl restart ceph.target
```

### 클러스터 제거 (주의!)

```bash
# FSID 확인 후 제거 (새로운 경로)
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/purge-cluster.yml \
  -e fsid=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# 또는 force_purge로 강제 제거
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/purge-cluster.yml \
  -e force_purge=true
```

## 🔧 트러블슈팅

### RGW 서비스 실패 문제
**증상**: RGW 서비스가 시작되지 않고 "failed to load realm" 오류 발생

**원인**: realm, zonegroup, zone이 생성되지 않은 상태에서 RGW 서비스 배치 시도

**해결**:
```bash
# RGW 설정 재실행 (realm 생성 포함)
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rgw.yml

# 서비스 재시작
ansible mon1 -i hosts-scalable.yml -b -m shell -a "systemctl restart ceph-*@rgw.*"
```

### Ansible 권한 문제
**증상**: "sudo: a password is required" 오류 발생

**원인**: delegate_to localhost 태스크에서 불필요한 sudo 권한 요구

**해결**: 해당 태스크에 `become: false` 추가

### 필수 Python 패키지 누락
**증상**: json_query 필터 오류, boto3 import 오류

**해결**:
```bash
source venv/bin/activate
pip install jmespath boto3 botocore
```

### MON_CLOCK_SKEW 경고
**증상**: Monitor 간 시간 동기화 문제

**해결**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/sync-time.yml
```

## 📊 프로덕션 체크리스트

- [ ] SSH 키 인증 설정 (패스워드 인증 대신)
- [ ] 방화벽 규칙 구성
- [ ] 네트워크 분리 (Public/Cluster network)
- [ ] OSD 디스크 준비 및 검증
- [ ] 모니터링 스택 활성화 (Prometheus/Grafana)
- [ ] 백업 전략 수립
- [ ] 성능 튜닝 (pg_num, pg_autoscale 등)
- [ ] Python 의존성 관리 (venv 사용)
- [ ] RGW realm/zone 설정 검증

---

*이 가이드는 실제 프로덕션 환경 배포를 위한 검증된 워크플로우입니다. (최종 업데이트: 2025-09-23)*