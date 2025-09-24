# 인벤토리 구성 가이드

## 📋 개요

Ansible 인벤토리는 cephadm-ansible이 관리할 호스트들을 정의하는 핵심 구성 파일입니다. 이 가이드는 `hosts-scalable.yml`을 기반으로 확장 가능하고 유지보수가 쉬운 인벤토리 구성 방법을 설명합니다.

> **참고**: 이 프로젝트에서는 `hosts-scalable.yml`을 표준 인벤토리 파일명으로 사용합니다.

## 🏗️ 인벤토리 구조

### 기본 구조

```yaml
all:
  vars:
    # 전역 변수 정의
  children:
    # 호스트 그룹 정의
    mons:
      hosts:
        # 모니터 호스트
    osds:
      hosts:
        # OSD 호스트
    mgrs:
      hosts:
        # 매니저 호스트
```

## 🔧 확장 가능한 구성 방법

### 1. 표준 구성 - hosts-scalable.yml (권장)

현재 프로젝트에서 사용하는 표준 구성 방식:

```yaml
# hosts-scalable.yml - 표준 인벤토리 구성
all:
  vars:
    ansible_ssh_user: mocomsys
    ansible_ssh_pass: mocomsys

    # Ubuntu 24.04 기본 저장소의 Squid 사용 (권장)
    ceph_origin: distro  # Ceph Squid 19.2.0 사용
    ceph_mirror: https://download.ceph.com

    # 확장 가능한 Ubuntu 버전 매핑 전략
    ubuntu_to_ceph_repo_map:
      noble: jammy      # 24.04 -> 22.04 저장소
      mantic: jammy     # 23.10 -> 22.04 저장소
      lunar: jammy      # 23.04 -> 22.04 저장소
      jammy: jammy      # 22.04 -> 22.04 저장소
      focal: focal      # 20.04 -> 20.04 저장소

    # 실제 사용할 저장소 결정
    ceph_stable_release_deb: "{{ ubuntu_to_ceph_repo_map[ansible_distribution_release] | default(ansible_distribution_release) }}"

  children:
    mons:
      hosts:
        mon1:
          ansible_host: 10.10.2.91
        mon2:
          ansible_host: 10.10.2.92
        mon3:
          ansible_host: 10.10.2.93

    # 모든 서비스가 모니터 호스트를 재사용하는 효율적 구성
    osds:
      children:
        mons: {}
    mgrs:
      children:
        mons: {}
    monitoring:
      children:
        mons: {}
    clients:
      children:
        mons: {}
    mdss:
      children:
        mons: {}
    admin:
      hosts:
        mon1: {}  # 첫 번째 모니터를 관리 노드로 사용
```

### 2. 중앙 집중식 변수 관리 (대안)

**group_vars/all.yml** 사용으로 인벤토리와 변수 분리:

```yaml
# group_vars/all.yml - 중앙 집중식 변수
ansible_ssh_user: mocomsys
ansible_ssh_pass: mocomsys
ceph_origin: distro
ceph_mirror: https://download.ceph.com

# Ubuntu 버전 매핑
ubuntu_to_ceph_repo_map:
  noble: jammy    # 24.04
  mantic: jammy   # 23.10
  jammy: jammy    # 22.04
  focal: focal    # 20.04

ceph_stable_release_deb: "{{ ubuntu_to_ceph_repo_map[ansible_distribution_release] | default('jammy') }}"
```

### 3. 고급 Ubuntu 버전 매핑 전략

hosts-scalable.yml에서 지원하는 다양한 매핑 전략:

#### 방법 1: 딕셔너리 매핑 (현재 사용 중, 가장 확장성 좋음)

```yaml
# Ubuntu 버전 -> Ceph 저장소 매핑
ubuntu_to_ceph_repo_map:
  noble: jammy      # 24.04 -> 22.04 저장소
  mantic: jammy     # 23.10 -> 22.04 저장소
  lunar: jammy      # 23.04 -> 22.04 저장소
  jammy: jammy      # 22.04 -> 22.04 저장소
  focal: focal      # 20.04 -> 20.04 저장소
  # 향후 추가 가능
  # oracular: jammy  # 24.10 -> 22.04 저장소
  # plucky: jammy    # 25.04 -> 22.04 저장소

# 실제 사용할 저장소 결정
ceph_stable_release_deb: "{{ ubuntu_to_ceph_repo_map[ansible_distribution_release] | default(ansible_distribution_release) }}"
```

#### 방법 2: 버전 번호 기반 매핑

```yaml
# Ubuntu 버전이 22.10 이상이면 jammy 사용
ceph_stable_release_deb: >-
  {%- if ansible_distribution_version is version('22.10', '>=') -%}
    jammy
  {%- elif ansible_distribution_version is version('20.04', '>=') and ansible_distribution_version is version('22.04', '<=') -%}
    {{ ansible_distribution_release }}
  {%- else -%}
    focal
  {%- endif -%}
```

#### 방법 3: Ceph 지원 저장소 목록 기반

