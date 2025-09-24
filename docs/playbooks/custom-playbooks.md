# 플레이북 상세 가이드

이 문서는 cephadm-ansible 프로젝트의 모든 플레이북을 상세히 설명합니다.

## 📁 플레이북 디렉토리 구조

플레이북은 기능별로 체계적으로 구조화되어 있습니다:

```
playbooks/
├── 00-preparation/     # 사전 준비 작업
├── 01-deployment/      # 클러스터 배포
├── 02-services/        # 스토리지 서비스 구성
├── 03-operations/      # 운영 작업
├── 04-validation/      # 검증 및 테스트
└── 90-maintenance/     # 유지보수 및 정리
```

---

## 🛠️ 00-preparation: 사전 준비

### fix-ubuntu24.yml

**목적**: Ubuntu 24.04 (Noble)의 cephadm 패키지 버그를 수정합니다.

**주요 작업**:
- `/var/lib/cephadm` 디렉토리 생성
- 필요한 권한 설정

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/fix-ubuntu24.yml
```

**사용 시기**: Ubuntu 24.04 환경에서 cephadm 설치 전

### prepare-disks.yml

**목적**: OSD용 디스크를 준비하고 기존 파티션을 제거합니다.

**주요 작업**:
- 디스크 파티션 정보 수집
- 기존 파일시스템 제거 (`wipefs`)
- GPT 테이블 초기화 (`sgdisk`)

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/prepare-disks.yml
```

**⚠️ 주의**: 모든 데이터가 영구적으로 삭제됩니다!

### setup-root-ssh.yml

**목적**: Root 사용자 SSH 접근을 활성화하고 패스워드를 설정합니다.

**주요 작업**:
- SSH 설정 파일 수정 (`PermitRootLogin yes`)
- Root 패스워드 설정
- SSH 서비스 재시작

**필수 파일**: `secret.yml` (ansible-vault로 암호화)

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/setup-root-ssh.yml --ask-vault-pass
```

### add-gpg-keys.yml

**목적**: Ceph 및 Docker GPG 키와 저장소를 추가합니다.

**주요 작업**:
- GPG 키 다운로드 및 설치
- APT 저장소 설정
- 패키지 목록 업데이트

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/add-gpg-keys.yml
```

---

## 🚀 01-deployment: 클러스터 배포

### complete-deployment.yml ⭐

**목적**: 전체 클러스터를 한 번에 자동 배포하는 메인 플레이북입니다.

**포함 작업**:
1. Ubuntu 24.04 수정 (필요 시)
2. Preflight 실행
3. Bootstrap 자동화
4. SSH 키 배포
5. Post-Bootstrap 설정
6. 모든 스토리지 서비스 구성
7. 사용자 및 CSI 설정

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml
```

**권장 사용법**: 신규 클러스터 구축 시 첫 번째 선택

### bootstrap.yml

**목적**: Ceph 클러스터 bootstrap을 Ansible로 자동화합니다.

**주요 작업**:
- 첫 번째 모니터 노드에서 `cephadm bootstrap` 실행
- Dashboard 사용자 및 패스워드 설정
- 필요한 변수 자동 구성

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/bootstrap.yml \
  -e dashboard_user=admin \
  -e dashboard_password="P@ssw0rd123"
```

### distribute-ssh-key.yml

**목적**: Ceph SSH 키를 모든 호스트에 배포합니다.

**주요 작업**:
- Admin 노드에서 Ceph 공개 키 추출
- 모든 노드의 root authorized_keys에 추가
- SSH 연결 테스트

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/distribute-ssh-key.yml \
  -e admin_node=mon1
```

**중요**: Bootstrap 후 반드시 실행해야 하는 필수 단계입니다.

### post-bootstrap.yml

**목적**: Bootstrap 후 호스트 추가 및 OSD 배포를 자동화합니다.

**주요 작업**:
- 추가 호스트를 클러스터에 등록
- 호스트 라벨 설정
- OSD 자동 배포
- 서비스 상태 확인

**실행 예제**:
```bash
# FSID는 save-fsid.yml로 미리 저장
FSID=$(cat current-cluster-fsid.txt)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/post-bootstrap.yml -e fsid=$FSID
```

---

## 🗄️ 02-services: 스토리지 서비스 구성

### configure-global.yml

**목적**: Ceph 클러스터의 전역 설정을 구성합니다.

**주요 작업**:
- `mon_max_pg_per_osd` 설정
- 기타 클러스터 전역 파라미터 조정

**변수 설정** (`ceph-vars.yml`):
```yaml
ceph:
  global:
    mon_max_pg_per_osd: 300
