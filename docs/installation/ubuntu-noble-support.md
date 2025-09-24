# Ubuntu 24.04 (Noble Numbat) Ceph 지원 가이드

## 📋 개요

Ubuntu 24.04 (Noble Numbat)는 2024년 4월에 출시되었지만, Ceph 공식 저장소에서는 아직 직접적인 지원을 제공하지 않습니다. 이 문서는 Ubuntu 24.04에서 cephadm-ansible을 사용하여 Ceph를 배포하는 방법과 향후 Ubuntu 버전에 대한 확장 가능한 해결책을 제공합니다.

## 🔍 문제 상황

### 현재 Ceph 저장소 지원 현황

| Ceph 버전 | 지원 Ubuntu 버전 |
|----------|-----------------|
| Reef | focal (20.04), jammy (22.04) |
| Squid | bookworm, jammy (22.04) |
| Quincy | focal (20.04), jammy (22.04) |

### 주요 이슈
- Ceph 공식 저장소(download.ceph.com)에 Noble 전용 저장소 없음
- Ubuntu 24.04 시스템에서 `ceph_origin: community` 사용 시 저장소 오류 발생
- 새로운 Ubuntu 버전이 출시될 때마다 동일한 문제 반복 가능성

## ✅ 권장 솔루션: Ubuntu 24.04 기본 저장소 사용

### Ubuntu 24.04의 Ceph Squid 지원

Ubuntu 24.04 LTS는 기본 저장소에 **Ceph Squid (19.2.0)**를 포함하고 있습니다. 이는 Reef (18.x)보다 최신 버전으로, 추가 저장소 설정 없이 바로 사용 가능합니다.

```yaml
# group_vars/all.yml
# Ubuntu 24.04 기본 저장소 사용 (권장)
ceph_origin: distro  # Ceph Squid 19.2.0 사용
```

### Ceph 버전 비교

| Ceph 버전 | 릴리스 번호 | Ubuntu 지원 |
|----------|------------|------------|
| Quincy | 17.x | Ubuntu 22.04 기본 |
| Reef | 18.x | 공식 저장소 필요 |
| Squid | 19.x | Ubuntu 24.04 기본 ✅ |

## 🔧 대안: 확장 가능한 매핑 전략

### 1. 중앙 집중식 구성 (group_vars/all.yml)

가장 확장성 있고 관리하기 쉬운 방법입니다.

```yaml
# group_vars/all.yml
# 중앙 집중식 변수 관리 (더 나은 확장성)

# SSH 설정
ansible_ssh_user: mocomsys
ansible_ssh_pass: mocomsys

# Ceph 기본 설정
# Ubuntu 24.04는 Squid (19.2.0) 기본 포함
ceph_origin: distro  # 권장: Ubuntu 저장소 사용

# 또는 특정 버전이 필요한 경우:
# ceph_release: reef
# ceph_origin: community
ceph_mirror: https://download.ceph.com

# Ubuntu 버전별 Ceph 저장소 매핑
# 새로운 Ubuntu 버전이 출시되면 여기만 업데이트
ubuntu_ceph_repo_mapping:
  # Ubuntu 24.10 (Oracular Oriole) - 2024년 10월 예정
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

  # Ubuntu 18.04 LTS (Bionic Beaver) - EOL
  bionic: focal

# 저장소 결정 로직
ceph_stable_release_deb: "{{ ubuntu_ceph_repo_mapping[ansible_distribution_release] | default('jammy') }}"

# 동적 저장소 URL 생성
ceph_apt_repo_url: "deb {{ ceph_mirror }}/debian-{{ ceph_release }}/ {{ ceph_stable_release_deb }} main"
```

### 2. 인벤토리 파일 설정

```yaml
# hosts.yaml
all:
  # group_vars/all.yml의 변수를 자동으로 사용
  children:
    mons:
      hosts:
        mon1:
          ansible_host: 10.10.2.91
        mon2:
          ansible_host: 10.10.2.92
        mon3:
          ansible_host: 10.10.2.93
```

## 🚀 구현 방법

### 1단계: group_vars 디렉토리 생성

```bash
mkdir -p group_vars
```

### 2단계: all.yml 파일 생성

위의 중앙 집중식 구성 내용으로 `group_vars/all.yml` 파일을 생성합니다.

### 3단계: 배포 실행

