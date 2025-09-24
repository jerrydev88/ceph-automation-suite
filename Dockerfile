# ===== Stage 1: UV 설치 및 Python 의존성 빌드 =====
FROM python:3.11-alpine AS uv-builder

# UV 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 빌드 도구 설치 (Alpine용)
RUN apk add --no-cache gcc musl-dev libffi-dev openssl-dev python3-dev

# 작업 디렉토리
WORKDIR /app

# Python 의존성 파일 복사
COPY pyproject.toml README.md CLAUDE.md ./

# UV를 사용한 의존성 설치 (.venv에 설치)
# pyproject.toml의 의존성을 설치 (editable 모드로 설치)
RUN uv venv .venv && \
    uv pip install --python .venv/bin/python -e .

# ===== Stage 2: cephadm-ansible 빌드 =====
FROM alpine:3.19 AS cephadm-builder

# Git 설치 (cephadm-ansible 클론용)
RUN apk add --no-cache git

# cephadm-ansible 클론 (특정 버전 고정)
RUN git clone --depth 1 --branch v3.1.0 https://github.com/ceph/cephadm-ansible.git /opt/cephadm-ansible

# ===== Stage 3: 최종 런타임 이미지 =====
FROM python:3.11-alpine

LABEL maintainer="pigeon@mocomsys.com"
LABEL description="Ceph Automation Suite with embedded cephadm-ansible (Alpine)"
LABEL version="1.0.0"

# 환경 변수 설정
ENV ANSIBLE_HOST_KEY_CHECKING=False \
    ANSIBLE_RETRY_FILES_ENABLED=False \
    PYTHONUNBUFFERED=1 \
    PATH="/opt/ceph-automation/.venv/bin:$PATH" \
    VIRTUAL_ENV=/opt/ceph-automation/.venv

# 런타임 필수 패키지만 설치 (Alpine)
RUN apk add --no-cache \
        openssh-client \
        git \
        sudo \
        bash \
        ca-certificates \
        libffi \
        && rm -rf /var/cache/apk/*

# 사용자 생성 (보안 강화)
RUN adduser -D -s /bin/bash -u 1000 ansible && \
    echo "ansible ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# 작업 디렉토리 생성
WORKDIR /opt/ceph-automation

# Stage 1에서 빌드한 Python 가상환경 복사 (소유권 설정 없이)
COPY --from=uv-builder /app/.venv /opt/ceph-automation/.venv

# venv 경로 수정 (shebang 업데이트) 및 불필요한 파일 제거
RUN find /opt/ceph-automation/.venv/bin -type f -exec sed -i 's|/app/.venv|/opt/ceph-automation/.venv|g' {} \; && \
    # Python 캐시 제거
    find /opt/ceph-automation/.venv -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/ceph-automation/.venv -type f -name "*.pyc" -delete 2>/dev/null || true && \
    find /opt/ceph-automation/.venv -type f -name "*.pyo" -delete 2>/dev/null || true && \
    # ansible_test 제거 (큰 용량)
    rm -rf /opt/ceph-automation/.venv/lib/python*/site-packages/ansible_test && \
    # 문서 및 예제 제거
    rm -rf /opt/ceph-automation/.venv/lib/python*/site-packages/*/examples && \
    rm -rf /opt/ceph-automation/.venv/lib/python*/site-packages/*/docs && \
    rm -rf /opt/ceph-automation/.venv/lib/python*/site-packages/*/*.md && \
    rm -rf /opt/ceph-automation/.venv/lib/python*/site-packages/*/*.rst && \
    # pip 캐시 제거
    rm -rf /opt/ceph-automation/.venv/lib/python*/site-packages/pip* && \
    rm -rf /opt/ceph-automation/.venv/lib/python*/site-packages/setuptools* && \
    rm -rf /opt/ceph-automation/.venv/lib/python*/site-packages/wheel*

# Stage 2에서 클론한 cephadm-ansible 복사
COPY --from=cephadm-builder /opt/cephadm-ansible /opt/cephadm-ansible

# UV 바이너리 복사 (추가 패키지 설치가 필요한 경우를 위해)
COPY --from=uv-builder /usr/local/bin/uv /usr/local/bin/uv

# Ceph Automation Suite 복사 (필요한 파일만)
COPY --chown=ansible:ansible playbooks /opt/ceph-automation/playbooks
COPY --chown=ansible:ansible inventory /opt/ceph-automation/inventory
COPY --chown=ansible:ansible group_vars /opt/ceph-automation/group_vars
COPY --chown=ansible:ansible ansible.cfg docker-entrypoint.sh pyproject.toml README.md CLAUDE.md /opt/ceph-automation/

# 심볼릭 링크 생성 및 권한 설정을 한 번에 처리
RUN ln -sf /opt/cephadm-ansible/cephadm-preflight.yml /opt/ceph-automation/cephadm-preflight.yml && \
    ln -sf /opt/cephadm-ansible/cephadm-bootstrap.yml /opt/ceph-automation/cephadm-bootstrap.yml && \
    chmod +x /opt/ceph-automation/docker-entrypoint.sh && \
    # 소유권을 한 번에 변경 (레이어 최적화)
    chown -R ansible:ansible /opt/ceph-automation /opt/cephadm-ansible

# 사용자 전환
USER ansible

# 볼륨 마운트 포인트 (사용자 홈 디렉토리)
VOLUME ["/opt/ceph-automation/inventory"]
VOLUME ["/home/ansible/.ssh"]

# 헬스체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD ansible --version || exit 1

# 엔트리포인트 설정
ENTRYPOINT ["/opt/ceph-automation/docker-entrypoint.sh"]
CMD ["bash"]