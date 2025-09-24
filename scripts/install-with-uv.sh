#!/bin/bash

# UV를 사용한 로컬 개발 환경 설정 스크립트

set -e

echo "🚀 Ceph Automation Suite - UV 기반 설치"
echo "========================================"

# UV 설치 확인
if ! command -v uv &> /dev/null; then
    echo "📦 UV를 설치합니다..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    source $HOME/.cargo/env
fi

echo "✓ UV 버전: $(uv --version)"

# Python 버전 확인 및 설정
echo "🐍 Python 환경 설정..."
uv python install 3.11

# 가상환경 생성
echo "📁 가상환경 생성..."
uv venv .venv --python 3.11

# 의존성 설치
echo "📚 의존성 설치..."
uv pip install -e .

# cephadm-ansible 옵션 제공
echo ""
echo "📋 cephadm-ansible 설치 옵션:"
echo "1) 로컬에 클론 (../cephadm-ansible)"
echo "2) Docker 컨테이너 사용 (권장)"
echo "3) 건너뛰기"
read -p "선택 [1-3]: " choice

case $choice in
    1)
        echo "📥 cephadm-ansible 클론..."
        if [ ! -d "../cephadm-ansible" ]; then
            git clone https://github.com/ceph/cephadm-ansible.git ../cephadm-ansible
            cd ../cephadm-ansible
            uv pip install -r requirements.txt
            cd -
        else
            echo "✓ cephadm-ansible이 이미 존재합니다"
        fi
        ;;
    2)
        echo "🐳 Docker 이미지 빌드..."
        docker-compose build
        echo "✓ Docker 이미지 준비 완료"
        ;;
    3)
        echo "⏭️  cephadm-ansible 설치를 건너뜁니다"
        ;;
esac

# 활성화 스크립트 생성
cat > activate.sh << 'EOF'
#!/bin/bash
# Ceph Automation Suite 환경 활성화

source .venv/bin/activate

echo "✓ Ceph Automation Suite 환경이 활성화되었습니다"
echo ""
echo "사용 가능한 명령:"
echo "  ansible-playbook -i inventory/hosts-scalable.yml playbooks/[플레이북].yml"
echo "  docker-compose run ceph-automation bash  # Docker 환경 사용"
echo ""

export PS1="(ceph-auto) $PS1"
EOF

chmod +x activate.sh

echo ""
echo "✅ 설치 완료!"
echo ""
echo "환경 활성화:"
echo "  source activate.sh"
echo ""
echo "Docker 사용:"
echo "  docker-compose run ceph-automation bash"
echo ""