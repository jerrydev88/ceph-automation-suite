# 문제 해결 가이드

이 문서는 cephadm-ansible 사용 중 발생할 수 있는 일반적인 문제와 해결 방법을 제공합니다. 모든 예제는 현재 프로젝트 구조(`hosts-scalable.yml`, `playbooks/` 디렉토리)를 기반으로 합니다.

## 🔧 새로운 검증 시스템

프로젝트에 자동 검증 시스템이 추가되어 문제를 사전에 식별할 수 있습니다:

```bash
# 전체 시스템 검증
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-all.yml

# 개별 컴포넌트 검증
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-cluster-health.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-cephfs.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rgw.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rbd.yml
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-csi-users.yml
```

## 🔍 진단 도구

### 기본 진단 명령어

```bash
# 클러스터 상태 확인
ceph status
ceph health detail

# 서비스 상태 확인
ceph orch ls
ceph orch ps

# 로그 확인
journalctl -u ceph-* -f
tail -f /var/log/ceph/*.log

# 네트워크 연결 확인
ceph ping mon.*
```

---

## 🚨 일반적인 문제와 해결

### 1. Ansible 연결 문제

#### 증상
```
UNREACHABLE! => {"changed": false, "msg": "Failed to connect to the host via ssh"}
```

#### 해결 방법

```bash
# SSH 키 생성 및 배포
ssh-keygen -t rsa -N ""
ssh-copy-id user@target-host

# SSH 설정 확인
vi ~/.ssh/config
```

```
Host *
    StrictHostKeyChecking no
    UserKnownHostsFile=/dev/null
```

#### 추가 확인 사항

- 방화벽 설정 확인
- SELinux 상태 확인 (`getenforce`)
- SSH 서비스 상태 확인

### 2. Preflight 실행 오류

#### 증상: 저장소 접근 실패
```
Failed to download metadata for repo 'ceph_stable'
```

#### 해결 방법

```bash
# 프록시 설정 (필요한 경우)
export http_proxy=http://proxy.example.com:8080
export https_proxy=http://proxy.example.com:8080

# 커스텀 저장소 사용
ansible-playbook -i hosts-scalable.yml cephadm-preflight.yml \
  -e ceph_origin=custom \
  -e custom_repo_url=http://local-mirror/ceph \
  -e custom_repo_gpgkey=http://local-mirror/keys/release.asc

# Ubuntu 24.04 지원 문제 해결
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/fix-ubuntu24.yml
```

#### 증상: Python 모듈 누락
```
ModuleNotFoundError: No module named 'netaddr'
```

#### 해결 방법

```bash
# Python 패키지 설치
pip install netaddr jinja2 pyyaml

# 또는 시스템 패키지로 설치
yum install python3-netaddr python3-jinja2
apt-get install python3-netaddr python3-jinja2
```

### 3. OSD 배포 실패

#### 증상: 디스크를 찾을 수 없음
```
No available devices found
```

#### 해결 방법

```bash
# 디스크 상태 확인
lsblk
ceph orch device ls

# 디스크 초기화 (주의: 데이터 손실!)
wipefs -a /dev/sdX
sgdisk --zap-all /dev/sdX

# LVM 정리
vgremove -f ceph-*
pvremove /dev/sdX

# OSD 재배포 (현재 구조)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/post-bootstrap.yml -e fsid=$(cat current-cluster-fsid.txt)

# 또는 완전 재배포
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml
```

### 4. RGW 서비스 문제

#### 증상: RGW 서비스 시작 실패
```
rgw service not starting
```

#### 해결 방법

```bash
# 서비스 로그 확인
ceph log last cephadm

# 포트 충돌 확인
ss -tlnp | grep :80
ss -tlnp | grep :443

# 서비스 재시작
ceph orch restart rgw.service_name

# 수동 재배포 (현재 구조)
ceph orch rm rgw.service_name
ansible-playbook -i hosts-scalable.yml playbooks/02-services/configure-rgw.yml

# RGW 설정 검증
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-rgw.yml
```

### 5. CSI 사용자 생성 실패

#### 증상: 권한 오류
```
Error EACCES: access denied
```

#### 해결 방법

