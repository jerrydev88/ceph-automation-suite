# 01-deployment - 클러스터 배포 플레이북

이 디렉토리는 Ceph 클러스터 배포와 초기 설정을 위한 플레이북을 포함합니다.

## 플레이북 목록

### complete-deployment.yml

- **목적**: 전체 클러스터를 한 번에 자동 배포 (가장 권장)
- **원본**: `complete-deployment.yml`
- **기능**:
  - Ubuntu 24.04 버그 수정
  - Preflight 실행
  - Bootstrap 자동화
  - Post-Bootstrap 설정
  - 스토리지 서비스 구성
  - RGW 사용자/버킷 생성
  - CSI 사용자 생성

**사용법**:

```bash
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml
```

### bootstrap.yml

- **목적**: cephadm bootstrap 명령을 Ansible로 자동화
- **원본**: `bootstrap-wrapper.yml`
- **기능**:
  - Monitor IP 설정
  - Dashboard 사용자 생성
  - 클러스터 초기화
  - FSID 생성 및 저장

**사용법**:

```bash
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/bootstrap.yml \
  -e dashboard_user=admin \
  -e dashboard_password="YourPassword"
```

### post-bootstrap.yml

- **목적**: Bootstrap 후 추가 호스트 및 OSD 배포
- **원본**: `01.post-bootstrap-setup.yml`
- **기능**:
  - 추가 호스트 등록 (ceph2, ceph3)
  - SSH 키 배포
  - OSD 자동 배포
  - Monitor 3개 배치
  - Manager 2개 배치

**사용법**:

```bash
# FSID 필요 (bootstrap 출력에서 확인)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/post-bootstrap.yml \
  -e fsid=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

## 배포 옵션

### 옵션 1: 완전 자동화 (권장) ⭐

```bash
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml
```

### 옵션 2: 단계별 배포

```bash
# 1. Bootstrap
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/bootstrap.yml \
  -e dashboard_user=admin \
  -e dashboard_password="P@ssw0rd123"

# 2. Post-Bootstrap 설정
FSID=$(cat current-cluster-fsid.txt)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/post-bootstrap.yml \
  -e fsid=$FSID
```

## 주의사항

- Bootstrap은 클러스터당 한 번만 실행해야 합니다
- 기존 클러스터가 있다면 먼저 purge를 실행하세요
- FSID는 bootstrap 출력에서 확인하거나 `save-current-fsid.yml`로 저장할 수 있습니다