```yaml
ceph_supported_distros:
  - focal
  - jammy

ceph_stable_release_deb: >-
  {%- if ansible_distribution_release in ceph_supported_distros -%}
    {{ ansible_distribution_release }}
  {%- else -%}
    jammy
  {%- endif -%}
```

## 📊 호스트 그룹 설명

### 필수 그룹

| 그룹명 | 용도 | 최소 수량 | 권장 수량 |
|--------|------|----------|-----------|
| `admin` | 클러스터 관리 노드 | 1 | 1 |
| `mons` | 모니터 데몬 | 1 | 3 (홀수) |

### 선택적 그룹

| 그룹명 | 용도 | 권장 구성 | hosts-scalable.yml 패턴 |
|--------|------|-----------|------------------------|
| `osds` | 스토리지 데몬 | 모든 스토리지 노드 | `children: mons: {}` |
| `mgrs` | 매니저 데몬 | 모니터와 동일 | `children: mons: {}` |
| `mdss` | 메타데이터 서버 (CephFS) | 2개 이상 (HA) | `children: mons: {}` |
| `rgws` | RADOS 게이트웨이 | 2개 이상 (LB) | 별도 구성 또는 `children: mons: {}` |
| `monitoring` | 모니터링 스택 | 전용 노드 권장 | `children: mons: {}` |
| `clients` | Ceph 클라이언트 | 필요에 따라 | `children: mons: {}` |

### 🔄 호스트 재사용 패턴 (현재 사용 중)

hosts-scalable.yml에서 사용하는 효율적인 패턴:

```yaml
# 모니터 호스트 정의 (기준점)
mons:
  hosts:
    mon1:
      ansible_host: 10.10.2.91
    mon2:
      ansible_host: 10.10.2.92
    mon3:
      ansible_host: 10.10.2.93

# 모든 서비스가 모니터 호스트를 재사용
osds:
  children:
    mons: {}  # mon1, mon2, mon3가 모두 OSD 역할도 수행
mgrs:
  children:
    mons: {}  # mon1, mon2, mon3가 모두 매니저 역할도 수행
monitoring:
  children:
    mons: {}  # mon1, mon2, mon3가 모니터링 역할도 수행
clients:
  children:
    mons: {}  # mon1, mon2, mon3가 클라이언트 역할도 수행
mdss:
  children:
    mons: {}  # mon1, mon2, mon3가 MDS 역할도 수행
```

이 패턴의 장점:
- **리소스 효율성**: 적은 수의 노드로 모든 서비스 실행
- **관리 단순화**: 호스트 정보를 한 곳에서만 관리
- **확장성**: 필요시 특정 서비스만 별도 호스트로 분리 가능
- **비용 절약**: 개발/테스트 환경에서 인프라 비용 최소화

## 🔄 동적 인벤토리

### Python 스크립트 기반 동적 인벤토리

```python
#!/usr/bin/env python3
# dynamic_inventory.py

import json
import subprocess

def get_hosts_from_cloud():
    """클라우드 API나 다른 소스에서 호스트 정보 가져오기"""
    # 실제 구현은 환경에 따라 다름
    hosts = {
        "mon1": "10.10.2.91",
        "mon2": "10.10.2.92",
        "mon3": "10.10.2.93"
    }
    return hosts

def generate_inventory():
    hosts = get_hosts_from_cloud()

    inventory = {
        "_meta": {
            "hostvars": {}
        },
        "all": {
            "vars": {
                "ansible_ssh_user": "mocomsys",
                "ceph_release": "reef",
                "ceph_origin": "community"
            }
        },
        "mons": {
            "hosts": []
        },
        "admin": {
            "hosts": ["mon1"]
        }
    }

    for hostname, ip in hosts.items():
        inventory["mons"]["hosts"].append(hostname)
        inventory["_meta"]["hostvars"][hostname] = {
            "ansible_host": ip
        }

    return inventory

if __name__ == "__main__":
    print(json.dumps(generate_inventory(), indent=2))
```

사용 방법:

```bash
chmod +x dynamic_inventory.py
ansible-playbook -i dynamic_inventory.py cephadm-preflight.yml
```

## 🔐 보안 고려사항

### 1. SSH 키 기반 인증 사용

```yaml
all:
  vars:
    ansible_ssh_user: ceph-admin
    ansible_ssh_private_key_file: ~/.ssh/ceph_key
    # ansible_ssh_pass는 제거
```

### 2. Ansible Vault로 민감 정보 암호화

```bash
# 비밀번호 파일 생성
cat > vault_vars.yml << EOF
ansible_ssh_pass: "실제_패스워드"
ceph_admin_password: "관리자_패스워드"
EOF

# 암호화
ansible-vault encrypt vault_vars.yml

# 인벤토리에서 참조
echo "all:" > hosts.yaml
echo "  vars_files:" >> hosts.yaml
echo "    - vault_vars.yml" >> hosts.yaml
```

### 3. 환경별 인벤토리 분리

```bash
inventory/
├── production/
│   ├── hosts-scalable.yml
│   └── group_vars/
│       └── all.yml
├── staging/
│   ├── hosts-scalable.yml
│   └── group_vars/
│       └── all.yml
└── development/
    ├── hosts-scalable.yml
    └── group_vars/
        └── all.yml
```