```bash
# Preflight 체크
ansible-playbook -i hosts.yaml cephadm-preflight.yml

# 클러스터 부트스트랩
ansible-playbook -i hosts.yaml cephadm-bootstrap.yml
```

## 🔧 대안 솔루션

### 방법 1: 인벤토리 내 직접 매핑

hosts.yaml에 직접 매핑을 포함시키는 방법:

```yaml
all:
  vars:
    ubuntu_to_ceph_repo_map:
      noble: jammy
      mantic: jammy
      lunar: jammy
      jammy: jammy
      focal: focal

    ceph_stable_release_deb: "{{ ubuntu_to_ceph_repo_map[ansible_distribution_release] | default(ansible_distribution_release) }}"
```

### 방법 2: Ubuntu 공식 저장소 사용

Ubuntu 24.04는 기본적으로 Ceph 19.2.1을 포함:

```yaml
all:
  vars:
    ceph_origin: distro  # Ubuntu 저장소 사용
```

### 방법 3: Ubuntu Cloud Archive 사용

최신 Ceph 버전이 필요한 경우:

```bash
sudo add-apt-repository cloud-archive:caracal
sudo apt update
sudo apt install ceph ceph-common cephadm
```

## 📊 각 방법의 장단점

| 방법 | 장점 | 단점 | 사용 시나리오 |
|-----|------|------|--------------|
| Ubuntu 저장소 (distro) | 설정 불필요, Squid 19.2.0 제공, 가장 안정적 | 특정 버전 선택 불가 | **Ubuntu 24.04 권장** ✅ |
| group_vars/all.yml | 중앙 관리, 확장성 우수, 재사용 가능 | 초기 설정 필요 | 프로덕션, 다중 환경 |
| 인벤토리 직접 매핑 | 단순, 빠른 설정 | 인벤토리 파일 복잡 | 테스트, 단일 환경 |
| Cloud Archive | 최신 버전 | 추가 저장소 필요 | 최신 기능 필요 시 |

## ⚠️ 주의 사항

1. **호환성 확인**: Jammy 저장소의 패키지가 Noble에서 정상 작동하는지 테스트
2. **의존성 충돌**: 일부 의존성 패키지 버전 차이로 인한 충돌 가능성
3. **프로덕션 배포**: 충분한 테스트 후 프로덕션 환경에 적용
4. **공식 지원 대기**: Ceph가 공식적으로 Noble을 지원하면 매핑 업데이트

## 🔍 문제 해결

### 저장소 오류 발생 시

```bash
# APT 캐시 정리
sudo apt clean
sudo apt update

# GPG 키 재설치
curl -fsSL https://download.ceph.com/keys/release.asc | sudo apt-key add -
```

### 패키지 충돌 발생 시

```bash
# 특정 버전 고정
sudo apt install ceph=17.2.6-1 ceph-common=17.2.6-1
```

## 📈 향후 계획

### 자동화된 버전 매핑

```yaml
# 향후 구현 예정: 자동 폴백 로직
ceph_stable_release_deb: >-
  {%- if ansible_distribution_version is version('22.10', '>=') -%}
    jammy
  {%- elif ansible_distribution_version is version('20.04', '>=') -%}
    {{ ansible_distribution_release }}
  {%- else -%}
    focal
  {%- endif -%}
```

### CI/CD 통합

```yaml
# .gitlab-ci.yml 예제
test_ubuntu_versions:
  stage: test
  parallel:
    matrix:
      - UBUNTU_VERSION: ["20.04", "22.04", "24.04"]
  script:
    - ansible-playbook -i hosts.yaml cephadm-preflight.yml
```

## 📚 참고 자료

- [Ceph 공식 다운로드 페이지](https://download.ceph.com/)
- [Ubuntu 릴리스 일정](https://wiki.ubuntu.com/Releases)
- [cephadm-ansible GitHub](https://github.com/ceph/cephadm-ansible)
- [Ubuntu Cloud Archive](https://wiki.ubuntu.com/OpenStack/CloudArchive)

---

*이 문서는 Ubuntu 24.04 Noble Numbat에서 Ceph를 성공적으로 배포하기 위한 가이드입니다. 새로운 Ubuntu 버전이 출시될 때마다 이 문서의 매핑 테이블을 업데이트하여 지속적인 호환성을 유지할 수 있습니다.*