```

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-global.yml
```

### configure-cephfs.yml

**목적**: CephFS 파일시스템을 생성하고 MDS 서비스를 구성합니다.

**주요 작업**:
- CephFS 볼륨 생성
- MDS(Metadata Server) 서비스 배치
- 파일시스템 초기화

**변수 설정**:
```yaml
ceph:
  cephfs:
    - name: fs-oa
      mds:
        count: 1
```

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-cephfs.yml
```

### configure-rgw.yml

**목적**: RADOS Gateway (S3/Swift 호환) 서비스를 배포합니다.

**주요 작업**:
- Realm, zonegroup, zone 생성
- RGW 서비스 인스턴스 생성
- S3 엔드포인트 설정

**변수 설정**:
```yaml
ceph:
  rgw:
    - realm: default
      zonegroup: default
      zone: default
      service_name: rgw-oa
      count: 1
      gateway:
        s3_url: "http://10.10.2.91:80"
```

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rgw.yml
```

### configure-rbd.yml

**목적**: RBD(RADOS Block Device) 풀과 이미지를 구성합니다.

**주요 작업**:
- RBD 풀 생성
- 풀 초기화
- RBD 이미지 생성 (선택사항)

**변수 설정**:
```yaml
ceph:
  rbd:
    - pool_name: rbd-oa
      pool_pg_num: 16
      images: []
```

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rbd.yml
```

### rgw-objects.yml

**목적**: RGW 사용자와 S3 버킷을 통합 생성합니다.

**주요 작업**:
- `rgw-users.yml` 호출
- `rgw-buckets.yml` 호출

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-objects.yml
```

### rgw-users.yml

**목적**: RGW 사용자를 생성하고 액세스 키를 관리합니다.

**주요 작업**:
- 사용자 존재 여부 확인
- 신규 사용자 생성
- Access Key와 Secret Key 생성
- 사용자별 권한(caps) 설정
- CSV 파일로 결과 저장

**변수 설정**:
```yaml
ceph:
  rgw:
    - users:
        - user_id: "testuser"
          display_name: "Test User"
          email: "test@example.com"
          caps:
            - type: "buckets"
              perm: "read, write, delete"
```

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-users.yml
```

### rgw-buckets.yml

**목적**: S3 버킷을 생성하고 사용자에게 할당합니다.

**주요 작업**:
- CSV 파일에서 사용자 키 정보 읽기
- AWS S3 API를 통한 버킷 생성
- 버킷별 쿼터 설정

**변수 설정**:
```yaml
ceph:
  rgw:
    - users:
        - buckets:
            - name: "test-bucket"
              permissions: "read, write, delete"
              quota: "10GB"
```

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-buckets.yml
```

### csi-users.yml

**목적**: Kubernetes CSI 드라이버를 위한 Ceph 사용자를 생성합니다.

**주요 작업**:
- CSI 사용자 생성
- 적절한 권한(capabilities) 설정
- 키링 정보 파일로 내보내기

**변수 설정**:
```yaml
ceph:
  csi:
    - cluster_name: "k8sdev"
      ceph_csi_user: "csi-rbd-user"
      caps:
        mon: "profile rbd"
        osd: "profile rbd pool=rbd-oa"
        mgr: "profile rbd pool=rbd-oa"
```

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/02-services/csi-users.yml
```

---

## 🔧 03-operations: 운영 작업

### save-fsid.yml

**목적**: 현재 실행 중인 클러스터의 FSID를 저장합니다.

**주요 작업**:
- `ceph fsid` 명령 실행
- `current-cluster-fsid.txt` 파일에 저장

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/save-fsid.yml
```

### sync-time.yml

**목적**: 노드 간 시간 동기화를 수행합니다 (MON_CLOCK_SKEW 해결).

**주요 작업**:
- NTP/Chrony 서비스 확인
- 시간 동기화 강제 실행
- 서비스 재시작

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/sync-time.yml
```

### list-rbd-images.yml

**목적**: 모든 RBD 풀의 이미지 목록을 조회합니다.

**주요 작업**:
- 모든 풀 목록 조회
- 각 풀의 RBD 이미지 나열
- 결과 화면 출력

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/list-rbd-images.yml
```

