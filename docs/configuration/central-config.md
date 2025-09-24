# 중앙 구성 파일 가이드

이 문서는 cephadm-ansible의 중앙 구성 관리 방법을 설명합니다. 두 가지 주요 구성 파일을 통해 인프라와 서비스를 분리하여 관리합니다.

## 📄 개요

cephadm-ansible은 두 가지 중앙 구성 파일을 사용합니다:

1. **`group_vars/all.yml`** - 인프라 및 배포 설정 (SSH, 저장소, Ubuntu 버전 매핑 등)
2. **`ceph-vars.yml`** - Ceph 서비스 구성 (CephFS, RGW, RBD, CSI 등)

이러한 분리를 통해 인프라 설정과 서비스 구성을 독립적으로 관리할 수 있습니다.

---

## 🔧 group_vars/all.yml - 인프라 구성

인프라 레벨의 설정을 관리하는 중앙 파일입니다. 이 파일은 모든 호스트에 자동으로 적용됩니다.

### 파일 위치
```bash
cephadm-ansible/
├── group_vars/
│   └── all.yml    # 모든 호스트에 적용되는 변수
├── hosts.yaml     # 인벤토리 파일
└── ceph-vars.yml  # Ceph 서비스 구성
```

### 기본 구조

```yaml
# group_vars/all.yml

# SSH 설정
ansible_ssh_user: mocomsys
ansible_ssh_pass: mocomsys
ansible_become: true
ansible_become_method: sudo

# Ceph 기본 설정
ceph_release: reef
ceph_origin: community
ceph_mirror: https://download.ceph.com

# Ubuntu 버전별 저장소 매핑
ubuntu_ceph_repo_mapping:
  # 매핑 정의
```

### Ubuntu 버전 매핑 (확장 가능한 설계)

새로운 Ubuntu 버전 출시 시 이 섹션만 업데이트하면 됩니다:

```yaml
# Ubuntu 버전별 Ceph 저장소 매핑
ubuntu_ceph_repo_mapping:
  # Ubuntu 25.04 (Plucky Puffin) - 예정
  plucky: jammy

  # Ubuntu 24.10 (Oracular Oriole) - 예정
  oracular: jammy

  # Ubuntu 24.04 LTS (Noble Numbat)
  noble: jammy

  # Ubuntu 23.10 (Mantic Minotaur)
  mantic: jammy

  # Ubuntu 23.04 (Lunar Lobster)
  lunar: jammy

  # Ubuntu 22.04 LTS (Jammy Jellyfish) - Ceph 공식 지원
  jammy: jammy

  # Ubuntu 20.04 LTS (Focal Fossa) - Ceph 공식 지원
  focal: focal

# 저장소 결정 로직
ceph_stable_release_deb: "{{ ubuntu_ceph_repo_mapping[ansible_distribution_release] | default('jammy') }}"
```

### 추가 인프라 설정 옵션

```yaml
# 네트워크 설정
public_network: "10.10.2.0/24"
cluster_network: "10.10.3.0/24"

# 패키지 버전 고정 (프로덕션용)
ceph_package_version_lock: false
ceph_package_version: "*"  # 또는 특정 버전: "17.2.6-1"

# 디버깅 변수
debug_ubuntu_version: "{{ ansible_distribution }} {{ ansible_distribution_version }} ({{ ansible_distribution_release }})"
debug_ceph_repo_used: "{{ ceph_stable_release_deb }}"

# Ceph 최소 버전 요구사항
ceph_minimum_ubuntu_versions:
  quincy: "20.04"
  reef: "20.04"
  squid: "22.04"
```

### 환경별 설정

```yaml
# 개발 환경
development:
  ceph_release: reef
  ceph_package_version_lock: false

# 스테이징 환경
staging:
  ceph_release: reef
  ceph_package_version: "17.2.6-1"
  ceph_package_version_lock: true

# 프로덕션 환경
production:
  ceph_release: reef
  ceph_package_version: "17.2.6-1"
  ceph_package_version_lock: true
```

---

## 📁 ceph-vars.yml - 서비스 구성

Ceph 스토리지 서비스의 상세 구성을 정의하는 파일입니다.

### 파일 구조

```yaml
ceph:
  global:         # 전역 설정
  cephfs:        # CephFS 구성
  rgw:           # RADOS Gateway 구성
  rbd:           # RBD 블록 스토리지 구성
  csi:           # Kubernetes CSI 구성
  # 출력 파일 경로
  rgw_user_creation_result_file: "경로"
  rgw_bucket_creation_result_file: "경로"
  csi_user_creation_result_file: "경로"
```

---

## 🌐 전역 설정 (Global)

클러스터 전체에 적용되는 설정을 정의합니다.

### 기본 구조

```yaml
ceph:
  global:
    mon_max_pg_per_osd: 300
```

### 주요 파라미터

| 파라미터 | 설명 | 기본값 | 권장값 |
|---------|------|--------|-------|
| `mon_max_pg_per_osd` | OSD당 최대 PG 수 | 250 | 300-400 |
| `osd_pool_default_size` | 복제본 수 | 3 | 3 |
| `osd_pool_default_min_size` | 최소 복제본 수 | 2 | 2 |

