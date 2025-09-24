# 변수 참조 문서

이 문서는 cephadm-ansible에서 사용되는 모든 변수를 정리한 참조 문서입니다.

## 📋 변수 카테고리

1. [전역 변수](#전역-변수)
2. [Preflight 변수](#preflight-변수)
3. [클라이언트 변수](#클라이언트-변수)
4. [스토리지 서비스 변수](#스토리지-서비스-변수)
5. [인벤토리 변수](#인벤토리-변수)

---

## 전역 변수

### 기본 클러스터 변수

| 변수명 | 설명 | 기본값 | 필수 |
|--------|------|---------|------|
| `fsid` | 클러스터 고유 ID | - | ✅ (clients, purge) |
| `ceph_origin` | Ceph 저장소 소스 | `community` | ❌ |
| `ceph_release` | Ceph 릴리스 버전 | `quincy` | ❌ |
| `ceph_stable_key` | GPG 키 URL | `https://download.ceph.com/keys/release.asc` | ❌ |
| `upgrade_ceph_packages` | 패키지 업그레이드 여부 | `false` | ❌ |

### 글로벌 설정 변수

| 변수명 | 설명 | 기본값 | 범위 |
|--------|------|---------|------|
| `mon_max_pg_per_osd` | OSD당 최대 PG 수 | `250` | 100-600 |
| `osd_pool_default_size` | 기본 복제본 수 | `3` | 1-5 |
| `osd_pool_default_min_size` | 최소 복제본 수 | `2` | 1-3 |
| `public_network` | 퍼블릭 네트워크 | - | CIDR 형식 |
| `cluster_network` | 클러스터 네트워크 | - | CIDR 형식 |

---

## Preflight 변수

### 저장소 구성

| 변수명 | 설명 | 유효값 | 기본값 |
|--------|------|--------|--------|
| `ceph_origin` | 저장소 타입 | `community`, `rhcs`, `custom`, `shaman`, `ibm` | `community` |
| `ceph_rhcs_version` | RHCS 버전 | `5`, `6` | `5` |
| `ceph_ibm_version` | IBM Ceph 버전 | `5`, `6` | `5` |
| `ceph_dev_branch` | 개발 브랜치 (shaman) | 브랜치명 | `main` |
| `ceph_dev_sha1` | 개발 빌드 SHA1 | SHA1 또는 `latest` | `latest` |

### 커스텀 저장소

| 변수명 | 설명 | 예제 | 필수 |
|--------|------|------|------|
| `custom_repo_url` | 커스텀 저장소 URL | `http://mirror.example.com/ceph` | ✅ (custom) |
| `custom_repo_gpgkey` | 커스텀 GPG 키 | `http://mirror.example.com/key.asc` | ❌ |
| `custom_repo_state` | 저장소 상태 | `present` / `absent` | ❌ |
| `custom_repo_enabled` | 저장소 활성화 | `1` / `0` | ❌ |

### 패키지 변수

| 변수명 | 설명 | 기본 패키지 |
|--------|------|-------------|
| `ceph_pkgs` | 서버 패키지 | `['cephadm', 'ceph-common']` |
| `infra_pkgs` | 인프라 패키지 | `['chrony', 'podman', 'lvm2', 'sos']` |
| `ceph_client_pkgs` | 클라이언트 패키지 | `['chrony', 'ceph-common']` |

---

## 클라이언트 변수

### 필수 변수

| 변수명 | 설명 | 예제 | 플레이북 |
|--------|------|------|----------|
| `fsid` | 클러스터 FSID | `a7f64266-0894-11e9-b1f8-002590f9ec12` | cephadm-clients.yml |
| `keyring` | 키링 파일 경로 | `/etc/ceph/ceph.client.admin.keyring` | cephadm-clients.yml |

### 선택적 변수

| 변수명 | 설명 | 기본값 | 예제 |
|--------|------|---------|------|
| `client_group` | 클라이언트 그룹명 | `clients` | `web_clients` |
| `keyring_dest` | 키링 대상 경로 | `/etc/ceph/ceph.keyring` | `/opt/ceph/keyring` |
| `conf` | 설정 파일 경로 | 자동 생성 | `/etc/ceph/custom.conf` |
| `local_client_dir` | 로컬 클라이언트 디렉토리 | `~/ceph-ansible-keys` | `/tmp/ceph-keys` |

---

## 스토리지 서비스 변수

### CephFS 변수

| 변수명 | 설명 | 타입 | 예제 |
|--------|------|------|------|
| `ceph.cephfs` | CephFS 구성 배열 | 배열 | - |
| `ceph.cephfs[].name` | 파일시스템 이름 | 문자열 | `fs-production` |
| `ceph.cephfs[].mds.count` | MDS 인스턴스 수 | 정수 | `2` |
| `ceph.cephfs[].mds.placement` | MDS 배치 규칙 | 객체 | `{hosts: [mon1, mon2]}` |

### RGW 변수

| 변수명 | 설명 | 타입 | 예제 |
|--------|------|------|------|
| `ceph.rgw` | RGW 구성 배열 | 배열 | - |
| `ceph.rgw[].realm` | Realm 이름 | 문자열 | `default` |
| `ceph.rgw[].zonegroup` | Zonegroup 이름 | 문자열 | `default` |
| `ceph.rgw[].zone` | Zone 이름 | 문자열 | `default` |
| `ceph.rgw[].service_name` | 서비스 이름 | 문자열 | `rgw-production` |
| `ceph.rgw[].count` | 인스턴스 수 | 정수 | `2` |
| `ceph.rgw[].gateway.s3_url` | S3 엔드포인트 | URL | `http://s3.example.com:80` |

### RGW 사용자 변수

| 변수명 | 설명 | 타입 | 예제 |
|--------|------|------|------|
| `ceph.rgw[].users` | 사용자 배열 | 배열 | - |
| `users[].user_id` | 사용자 ID | 문자열 | `admin` |
| `users[].display_name` | 표시 이름 | 문자열 | `Administrator` |
| `users[].email` | 이메일 | 문자열 | `admin@example.com` |
| `users[].max_buckets` | 최대 버킷 수 | 정수 | `1000` |
| `users[].caps` | 권한 설정 | 배열 | `[{type: buckets, perm: "read, write"}]` |

### RBD 변수

| 변수명 | 설명 | 타입 | 예제 |
|--------|------|------|------|
| `ceph.rbd` | RBD 구성 배열 | 배열 | - |
| `ceph.rbd[].pool_name` | 풀 이름 | 문자열 | `rbd-production` |
| `ceph.rbd[].pool_pg_num` | PG 수 | 정수 | `128` |
| `ceph.rbd[].pool_type` | 풀 타입 | 문자열 | `replicated` / `erasure` |
| `ceph.rbd[].size` | 복제본 수 | 정수 | `3` |
| `ceph.rbd[].min_size` | 최소 복제본 | 정수 | `2` |

### RBD 이미지 변수

| 변수명 | 설명 | 타입 | 예제 |
|--------|------|------|------|
| `ceph.rbd[].images` | 이미지 배열 | 배열 | - |
| `images[].image_name` | 이미지 이름 | 문자열 | `database-vol` |
| `images[].size` | 이미지 크기 | 문자열 | `100G` |
| `images[].image_format` | 이미지 포맷 | 정수 | `2` |
| `images[].object_size` | 객체 크기 | 문자열 | `4M` |
| `images[].image_features` | 이미지 기능 | 배열 | `['layering', 'exclusive-lock']` |

### CSI 변수

| 변수명 | 설명 | 타입 | 예제 |
|--------|------|------|------|
| `ceph.csi` | CSI 구성 배열 | 배열 | - |
| `ceph.csi[].cluster_name` | 클러스터 이름 | 문자열 | `kubernetes-prod` |
| `ceph.csi[].ceph_csi_user` | CSI 사용자명 | 문자열 | `csi-rbd-user` |
| `ceph.csi[].caps.mon` | MON 권한 | 문자열 | `profile rbd` |
| `ceph.csi[].caps.osd` | OSD 권한 | 문자열 | `profile rbd pool=rbd-pool` |
| `ceph.csi[].caps.mgr` | MGR 권한 | 문자열 | `allow rw` |
| `ceph.csi[].caps.mds` | MDS 권한 | 문자열 | `allow rw` |

---

## 인벤토리 변수

### 호스트 변수

| 변수명 | 설명 | 예제 | 범위 |
|--------|------|------|------|
| `ansible_host` | 호스트 IP/도메인 | `192.168.1.10` | 호스트 |
| `ansible_ssh_user` | SSH 사용자 | `ceph-admin` | 전역/그룹/호스트 |
| `ansible_ssh_pass` | SSH 패스워드 | `password` | 전역/그룹/호스트 |
| `ansible_ssh_private_key_file` | SSH 키 파일 | `~/.ssh/id_rsa` | 전역/그룹/호스트 |
| `ansible_become` | 권한 상승 | `true` / `false` | 전역/그룹/호스트 |
| `ansible_become_method` | 권한 상승 방법 | `sudo` / `su` | 전역/그룹/호스트 |

### 그룹 변수

| 그룹명 | 설명 | 필수 | 용도 |
|--------|------|------|------|
| `[admin]` | 관리 호스트 | ✅ (clients, purge) | 키링 및 설정 파일 보유 |
| `[clients]` | 클라이언트 호스트 | ✅ (clients) | 클라이언트 설정 대상 |
| `[mons]` | 모니터 호스트 | ❌ | 모니터 서비스 |
| `[osds]` | OSD 호스트 | ❌ | 스토리지 서비스 |
| `[mgrs]` | 매니저 호스트 | ❌ | 매니저 서비스 |
| `[rgws]` | RGW 호스트 | ❌ | 오브젝트 게이트웨이 |
| `[mdss]` | MDS 호스트 | ❌ | 메타데이터 서버 |

---

## 출력 파일 변수

| 변수명 | 설명 | 기본값 | 용도 |
|--------|------|---------|------|
| `rgw_user_creation_result_file` | RGW 사용자 결과 | `./ceph-rgw-users.csv` | 사용자 정보 저장 |
| `rgw_bucket_creation_result_file` | RGW 버킷 결과 | `./ceph-rgw-buckets.txt` | 버킷 정보 저장 |
| `csi_user_creation_result_file` | CSI 사용자 결과 | `./ceph-csi-users.txt` | CSI 키링 저장 |

---

## 특수 변수

### 런타임 변수

| 변수명 | 설명 | 사용 위치 | 예제 |
|--------|------|-----------|------|
| `rbd_image` | RBD 이미지 경로 | 스냅샷 플레이북 | `pool/image` |
| `snapshot_name` | 스냅샷 이름 | 스냅샷 플레이북 | `backup-20240101` |
| `user_confirm` | 사용자 확인 | 롤백 플레이북 | `yes` / `no` |
| `infra_pkgs_purge` | 제거할 인프라 패키지 | purge 플레이북 | `podman lvm2` |

### 내부 변수

| 변수명 | 설명 | 생성 위치 |
|--------|------|-----------|
| `_ceph_repo` | 저장소 설정 객체 | cephadm-preflight.yml |
| `ceph_custom_repositories` | 커스텀 저장소 배열 | cephadm-preflight.yml |
| `rgw_user_keys` | RGW 사용자 키 배열 | 30.2.rgw_bucket_creation.yml |
| `bucket_tasks` | 버킷 작업 배열 | 30.2.rgw_bucket_creation.yml |

---

## 변수 우선순위

Ansible의 변수 우선순위 (높은 순서대로):

1. 명령줄 변수 (`-e` / `--extra-vars`)
2. 플레이북 vars
3. 플레이북 vars_files
4. 역할 vars
5. 인벤토리 호스트 변수
6. 인벤토리 그룹 변수
7. 역할 defaults
8. 전역 defaults

---

## 변수 검증

### 필수 변수 확인

```yaml
- name: 필수 변수 확인
  fail:
    msg: "변수 {{ item }}이(가) 정의되지 않았습니다"
  when: vars[item] is undefined
  loop:
    - fsid
    - keyring
```

### 변수 타입 검증

```yaml
- name: 숫자 변수 검증
  fail:
    msg: "{{ item }}은(는) 숫자여야 합니다"
  when: vars[item] is not number
  loop:
    - pool_pg_num
    - mds_count
```

### 변수 범위 검증

```yaml
- name: 범위 검증
  fail:
    msg: "mon_max_pg_per_osd는 100-600 사이여야 합니다"
  when: mon_max_pg_per_osd < 100 or mon_max_pg_per_osd > 600
```

---

*이 문서는 cephadm-ansible의 모든 변수를 정리한 참조 문서입니다. 실제 사용 시 필수 변수를 확인하고 환경에 맞게 조정하세요.*