### list-rbd-snapshots.yml

**목적**: RBD 이미지의 스냅샷 목록을 조회합니다.

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/list-rbd-snapshots.yml
```

### create-rbd-snapshot.yml

**목적**: 특정 RBD 이미지의 스냅샷을 생성합니다.

**필수 변수**:
- `rbd_image`: 대상 이미지 (예: `pool/image`)
- `snapshot_name`: 스냅샷 이름

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/create-rbd-snapshot.yml \
  -e rbd_image=rbd-oa/myimage \
  -e snapshot_name=backup-$(date +%Y%m%d)
```

### remove-rbd-snapshot.yml

**목적**: RBD 이미지의 스냅샷을 삭제합니다.

**필수 변수**:
- `rbd_image`: 대상 이미지
- `snapshot_name`: 삭제할 스냅샷 이름

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/remove-rbd-snapshot.yml \
  -e rbd_image=rbd-oa/myimage \
  -e snapshot_name=backup-20240101
```

---

## ✅ 04-validation: 검증 및 테스트

### validate-all.yml ⭐

**목적**: 전체 클러스터 검증을 자동으로 수행하는 메인 검증 플레이북입니다.

**포함 검증**:
1. 클러스터 상태 검증
2. OSD 구성 검증
3. CephFS 검증 (구성된 경우)
4. RGW 검증 (구성된 경우)
5. RBD 검증 (구성된 경우)
6. CSI 사용자 검증 (구성된 경우)
7. 최종 검증 리포트 생성

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-all.yml
```

**출력**: `/tmp/ceph-validation-report.txt` 파일에 전체 검증 리포트 저장

### validate-cluster-health.yml

**목적**: 기본 클러스터 상태를 검증합니다.

**주요 검증**:
- 클러스터 상태 (HEALTH_OK)
- 모니터 쿼럼 상태
- OSD 상태 (모든 OSD가 up이고 in 상태)
- MGR 서비스 상태

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-cluster-health.yml
```

### validate-osd-configuration.yml

**목적**: OSD 구성을 검증합니다.

**주요 검증**:
- OSD 서비스 실행 상태
- OSD 트리 구조
- 풀 상태
- PG 상태

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-osd-configuration.yml
```

### validate-cephfs.yml

**목적**: CephFS 구성을 검증합니다.

**주요 검증**:
- CephFS 볼륨 존재 확인
- MDS 서비스 실행 상태
- 파일시스템 상태 (active)
- 메타데이터 및 데이터 풀 상태

**변수 의존성**: `ceph.cephfs`가 정의된 경우에만 실행

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-cephfs.yml
```

### validate-rgw.yml

**목적**: RGW 서비스를 검증합니다.

**주요 검증**:
- RGW 서비스 실행 상태
- S3 엔드포인트 접근성
- 사용자 생성 결과 파일 존재
- RGW 사용자 목록

**변수 의존성**: `ceph.rgw`가 정의된 경우에만 실행

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rgw.yml
```

### validate-rbd.yml

**목적**: RBD 구성을 검증합니다.

**주요 검증**:
- RBD 풀 존재 확인
- 풀 응용 프로그램 태그
- RBD 이미지 목록 (구성된 경우)

**변수 의존성**: `ceph.rbd`가 정의된 경우에만 실행

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rbd.yml
```

### validate-rgw-buckets.yml

**목적**: RGW 버킷을 검증합니다.

**주요 검증**:
- 버킷 생성 결과 파일 존재
- 실제 버킷 목록과 설정 일치 확인

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rgw-buckets.yml
```

### validate-rbd-snapshots.yml

**목적**: RBD 스냅샷을 검증합니다.

**주요 검증**:
- 스냅샷 목록 조회
- 스냅샷 상태 확인

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rbd-snapshots.yml
```

### validate-csi-users.yml

**목적**: CSI 사용자를 검증합니다.

**주요 검증**:
- CSI 사용자 존재 확인
- 사용자 권한(capabilities) 검증
- 키 파일 존재 및 내용 확인
- 인증 테스트

**변수 의존성**: `ceph.csi`가 정의된 경우에만 실행

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-csi-users.yml
```

---

## 🔄 90-maintenance: 유지보수 및 정리

### purge-cluster.yml

**목적**: 기존 클러스터를 완전히 제거합니다.

