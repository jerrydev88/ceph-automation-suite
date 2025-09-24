# 빠른 시작 가이드

이 가이드는 cephadm-ansible을 사용하여 첫 번째 Ceph 클러스터를 빠르게 구축하는 방법을 안내합니다.

## 📋 전제 조건

### 시스템 요구사항

- **운영체제**: RHEL 8/9, CentOS 8/9, Ubuntu 20.04/22.04/24.04
- **Python**: 3.6 이상
- **Ansible**: 2.9 이상
- **네트워크**: 모든 노드 간 통신 가능
- **디스크**: OSD용 추가 디스크 (최소 1개)

### 노드 준비

최소한 다음 노드들이 필요합니다:
- Monitor 노드: 1개 이상 (권장: 3개)
- OSD 노드: 1개 이상 (권장: 3개)
- 관리 노드: 1개 (보통 첫 번째 모니터 노드)

## 🚀 빠른 설정 방법

### 방법 1: 완전 자동화 배포 (⭐ 권장)

한 줄의 명령으로 전체 클러스터를 자동 배포합니다:

```bash
# 프로젝트 클론 및 준비
git clone https://github.com/ceph/cephadm-ansible.git
cd cephadm-ansible

# Python 가상환경 설정
python3 -m venv venv
source venv/bin/activate
pip install ansible netaddr

# 전체 자동 배포 (Bootstrap 포함)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml
```

### 방법 2: 단계별 플레이북 배포

각 단계를 개별 플레이북으로 실행:

```bash
# 1. 사전 준비
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/fix-ubuntu24.yml  # Ubuntu 24.04인 경우
ansible-playbook -i hosts-scalable.yml cephadm-preflight.yml

# 2. 클러스터 배포
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/bootstrap.yml \
  -e dashboard_user=admin \
  -e dashboard_password="P@ssw0rd123"

# SSH 키 배포 (중요!)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/distribute-ssh-key.yml \
  -e admin_node=mon1

# FSID 저장 및 Post-Bootstrap
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/save-fsid.yml
FSID=$(cat current-cluster-fsid.txt)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/post-bootstrap.yml -e fsid=$FSID

# 3. 스토리지 서비스 구성
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-global.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-cephfs.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rgw.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rbd.yml

# 4. 사용자 및 CSI 설정
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-users.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/rgw-buckets.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/csi-users.yml
```

## 📂 인벤토리 파일 준비

`hosts-scalable.yml` 파일을 생성하고 다음과 같이 구성합니다:

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
        mons: {}  # 모니터 호스트를 OSD로도 사용
    mgrs:
      children:
        mons: {}  # 모니터 호스트를 매니저로도 사용
    admin:
      hosts:
        mon1: {}  # 첫 번째 모니터를 관리 노드로 사용
```

전역 변수는 `group_vars/all.yml`에 별도로 구성:

```yaml
# group_vars/all.yml
ansible_ssh_user: mocomsys
ansible_ssh_pass: mocomsys
ceph_release: reef
ceph_origin: community

# Ubuntu 버전 매핑
ubuntu_ceph_repo_mapping:
  noble: jammy    # 24.04
  mantic: jammy   # 23.10
  jammy: jammy    # 22.04
  focal: focal    # 20.04

ceph_stable_release_deb: "{{ ubuntu_ceph_repo_mapping[ansible_distribution_release] | default('jammy') }}"
```

## 📝 서비스 구성 파일

`ceph-vars.yml` 파일로 Ceph 서비스를 구성합니다:

```yaml
ceph:
  global:
    mon_max_pg_per_osd: 300
  cephfs:
    - name: fs-oa
      mds:
        count: 1
  rgw:
    - realm: default
      zonegroup: default
      zone: default
      service_name: rgw-oa
      count: 1
      gateway:
        s3_url: "http://10.10.2.91:80"
      users:
        - user_id: "testuser"
          display_name: "Test User"
          email: "test@example.com"
          buckets:
            - name: "test-bucket"
              permissions: "read, write, delete"
              quota: "10GB"
  rbd:
    - pool_name: rbd-oa
      pool_pg_num: 16
      images: []
  csi:
    - cluster_name: "k8sdev"
      ceph_csi_user: "csi-rbd-user"
      caps:
        mon: "profile rbd"
        osd: "profile rbd pool=rbd-oa"
        mgr: "profile rbd pool=rbd-oa"
