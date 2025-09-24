# ===== Stage 1: UV 설치 및 Python 의존성 빌드 =====
FROM python:3.11-slim AS uv-builder

# UV 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 작업 디렉토리
WORKDIR /app

# Python 의존성 파일 복사
COPY pyproject.toml .

# UV를 사용한 의존성 설치 (.venv에 설치)
RUN uv venv .venv && \
    uv pip install --python .venv/bin/python -e .

# ===== Stage 2: cephadm-ansible 빌드 =====
FROM python:3.11-slim AS cephadm-builder

# Git 설치 (cephadm-ansible 클론용)
RUN apt-get update && \
    apt-get install -y --no-install-recommends git ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# cephadm-ansible 클론 (특정 버전 고정)
RUN git clone --depth 1 --branch v3.1.0 https://github.com/ceph/cephadm-ansible.git /opt/cephadm-ansible

# ===== Stage 3: 최종 런타임 이미지 =====
FROM python:3.11-slim

LABEL maintainer="jerrydev@mocomsys.com"
LABEL description="Ceph Automation Suite with embedded cephadm-ansible (optimized)"
LABEL version="1.0.0"

# 환경 변수
ENV DEBIAN_FRONTEND=noninteractive \
    ANSIBLE_HOST_KEY_CHECKING=False \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/ceph-automation/.venv/bin:$PATH" \
    VIRTUAL_ENV=/opt/ceph-automation/.venv

# 런타임 필수 패키지만 설치 (최소한)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openssh-client \
        git \
        sudo \
        ca-certificates \
        && rm -rf /var/lib/apt/lists/* \
        && apt-get clean

# 사용자 생성 (보안 강화)
RUN useradd -m -s /bin/bash -u 1000 ansible && \
    echo "ansible ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 작업 디렉토리 생성
WORKDIR /opt/ceph-automation

# Stage 1에서 빌드한 Python 가상환경 복사
COPY --from=uv-builder --chown=ansible:ansible /app/.venv /opt/ceph-automation/.venv

# Stage 2에서 클론한 cephadm-ansible 복사
COPY --from=cephadm-builder --chown=ansible:ansible /opt/cephadm-ansible /opt/cephadm-ansible

# cephadm-ansible 의존성 설치 (가상환경 사용)
RUN if [ -f /opt/cephadm-ansible/requirements.txt ]; then \
        /opt/ceph-automation/.venv/bin/pip install --no-cache-dir -r /opt/cephadm-ansible/requirements.txt; \
    fi

# Ceph Automation Suite 복사
COPY --chown=ansible:ansible . /opt/ceph-automation/

# 심볼릭 링크 생성 (경로 호환성)
RUN ln -sf /opt/cephadm-ansible/cephadm-preflight.yml /opt/ceph-automation/cephadm-preflight.yml && \
    ln -sf /opt/cephadm-ansible/cephadm-bootstrap.yml /opt/ceph-automation/cephadm-bootstrap.yml

# 엔트리포인트 스크립트 권한 설정
RUN chmod +x /opt/ceph-automation/docker-entrypoint.sh

# 디렉토리 권한 설정
RUN chown -R ansible:ansible /opt/ceph-automation

# 사용자 전환
USER ansible

# 볼륨 마운트 포인트 (사용자 홈 디렉토리)
VOLUME ["/opt/ceph-automation/inventory"]
VOLUME ["/home/ansible/.ssh"]

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ansible --version || exit 1

ENTRYPOINT ["/opt/ceph-automation/docker-entrypoint.sh"]
CMD ["bash"]