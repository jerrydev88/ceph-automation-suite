# Troubleshooting Guide

이 디렉토리는 cephadm-ansible 사용 중 발생할 수 있는 다양한 문제들과 해결 방법을 담고 있습니다.

## 목차

### 설치 관련 문제
- [Ubuntu 24.04 cephadm 패키지 설치 오류](./ubuntu-24.04-cephadm-installation.md)
  - dpkg configuration 오류 해결
  - `/var/lib/cephadm/.ssh` 디렉토리 문제

### 네트워크 관련 문제
- SSH 연결 문제 (준비 중)
- 방화벽 설정 (준비 중)

### 성능 관련 문제
- Ansible 실행 속도 최적화 (준비 중)
- 대규모 클러스터 배포 (준비 중)

## 일반적인 디버깅 팁

### 1. Ansible 디버깅
```bash
# 자세한 출력 보기
ansible-playbook -vvv -i hosts.yaml playbook.yml

# 특정 태스크부터 시작
ansible-playbook -i hosts.yaml playbook.yml --start-at-task="task name"

# Dry-run 모드
ansible-playbook -i hosts.yaml playbook.yml --check
```

### 2. 호스트 연결 테스트
```bash
# 모든 호스트 ping 테스트
ansible all -i hosts.yaml -m ping

# 특정 호스트 접속 테스트
ansible mon1 -i hosts.yaml -m setup
```

### 3. 패키지 상태 확인
```bash
# Ubuntu/Debian
ansible all -i hosts.yaml -m shell -a "dpkg -l | grep ceph"

# RHEL/CentOS
ansible all -i hosts.yaml -m shell -a "rpm -qa | grep ceph"
```

## 문제 보고

새로운 문제를 발견하셨다면:

1. GitHub Issues에 보고: https://github.com/ceph/cephadm-ansible/issues
2. 다음 정보 포함:
   - OS 버전
   - Ansible 버전 (`ansible --version`)
   - cephadm-ansible 버전/브랜치
   - 전체 에러 로그
   - 실행한 명령어

## 기여하기

이 문서에 새로운 트러블슈팅 케이스를 추가하려면:

1. 이 디렉토리에 새 마크다운 파일 생성
2. 명확한 제목과 구조 사용
3. 문제 상황, 원인, 해결 방법 포함
4. 실제 명령어와 출력 예시 제공
5. 이 README.md에 링크 추가