#### 환경별 설정 예시

```bash
# 개발 환경 배포
ansible-playbook -i inventory/development/hosts-scalable.yml \
  playbooks/01-deployment/complete-deployment.yml

# 스테이징 환경 검증
ansible-playbook -i inventory/staging/hosts-scalable.yml \
  playbooks/04-validation/validate-all.yml

# 프로덕션 환경 배포 (더 신중한 접근)
ansible-playbook -i inventory/production/hosts-scalable.yml \
  playbooks/01-deployment/bootstrap.yml --check
```

## 🎯 베스트 프랙티스

### 1. 호스트 네이밍 규칙

```yaml
# Good - 역할과 번호 명시
mon1, mon2, mon3
osd1, osd2, osd3
rgw1, rgw2

# Bad - 의미 없는 이름
server1, server2
node-a, node-b
```

### 2. IP 주소 관리

```yaml
# 네트워크별 변수 정의
all:
  vars:
    networks:
      public: "10.10.2.0/24"
      cluster: "10.10.3.0/24"

  children:
    mons:
      hosts:
        mon1:
          ansible_host: 10.10.2.91
          cluster_ip: 10.10.3.91
```

### 3. 호스트 그룹 재사용

```yaml
all:
  children:
    mons:
      hosts:
        mon1: {}
        mon2: {}
        mon3: {}

    # 모니터 호스트를 다른 역할로도 사용
    osds:
      children:
        mons: {}  # 모든 모니터를 OSD로 사용

    mgrs:
      children:
        mons: {}  # 모든 모니터를 매니저로 사용

    # 또는 일부만 선택
    rgws:
      hosts:
        mon1: {}  # 첫 번째 모니터만 RGW로 사용
        mon2: {}
```

## 📝 Ubuntu 버전별 설정

### Ubuntu 24.04 (Noble) 특별 설정

```yaml
# group_vars/all.yml
ubuntu_ceph_repo_mapping:
  noble: jammy    # Noble은 Jammy 저장소 사용
  mantic: jammy
  jammy: jammy
  focal: focal

# 자동 감지 및 매핑
ceph_stable_release_deb: "{{ ubuntu_ceph_repo_mapping[ansible_distribution_release] | default('jammy') }}"
```

### 버전별 조건부 설정

```yaml
all:
  vars:
    # Ubuntu 버전에 따른 패키지 설정
    ceph_packages: >-
      {%- if ansible_distribution_version is version('24.04', '>=') -%}
        ['cephadm', 'ceph-common', 'python3-packaging']
      {%- else -%}
        ['cephadm', 'ceph-common']
      {%- endif -%}
```

## 🧪 인벤토리 검증

### 1. 인벤토리 구조 확인

```bash
# 모든 호스트 나열
ansible -i hosts-scalable.yml all --list-hosts

# 특정 그룹 확인
ansible -i hosts-scalable.yml mons --list-hosts

# 변수 확인
ansible -i hosts-scalable.yml all -m debug -a "var=ceph_stable_release_deb"

# Ubuntu 버전 매핑 확인
ansible -i hosts-scalable.yml all -m debug -a "var=ubuntu_to_ceph_repo_map"
```

### 2. 연결 테스트

```bash
# 모든 호스트 ping
ansible -i hosts-scalable.yml all -m ping

# SSH 연결 확인
ansible -i hosts-scalable.yml all -m shell -a "hostname"

# 배포 전 사전 검사
ansible-playbook -i hosts-scalable.yml cephadm-preflight.yml --check
```

### 3. 변수 우선순위 확인

```bash
# 특정 호스트의 모든 변수 보기
ansible-inventory -i hosts-scalable.yml --host mon1

# 그룹 변수 확인
ansible-inventory -i hosts-scalable.yml --graph

# 실제 사용될 Ceph 저장소 확인
ansible -i hosts-scalable.yml all -m setup -a "filter=ansible_distribution*"
```

## 🔧 문제 해결

### 일반적인 문제

1. **SSH 연결 실패**

   ```bash
   # SSH 키 복사
   ssh-copy-id user@host

   # 권한 확인
   chmod 600 ~/.ssh/id_rsa
   ```

2. **변수 우선순위 충돌**

   ```yaml
   # 명시적 우선순위 지정
   ansible-playbook -i hosts-scalable.yml playbook.yml \
     -e "ceph_origin=distro"
   ```

3. **호스트 그룹 중복**

   ```yaml
   # children 사용으로 중복 방지
   osds:
     children:
       mons: {}  # 호스트 재정의 대신 참조
   ```

## 📚 참고 자료

- [Ansible 인벤토리 문서](https://docs.ansible.com/ansible/latest/user_guide/intro_inventory.html)
- [cephadm-ansible 인벤토리 예제](https://github.com/ceph/cephadm-ansible/tree/main/infrastructure-playbooks)
- [Ansible Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)

---

*이 문서는 cephadm-ansible의 인벤토리 구성 모범 사례를 제공합니다. 환경에 맞게 조정하여 사용하세요.*
