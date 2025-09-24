#!/bin/bash

echo "================================================"
echo " Ceph Automation Suite with cephadm-ansible"
echo "================================================"
echo ""
echo "환경 정보:"
echo "  Python: $(python --version 2>&1)"
echo "  Ansible: $(ansible --version | head -1)"
echo "  사용자: $(whoami)"
echo ""
echo "사용 가능한 명령어:"
echo "  ansible-playbook -i inventory/hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml"
echo "  ansible-playbook -i inventory/hosts-scalable.yml playbooks/04-validation/validate-all.yml"
echo ""
echo "프로젝트 위치:"
echo "  cephadm-ansible: /opt/cephadm-ansible"
echo "  Ceph Automation Suite: /opt/ceph-automation"
echo ""

# SSH 에이전트 설정 (필요한 경우)
SSH_DIR="/home/ansible/.ssh"
if [ -f "$SSH_DIR/id_rsa" ]; then
    eval "$(ssh-agent -s)" >/dev/null 2>&1
    ssh-add "$SSH_DIR/id_rsa" 2>/dev/null
    echo "✓ SSH 키가 로드되었습니다"
fi

# 권한 문제 해결 (볼륨 마운트시)
if [ -d "/opt/ceph-automation/inventory" ]; then
    sudo chown -R ansible:ansible /opt/ceph-automation/inventory 2>/dev/null || true
fi

# UV가 설치되어 있는 경우 표시
if command -v uvx &> /dev/null; then
    echo "✓ UV/UVX 사용 가능"
fi

# 명령어가 전달된 경우 실행, 그렇지 않으면 bash 쉘
exec "$@"