```bash
# 관리자 권한 확인
ceph auth get client.admin

# CSI 사용자 수동 생성
ceph auth get-or-create client.csi-rbd-user \
  mon 'profile rbd' \
  osd 'profile rbd pool=rbd-pool' \
  mgr 'profile rbd pool=rbd-pool'

# 권한 확인
ceph auth get client.csi-rbd-user

# CSI 사용자 자동 재생성 (현재 구조)
ansible-playbook -i hosts-scalable.yml playbooks/02-services/csi-users.yml

# CSI 사용자 검증
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-csi-users.yml
```

### 6. 클러스터 제거 실패

#### 증상: 풀 삭제 불가
```
Error EPERM: pool deletion is disabled
```

#### 해결 방법

```bash
# mon_allow_pool_delete 활성화
ceph config set mon mon_allow_pool_delete true

# 풀 삭제
ceph osd pool delete pool_name pool_name --yes-i-really-really-mean-it

# 설정 원복
ceph config set mon mon_allow_pool_delete false

# 클러스터 완전 제거 (현재 구조)
ansible-playbook -i hosts-scalable.yml playbooks/90-maintenance/purge-cluster.yml -e force_purge=true
```

### 7. Ubuntu 24.04 (Noble) 관련 문제

#### 증상: cephadm 디렉토리 생성 오류
```
Permission denied: '/var/lib/cephadm'
```

#### 해결 방법

```bash
# 자동 수정
ansible-playbook -i hosts-scalable.yml playbooks/00-preparation/fix-ubuntu24.yml

# 수동 수정
ansible all -i hosts-scalable.yml -m file -a "path=/var/lib/cephadm state=directory mode=0755" --become
```

### 8. 완전 자동화 배포 문제

#### 증상: complete-deployment.yml 실행 중 중단
```
FAILED! => {"msg": "Task failed"}
```

#### 해결 방법

```bash
# 단계별 배포로 전환
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/bootstrap.yml
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/distribute-ssh-key.yml -e admin_node=mon1
ansible-playbook -i hosts-scalable.yml playbooks/03-operations/save-fsid.yml
FSID=$(cat current-cluster-fsid.txt)
ansible-playbook -i hosts-scalable.yml playbooks/01-deployment/post-bootstrap.yml -e fsid=$FSID

# 각 단계 후 검증
ansible-playbook -i hosts-scalable.yml playbooks/04-validation/validate-cluster-health.yml
```

---

## 🛠️ 고급 문제 해결

### MON 쿼럼 손실

#### 증상
```
HEALTH_ERR: no quorum
```

#### 해결 방법

```bash
# MON 상태 확인
ceph mon stat
ceph mon dump

# 문제 MON 제거
ceph mon remove <mon-id>

# 새 MON 추가
ceph orch daemon add mon <host>:<ip>

# 쿼럼 재구성
systemctl restart ceph-mon@*
```

### OSD 성능 문제

#### 증상: 느린 요청
```
slow requests are blocked
```

#### 해결 방법

```bash
# OSD 상태 확인
ceph osd perf
ceph osd df tree

# 문제 OSD 식별
ceph daemon osd.X dump_historic_ops

# OSD 재가중치
ceph osd reweight osd.X 0.9

# scrub 일시 중지
ceph osd set noscrub
ceph osd set nodeep-scrub

# 완료 후 재활성화
ceph osd unset noscrub
ceph osd unset nodeep-scrub
```

### PG 상태 이상

#### 증상
```
PGs are stuck inactive/unclean
```

#### 해결 방법

```bash
# PG 상태 확인
ceph pg stat
ceph pg dump_stuck

# 특정 PG 쿼리
ceph pg <pgid> query

# PG 복구
ceph pg repair <pgid>

# 강제 백필
ceph osd force-backfill <pgid>

# 강제 복구
ceph osd force-recovery <pgid>
```

---

## 📊 성능 튜닝

### 네트워크 최적화

```bash
# MTU 설정
ip link set dev eth0 mtu 9000

# 네트워크 버퍼 크기
echo 'net.core.rmem_max = 134217728' >> /etc/sysctl.conf
echo 'net.core.wmem_max = 134217728' >> /etc/sysctl.conf
sysctl -p
```