### 사용 예제

```yaml
ceph:
  global:
    mon_max_pg_per_osd: 300
    osd_pool_default_size: 3
    osd_pool_default_min_size: 2
    public_network: "10.0.0.0/24"
    cluster_network: "10.0.1.0/24"
```

---

## 📁 CephFS 구성

분산 파일시스템 구성을 정의합니다.

### 기본 구조

```yaml
ceph:
  cephfs:
    - name: "파일시스템_이름"
      mds:
        count: MDS_서비스_수
```

### 상세 예제

```yaml
ceph:
  cephfs:
    - name: fs-production
      mds:
        count: 2
        placement:
          hosts:
            - mon1
            - mon2
    - name: fs-backup
      mds:
        count: 1
```

### MDS 배치 옵션

```yaml
mds:
  count: 2
  placement:
    # 옵션 1: 특정 호스트
    hosts:
      - mon1
      - mon2

    # 옵션 2: 라벨 기반
    label: "mds"

    # 옵션 3: 호스트 패턴
    host_pattern: "mds*"
```

---

## 🌐 RGW (RADOS Gateway) 구성

S3/Swift 호환 오브젝트 스토리지 구성입니다.

### 기본 구조

```yaml
ceph:
  rgw:
    - realm: "realm_이름"
      zonegroup: "zonegroup_이름"
      zone: "zone_이름"
      service_name: "서비스_이름"
      count: 인스턴스_수
      gateway:
        s3_url: "접근_URL"
      users: []
```

### 상세 예제

```yaml
ceph:
  rgw:
    - realm: default
      zonegroup: default
      zone: default
      service_name: rgw-production
      count: 2
      gateway:
        s3_url: "http://s3.example.com:80"
        swift_url: "http://swift.example.com:80"
      users:
        - user_id: "admin"
          display_name: "Administrator"
          email: "admin@example.com"
          max_buckets: 1000
          buckets:
            - name: "data-bucket"
              permissions: "read, write, delete"
              quota: "100GB"
              versioning: true
              lifecycle:
                - days: 30
                  action: "delete"
          caps:
            - type: "buckets"
              perm: "read, write, delete"
            - type: "metadata"
              perm: "read, write"
            - type: "usage"
              perm: "read"
            - type: "zone"
              perm: "read, write"
```

### 사용자 권한 (Caps) 옵션

| Type | 권한 옵션 | 설명 |
|------|----------|------|
| `buckets` | read, write, delete | 버킷 관리 권한 |
| `metadata` | read, write | 메타데이터 접근 |
| `usage` | read, write | 사용량 정보 |
| `users` | read, write | 사용자 관리 |
| `zone` | read, write | Zone 관리 |

### 버킷 설정 옵션

```yaml
buckets:
  - name: "bucket-name"
    permissions: "read, write, delete"
    quota: "100GB"              # 크기 제한
    max_objects: 10000          # 객체 수 제한
    versioning: true            # 버전 관리
    encryption: true            # 암호화
    public_read: false          # 공개 읽기
    cors:                       # CORS 설정
      - origin: "https://example.com"
        methods: ["GET", "POST"]
        headers: ["*"]
```

---

## 💾 RBD (RADOS Block Device) 구성

블록 스토리지 풀과 이미지 구성입니다.

### 기본 구조

```yaml
ceph:
  rbd:
    - pool_name: "풀_이름"
      pool_pg_num: PG_수
      images: []
```

### 상세 예제

```yaml
ceph:
  rbd:
    - pool_name: rbd-production
      pool_pg_num: 128
      pool_type: "replicated"      # replicated 또는 erasure
      size: 3                       # 복제본 수
      min_size: 2                   # 최소 복제본 수
      crush_rule: "default"         # CRUSH 규칙
      application: "rbd"            # 애플리케이션 타입
      images:
        - image_name: database-vol
          size: 100G
          image_format: 2           # RBD 이미지 포맷 (1 또는 2)
          object_size: 4M           # 객체 크기
          image_features:           # 이미지 기능
            - layering
            - exclusive-lock
            - object-map
            - fast-diff
            - deep-flatten
        - image_name: web-vol
          size: 50G
          image_format: 2
          object_size: 4M
          image_features:
            - layering
```

### PG 수 계산 가이드

```
PG 수 = (OSD 수 × 100) / 복제본 수
```

예시:
- OSD 12개, 복제본 3개: (12 × 100) / 3 = 400 → 512 (2의 제곱수로 반올림)

### 이미지 기능 옵션

| 기능 | 설명 | 호환성 |
|-----|------|---------|
| `layering` | 클론 지원 | 모든 클라이언트 |
| `exclusive-lock` | 배타적 잠금 | librbd ≥ 0.92 |
| `object-map` | 객체 맵 | librbd ≥ 0.93 |
| `fast-diff` | 빠른 diff | librbd ≥ 0.93 |
| `deep-flatten` | 깊은 평탄화 | librbd ≥ 0.93 |

---

## 🚀 CSI (Container Storage Interface) 구성

Kubernetes와의 통합을 위한 CSI 사용자 구성입니다.