```

## 🔍 상태 확인 및 검증

### 클러스터 상태 확인

```bash
# mon1 노드에서 실행
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

# CSI 사용자
sudo ceph auth list | grep csi
```

### 자동 검증 실행

전체 클러스터 검증을 자동으로 수행:

```bash
# 모든 서비스 검증
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-all.yml

# 개별 서비스 검증
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-cluster-health.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-cephfs.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rgw.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rbd.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-csi-users.yml
```

### Dashboard 접속

```text
URL: https://10.10.2.91:8443
Username: admin
Password: P@ssw0rd123
```

## ⚙️ 고급 구성 옵션

### 특정 호스트 그룹 타겟팅

```bash
# 모니터 노드만 타겟
ansible-playbook -i hosts-scalable.yml cephadm-preflight.yml --limit mons

# 특정 노드만 타겟
ansible-playbook -i hosts-scalable.yml cephadm-preflight.yml --limit mon1
```

### 서비스별 개별 구성

```bash
# 개별 서비스 구성
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-cephfs.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rgw.yml
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rbd.yml

# 개별 서비스 제거
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-cephfs.yml
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-rgw.yml
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/undo-configure-rbd.yml
```

## 🚨 일반적인 문제 해결

### 1. Ubuntu 24.04 관련 문제

```bash
# cephadm 디렉토리 생성 오류
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/fix-ubuntu24.yml

# 또는 수동으로
ansible all -i hosts-scalable.yml -m file -a "path=/var/lib/cephadm state=directory mode=0755" --become
```

### 2. SSH 연결 실패

```bash
# SSH 키 생성 및 배포
ssh-keygen -t rsa -N ""
for host in 10.10.2.91 10.10.2.92 10.10.2.93; do
  ssh-copy-id mocomsys@$host
done
```

### 3. Python 의존성 문제

```bash
# 필요한 Python 패키지 설치
source venv/bin/activate
pip install ansible netaddr jmespath boto3 botocore
```

### 4. 클러스터 완전 제거

```bash
# 기존 클러스터 완전 제거
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/purge-cluster.yml -e force_purge=true
```

### 5. MON_CLOCK_SKEW 경고

```bash
# 시간 동기화 문제 해결
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/sync-time.yml
```

## 🔄 운영 작업

### 스냅샷 관리

```bash
# RBD 스냅샷 생성
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/create-rbd-snapshot.yml \
  -e rbd_image=rbd-oa/myimage \
  -e snapshot_name=backup-$(date +%Y%m%d)

# RBD 스냅샷 제거
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/remove-rbd-snapshot.yml \
  -e rbd_image=rbd-oa/myimage \
  -e snapshot_name=backup-20240101

# RBD 이미지 및 스냅샷 목록
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/list-rbd-images.yml
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/list-rbd-snapshots.yml
```

## 📚 다음 학습 단계

- [실제 환경 빠른 시작](./real-world-quickstart.md) - 상세한 실전 워크플로우
- [기본 개념](./concepts.md) - 핵심 용어와 개념 이해
- [플레이북 가이드](../playbooks/custom-playbooks.md) - 모든 플레이북 상세 설명
- [구성 관리](../configuration/central-config.md) - 고급 구성 옵션
- [운영 가이드](../operations/troubleshooting.md) - 일상 운영 작업

## 💡 팁과 모범 사례

1. **완전 자동화 배포 사용**: `complete-deployment.yml` 플레이북 권장
2. **검증 플레이북 활용**: 배포 후 항상 `validate-all.yml` 실행
3. **변경 전 백업**: 중요한 변경 전 백업 수행
4. **단계적 배포**: 프로덕션에서는 단계별 배포 고려
5. **로그 모니터링**: `/var/log/ceph/` 디렉토리 정기 확인

---

*이 빠른 시작 가이드는 기본적인 Ceph 클러스터 구축을 안내합니다. 더 상세한 내용은 [실제 환경 빠른 시작 가이드](./real-world-quickstart.md)를 참조하세요.*