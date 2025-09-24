# Ceph Automation Suite 변수 구조

## 변수 파일 위치

### 1. `ceph-vars.yml` (프로젝트 루트)
- **위치**: `/ceph-vars.yml`
- **용도**: Ceph 클러스터 전체 설정
- **포함 내용**:
  - CephFS 설정
  - RGW (Object Storage) 설정
  - RBD (Block Storage) 설정
  - CSI 사용자 설정
  - 결과 파일 경로

### 2. `group_vars/all.yml`
- **위치**: `/group_vars/all.yml`
- **용도**: Ansible 전역 변수
- **포함 내용**:
  - Ansible 동작 설정
  - 공통 경로 설정
  - 기본값 설정

### 3. `inventory/hosts-scalable.yml`
- **위치**: `/inventory/hosts-scalable.yml`
- **용도**: 호스트별 변수 및 그룹 변수
- **포함 내용**:
  - 호스트 IP 주소
  - SSH 연결 정보
  - 호스트별 특수 설정

## 변수 우선순위 (낮음 → 높음)

1. `group_vars/all.yml` - 기본값
2. `group_vars/{group_name}.yml` - 그룹별 설정
3. `host_vars/{host_name}.yml` - 호스트별 설정
4. `ceph-vars.yml` - Ceph 특화 설정 (vars_files로 명시적 로드)
5. 플레이북 내 vars - 플레이북 로컬 변수
6. 명령줄 `-e` 옵션 - 최우선 순위

## 파일 관리 지침

### `ceph-vars.yml` 관리

1. **보안**:
   - 실제 파일은 `.gitignore`에 추가
   - `ceph-vars.yml.example` 템플릿 제공
   - 민감한 정보는 Ansible Vault 사용

2. **버전 관리**:
   ```bash
   # 예제 파일은 버전 관리
   git add ceph-vars.yml.example

   # 실제 파일은 제외
   echo "ceph-vars.yml" >> .gitignore
   ```

3. **초기 설정**:
   ```bash
   # 예제에서 실제 파일 생성
   cp ceph-vars.yml.example ceph-vars.yml

   # 환경에 맞게 수정
   vi ceph-vars.yml
   ```

## 변수 구조 예시

### Ceph 변수 구조 (`ceph-vars.yml`)
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
      users:
        - user_id: "admin"
          buckets:
            - name: "bucket1"
              quota: "80GB"

  rbd:
    - pool_name: rbd-oa
      pool_pg_num: 16
      images: []

  csi:
    - cluster_name: "k8s"
      ceph_csi_user: "csi-rbd-user"
```

### 그룹 변수 구조 (`group_vars/all.yml`)
```yaml
# Ansible 설정
ansible_python_interpreter: /usr/bin/python3
gather_facts: yes

# 공통 경로
ceph_config_dir: /etc/ceph
ceph_data_dir: /var/lib/ceph

# 기본값
default_timeout: 300
retry_count: 3
```

## 플레이북에서 변수 사용

### 1. vars_files 사용 (명시적 로드)
```yaml
- name: Configure Ceph Services
  hosts: all
  vars_files:
    - ../../ceph-vars.yml  # 상대 경로로 로드
  tasks:
    - name: Use Ceph variable
      debug:
        msg: "CephFS name: {{ ceph.cephfs[0].name }}"
```

### 2. group_vars 자동 로드
```yaml
- name: Common Tasks
  hosts: all
  tasks:
    - name: Use group variable
      debug:
        msg: "Python: {{ ansible_python_interpreter }}"
```

## 권장 사항

1. **환경별 분리**: 개발/스테이징/운영 환경별 변수 파일 분리
2. **민감 정보 암호화**: Ansible Vault 사용
3. **변수 명명 규칙**:
   - Ceph 관련: `ceph_*` 접두사
   - 환경 관련: `env_*` 접두사
   - 앱 관련: `app_*` 접두사
4. **문서화**: 각 변수의 용도와 가능한 값 범위 명시
5. **검증**: 변수 값 검증 태스크 추가

## 디버깅

변수 확인 방법:
```bash
# 특정 호스트의 모든 변수 확인
ansible -i inventory/hosts-scalable.yml hostname -m debug -a "var=hostvars[inventory_hostname]"

# 특정 변수 확인
ansible-playbook playbooks/debug-vars.yml -e "target_var=ceph"
```