### 기본 구조

```yaml
ceph:
  csi:
    - cluster_name: "클러스터_이름"
      ceph_csi_user: "사용자_이름"
      caps:
        mon: "권한"
        osd: "권한"
```

### 상세 예제

```yaml
ceph:
  csi:
    # RBD 일반 사용자
    - cluster_name: "kubernetes-prod"
      ceph_csi_user: "csi-rbd-node"
      caps:
        mon: "profile rbd"
        osd: "profile rbd pool=rbd-k8s"

    # RBD 프로비저너 (관리자)
    - cluster_name: "kubernetes-prod"
      ceph_csi_user: "csi-rbd-provisioner"
      caps:
        mon: "profile rbd, allow command 'osd blocklist'"
        mgr: "allow rw"
        osd: "profile rbd pool=rbd-k8s"

    # CephFS 사용자
    - cluster_name: "kubernetes-prod"
      ceph_csi_user: "csi-cephfs-node"
      caps:
        mon: "allow r"
        mgr: "allow rw"
        osd: "allow rw pool=cephfs-data, allow rw pool=cephfs-metadata"
        mds: "allow rw"

    # CephFS 프로비저너
    - cluster_name: "kubernetes-prod"
      ceph_csi_user: "csi-cephfs-provisioner"
      caps:
        mon: "allow r, allow command 'osd blocklist'"
        mgr: "allow rw"
        osd: "allow rw pool=cephfs-data, allow rw pool=cephfs-metadata"
        mds: "allow *"
```

### CSI 사용자 타입별 권한

| 사용자 타입 | 용도 | 필요 권한 |
|------------|------|----------|
| RBD Node | Pod에서 볼륨 마운트 | mon: "profile rbd", osd: "profile rbd pool=풀이름" |
| RBD Provisioner | PV 동적 생성 | mon: "profile rbd, allow command 'osd blocklist'", mgr: "allow rw" |
| CephFS Node | Pod에서 파일시스템 마운트 | mon: "allow r", mds: "allow rw" |
| CephFS Provisioner | PV 동적 생성 | mon: "allow r, allow command 'osd blocklist'", mds: "allow *" |

---

## 📄 출력 파일 설정

작업 결과를 저장할 파일 경로를 설정합니다.

```yaml
ceph:
  # RGW 사용자 생성 결과
  rgw_user_creation_result_file: "./results/rgw-users.csv"

  # RGW 버킷 생성 결과
  rgw_bucket_creation_result_file: "./results/rgw-buckets.txt"

  # CSI 사용자 생성 결과
  csi_user_creation_result_file: "./results/csi-users.txt"
```

---

## 🔧 전체 예제

완전한 `ceph-vars.yml` 파일 예제:

```yaml
ceph:
  global:
    mon_max_pg_per_osd: 300
    osd_pool_default_size: 3
    osd_pool_default_min_size: 2

  cephfs:
    - name: fs-production
      mds:
        count: 2

  rgw:
    - realm: default
      zonegroup: default
      zone: default
      service_name: rgw-prod
      count: 2
      gateway:
        s3_url: "http://s3.example.com:80"
      users:
        - user_id: "app-user"
          display_name: "Application User"
          email: "app@example.com"
          buckets:
            - name: "app-data"
              permissions: "read, write, delete"
              quota: "50GB"
          caps:
            - type: "buckets"
              perm: "read, write, delete"

  rbd:
    - pool_name: rbd-prod
      pool_pg_num: 128
      images:
        - image_name: db-volume
          size: 100G
          image_format: 2
          object_size: 4M
          image_features:
            - layering
            - exclusive-lock

  csi:
    - cluster_name: "k8s-cluster"
      ceph_csi_user: "csi-rbd-node"
      caps:
        mon: "profile rbd"
        osd: "profile rbd pool=rbd-prod"

  rgw_user_creation_result_file: "./ceph-rgw-users.csv"
  rgw_bucket_creation_result_file: "./ceph-rgw-buckets.txt"
  csi_user_creation_result_file: "./ceph-csi-users.txt"
```

---

## ✅ 검증 및 테스트

### 구성 파일 검증

```bash
# YAML 문법 검증
python -c "import yaml; yaml.safe_load(open('ceph-vars.yml'))"

# Ansible 변수 테스트
ansible-playbook -i hosts.yaml test-vars.yml --check
```

### 테스트 플레이북

```yaml
# test-vars.yml
---
- hosts: localhost
  vars_files:
    - ceph-vars.yml
  tasks:
    - name: 변수 출력
      debug:
        var: ceph
```

---

## 📚 참고 사항

1. **백업**: 변경 전 항상 기존 설정 백업
2. **단계적 적용**: 큰 변경은 단계적으로 적용
3. **테스트 환경**: 프로덕션 적용 전 테스트 환경에서 검증
4. **문서화**: 변경 사항은 반드시 문서화
5. **버전 관리**: Git 등으로 설정 파일 버전 관리

---

*이 문서는 ceph-vars.yml 구성 파일의 완전한 가이드입니다. 실제 환경에 맞게 값을 조정하여 사용하세요.*
