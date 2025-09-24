# 00-preparation - 사전 준비 플레이북

이 디렉토리는 Ceph 클러스터 배포 전 필요한 모든 준비 작업을 위한 플레이북을 포함합니다.

## 플레이북 목록

### fix-ubuntu24.yml
- **목적**: Ubuntu 24.04 특정 버그 수정
- **원본**: `fix-cephadm-quick.yml`
- **기능**:
  - `/var/lib/cephadm` 디렉토리 생성
  - cephadm 패키지 문제 해결

**사용법**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/fix-ubuntu24.yml
```

### prepare-disks.yml
- **목적**: OSD용 디스크 초기화 및 준비
- **원본**: `zap-disks-for-osd.yml`
- **기능**:
  - 기존 파티션/파일시스템 제거
  - LVM 볼륨 정리
  - 디스크 완전 초기화

**사용법**:
```bash
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/prepare-disks.yml
```

⚠️ **주의**: prepare-disks.yml은 지정된 디스크의 모든 데이터를 삭제합니다!

## 실행 순서

1. fix-ubuntu24.yml (Ubuntu 24.04 사용 시)
2. `cephadm-preflight.yml` (원본 프로젝트 파일 사용)
3. prepare-disks.yml (필요 시)

**참고**: preflight는 원본 cephadm-ansible 프로젝트 파일이므로 루트 디렉토리의 `cephadm-preflight.yml`을 사용합니다.