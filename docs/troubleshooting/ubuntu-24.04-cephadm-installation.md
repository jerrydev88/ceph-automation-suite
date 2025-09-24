# Ubuntu 24.04 cephadm 패키지 설치 오류 해결

## 문제 상황

Ubuntu 24.04에서 `cephadm-preflight.yml` playbook 실행 시 다음과 같은 오류가 발생할 수 있습니다:

### 증상
```
fatal: [mon1]: FAILED! => changed=false
  msg: |-
    '/usr/bin/apt-get -y -o "Dpkg::Options::=--force-confdef" -o "Dpkg::Options::=--force-confold"
    install 'cephadm=19.2.1-0ubuntu0.24.04.2'' failed: E: Sub-process /usr/bin/dpkg returned an error code (1)
  stdout: |-
    Setting up cephadm (19.2.1-0ubuntu0.24.04.2) ...
    mkdir: cannot create directory '/var/lib/cephadm/.ssh': No such file or directory
    dpkg: error processing package cephadm (--configure):
     installed cephadm package post-installation script subprocess returned error exit status 1
```

### 원인 분석
- Ubuntu 24.04의 cephadm 패키지(19.2.1-0ubuntu0.24.04.2)에 버그가 존재
- Post-installation 스크립트가 `/var/lib/cephadm/.ssh` 디렉토리를 생성하려 하지만 부모 디렉토리(`/var/lib/cephadm`)가 없어서 실패
- 패키지는 설치되지만 configuration이 incomplete 상태로 남음

## 해결 방법

### 방법 1: Quick Fix Playbook (권장)

1. 다음 내용으로 `fix-cephadm-ubuntu24.yml` 파일을 생성합니다:

```yaml
---
- name: Fix broken cephadm package on Ubuntu 24.04 hosts
  hosts: all  # 또는 문제가 있는 특정 호스트 지정
  become: true
  gather_facts: false
  tasks:
    - name: Create cephadm directory
      ansible.builtin.file:
        path: /var/lib/cephadm
        state: directory
        mode: '0755'
        owner: root
        group: root

    - name: Reconfigure dpkg to fix broken packages
      ansible.builtin.command: dpkg --configure -a
      register: dpkg_result
      changed_when: dpkg_result.rc == 0

    - name: Verify cephadm is properly installed
      ansible.builtin.command: dpkg -l cephadm
      register: cephadm_status
      changed_when: false
      failed_when: "'ii  cephadm' not in cephadm_status.stdout"
```

2. Fix playbook 실행:
```bash
ansible-playbook -i hosts-scalable.yaml fix-cephadm-ubuntu24.yml
```

3. 원래 playbook 재실행:
```bash
ansible-playbook -i hosts-scalable.yaml cephadm-preflight.yml
```

### 방법 2: Ad-hoc Ansible 명령

문제가 있는 호스트에만 직접 수정:

```bash
# 특정 호스트에만 적용 (예: mon1, mon2)
ansible mon1,mon2 -i hosts-scalable.yaml -m file -a "path=/var/lib/cephadm state=directory mode=0755" --become
ansible mon1,mon2 -i hosts-scalable.yaml -m shell -a "dpkg --configure -a" --become
```

### 방법 3: 수동 SSH 접속 수정

각 호스트에 SSH로 접속하여 직접 수정:

```bash
ssh user@mon1
sudo mkdir -p /var/lib/cephadm
sudo chmod 755 /var/lib/cephadm
sudo dpkg --configure -a
exit
```

## 영구적인 해결책

`cephadm-preflight.yml` playbook을 수정하여 Ubuntu 24.04를 위한 workaround 추가:

```yaml
# cephadm-preflight.yml의 Ubuntu 섹션에 추가
- name: Ubuntu related tasks
  when: ansible_facts['distribution'] == 'Ubuntu'
  block:
    # ... 기존 태스크들 ...

    - name: Fix for Ubuntu 24.04 cephadm directory issue
      when: ansible_facts['distribution_version'] is version('24.04', '>=')
      block:
        - name: Create cephadm directory structure before package installation
          file:
            path: /var/lib/cephadm
            state: directory
            mode: '0755'
            owner: root
            group: root

    - name: install prerequisites packages
      apt:
        name: "{{ ['python3','chrony'] + ceph_pkgs }}"
        # ... 나머지 설정 ...
```

## 검증

문제가 해결되었는지 확인:

```bash
# 모든 호스트에서 cephadm 패키지 상태 확인
ansible all -i hosts-scalable.yaml -m shell -a "dpkg -l | grep cephadm" --become
```

정상적으로 설치된 경우 다음과 같이 표시됩니다:
```
ii  cephadm  19.2.1-0ubuntu0.24.04.2  all  cephadm utility to bootstrap ceph daemons
```

## 관련 이슈

- Ubuntu 24.04 LTS 특정 이슈
- cephadm 패키지 버전: 19.2.1-0ubuntu0.24.04.2
- 영향받는 Ceph 버전: Reef (19.2.x)

## 추가 참고사항

- 이 문제는 Ansible의 멱등성(idempotency) 덕분에 수정 후 playbook을 재실행해도 안전합니다
- 이미 성공적으로 설치된 호스트는 영향을 받지 않습니다
- Ubuntu 패키지 메인테이너에게 버그 리포트가 제출되어야 합니다

---
*최종 업데이트: 2025년 9월*