**주요 작업**:
1. 사용자 확인 프롬프트
2. 모든 Ceph 서비스 중지
3. 데이터 디렉토리 삭제
4. 패키지 제거 (선택사항)
5. 시스템 정리

**실행 예제**:
```bash
# FSID 지정 제거
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/purge-cluster.yml \
  -e fsid=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx

# 강제 제거
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/purge-cluster.yml \
  -e force_purge=true
```

**⚠️ 주의**: 모든 데이터가 영구적으로 삭제됩니다!

### undo-configure-rbd.yml

**목적**: RBD 구성을 완전히 제거합니다.

**주요 작업**:
1. 사용자 확인 프롬프트
2. `mon_allow_pool_delete` 활성화
3. RBD 이미지 삭제
4. RBD 풀 삭제
5. `mon_allow_pool_delete` 비활성화

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-rbd.yml
```

### undo-configure-rgw.yml

**목적**: RGW 서비스를 제거합니다.

**주요 작업**:
1. 사용자 확인 프롬프트
2. RGW 서비스 인스턴스 제거
3. 관련 데이터 정리

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-rgw.yml
```

### undo-configure-cephfs.yml

**목적**: CephFS 볼륨을 제거합니다.

**주요 작업**:
1. 사용자 확인 프롬프트
2. `mon_allow_pool_delete` 활성화
3. CephFS 볼륨 삭제
4. 관련 풀 제거
5. `mon_allow_pool_delete` 비활성화

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-cephfs.yml
```

### undo-configure-osd.yml

**목적**: OSD 구성을 롤백합니다.

**현재 상태**: 기본 구조만 제공, 필요시 확장 가능

**실행 예제**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-osd.yml
```

---

## 📊 권장 실행 순서

### 신규 클러스터 구축

```bash
# 방법 1: 완전 자동화 (권장)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml

# 방법 2: 단계별 실행
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/fix-ubuntu24.yml  # Ubuntu 24.04만
ansible-playbook -i hosts-scalable.yml cephadm-preflight.yml
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/bootstrap.yml
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/distribute-ssh-key.yml
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/save-fsid.yml
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/post-bootstrap.yml -e fsid=$(cat current-cluster-fsid.txt)
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-global.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-cephfs.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rgw.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rbd.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/csi-users.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-users.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-buckets.yml
```

### 검증 및 테스트

```bash
# 전체 검증
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-all.yml

# 개별 검증
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-cluster-health.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-cephfs.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rgw.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rbd.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-csi-users.yml
```

### 클러스터 제거 (역순)

```bash
# 서비스 제거
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-rbd.yml
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-rgw.yml
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-cephfs.yml

# 전체 클러스터 제거
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/purge-cluster.yml -e force_purge=true
```

---

## ⚠️ 주의사항 및 모범 사례

### 일반 원칙

1. **변수 파일 확인**: 실행 전 `ceph-vars.yml` 설정 검토
2. **검증 습관화**: 배포 후 항상 `validate-all.yml` 실행
3. **백업 우선**: 중요한 변경 전 데이터 백업
4. **단계적 접근**: 프로덕션에서는 단계별 배포 고려
5. **로그 모니터링**: 실행 중 에러 메시지 주의 깊게 확인

### 환경별 고려사항

**개발 환경**:
- `complete-deployment.yml` 사용 권장
- 빠른 테스트를 위한 간소화된 구성

**스테이징 환경**:
- 단계별 배포로 검증 포인트 확보
- 프로덕션 환경과 동일한 절차 적용

**프로덕션 환경**:
- 단계별 배포 필수
- 각 단계마다 검증 수행
- 백업 및 롤백 계획 수립

### 트러블슈팅

**일반적인 문제**:
1. **SSH 키 문제**: `distribute-ssh-key.yml` 재실행
2. **시간 동기화**: `sync-time.yml` 실행
3. **권한 문제**: 플레이북에서 `become: false` 확인
4. **파일 경로 문제**: 절대 경로 사용 확인

**디버깅 방법**:
```bash
# Dry-run 모드
ansible-playbook --check playbook.yml

# 상세 출력
ansible-playbook -vvv playbook.yml

# 특정 태스크부터 시작
ansible-playbook --start-at-task="태스크명" playbook.yml
```

---

*이 문서는 cephadm-ansible 프로젝트의 모든 플레이북에 대한 완전한 가이드입니다. 각 플레이북의 소스 코드는 해당 디렉토리에서 확인할 수 있습니다.*