### OSD 메모리 최적화

```bash
# OSD 메모리 목표 설정
ceph config set osd osd_memory_target 4294967296  # 4GB

# 캐시 크기 조정
ceph config set osd bluestore_cache_size_ssd 3221225472  # 3GB
ceph config set osd bluestore_cache_size_hdd 1073741824  # 1GB
```

### PG 자동 스케일링

```bash
# 자동 스케일링 활성화
ceph osd pool set <pool> pg_autoscale_mode on

# 목표 비율 설정
ceph osd pool set <pool> target_size_ratio 0.2
```

---

## 🔎 로그 분석

### 로그 위치

| 컴포넌트 | 로그 경로 | 설명 |
|---------|----------|------|
| MON | `/var/log/ceph/ceph-mon.*.log` | 모니터 로그 |
| OSD | `/var/log/ceph/ceph-osd.*.log` | OSD 로그 |
| MGR | `/var/log/ceph/ceph-mgr.*.log` | 매니저 로그 |
| RGW | `/var/log/ceph/ceph-client.rgw.*.log` | RGW 로그 |
| MDS | `/var/log/ceph/ceph-mds.*.log` | MDS 로그 |

### 로그 레벨 조정

```bash
# 임시 조정
ceph tell osd.* config set debug_osd 10/10

# 영구 조정
ceph config set osd debug_osd 10/10

# 원복
ceph config rm osd debug_osd
```

### 유용한 로그 검색 패턴

```bash
# 오류만 검색
grep -i error /var/log/ceph/*.log

# 특정 시간대 로그
journalctl -u ceph-osd@* --since "2024-01-01 10:00" --until "2024-01-01 11:00"

# 실시간 모니터링
tail -f /var/log/ceph/*.log | grep -E "error|warning|fail"
```

---

## 🆘 긴급 복구

### 데이터 복구

```bash
# 백업에서 복구
ceph-objectstore-tool --data-path /var/lib/ceph/osd/ceph-0 --op list

# PG 내보내기
ceph-objectstore-tool --data-path /var/lib/ceph/osd/ceph-0 \
  --pgid 1.0 --op export --file pg-backup.tar

# PG 가져오기
ceph-objectstore-tool --data-path /var/lib/ceph/osd/ceph-1 \
  --op import --file pg-backup.tar
```

### 재해 복구

```bash
# 클러스터 백업
ceph-backup export --all --output backup.tar.gz

# 클러스터 복원
ceph-backup import --input backup.tar.gz

# MON 데이터베이스 재구축
ceph-monstore-tool /var/lib/ceph/mon/ceph-mon1 rebuild
```

---

## 📝 체크리스트

### 문제 발생 시 확인 사항

- [ ] 클러스터 상태 (`ceph -s`)
- [ ] 네트워크 연결성
- [ ] 디스크 공간 (`df -h`)
- [ ] 메모리 사용량 (`free -m`)
- [ ] 서비스 상태 (`systemctl status ceph-*`)
- [ ] 로그 확인 (`/var/log/ceph/`)
- [ ] 시간 동기화 (`chronyc sources`)
- [ ] 방화벽 규칙
- [ ] SELinux/AppArmor 상태

### 에스컬레이션 기준

1. **레벨 1**: 일반적인 문제 - 이 가이드로 해결
2. **레벨 2**: 성능 저하 - 튜닝 및 최적화
3. **레벨 3**: 데이터 손실 위험 - 즉시 백업 및 전문가 상담
4. **레벨 4**: 클러스터 다운 - 긴급 복구 프로세스 실행

---

## 📚 추가 리소스

- [Ceph 공식 문제 해결 가이드](https://docs.ceph.com/en/latest/rados/troubleshooting/)
- [cephadm 문제 해결](https://docs.ceph.com/en/latest/cephadm/troubleshooting/)
- [Ceph 사용자 메일링 리스트](https://lists.ceph.io/postorius/lists/ceph-users.ceph.io/)
- [Ceph 트래커](https://tracker.ceph.com/)

---

*이 문서는 일반적인 문제 해결 가이드입니다. 심각한 문제의 경우 데이터 백업을 먼저 수행하고 전문가의 도움을 받으세요.*