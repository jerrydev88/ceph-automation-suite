.PHONY: help build run shell deploy validate clean lint format test

# 버전 정보 (VERSION 파일에서 읽기)
VERSION := $(shell cat VERSION 2>/dev/null || echo "0.0.1")

# 쉘 설정 (macOS에서 zsh 사용)
SHELL := /bin/zsh

# 컨테이너 런타임 감지
CONTAINER_CHECK := $(shell command -v container 2>/dev/null)
ifdef CONTAINER_CHECK
    CONTAINER_RUNTIME := container
else
    CONTAINER_RUNTIME := docker
endif

# Compose 도구 감지
ifeq ($(CONTAINER_RUNTIME),container)
    # Container-Compose 확인
    CONTAINER_COMPOSE_EXISTS := $(shell command -v container-compose 2>/dev/null)
    ifdef CONTAINER_COMPOSE_EXISTS
        COMPOSE_CMD := container-compose
        COMPOSE_FILE := container-compose.yml
    else
        COMPOSE_CMD := @echo "⚠️  Container-Compose가 설치되지 않았습니다. './scripts/setup-container-compose.sh'를 실행하세요"
        COMPOSE_FILE :=
    endif
else
    COMPOSE_CMD := docker-compose
    COMPOSE_FILE := docker-compose.yml
endif

# 기본 타겟
help:
	@echo "Ceph Automation Suite - Make 타겟"
	@echo "=================================="
	@echo "감지된 컨테이너 런타임: $(CONTAINER_RUNTIME)"
	@echo "감지된 Compose 도구: $(COMPOSE_CMD)"
	@echo ""
	@echo "컨테이너 명령어:"
	@echo "  make build          - 컨테이너 이미지 빌드"
	@echo "  make run            - 컨테이너 실행 (대화형)"
	@echo "  make shell          - 실행 중인 컨테이너에 쉘 접속"
	@echo "  make deploy         - Ceph 클러스터 배포"
	@echo "  make validate       - 클러스터 검증 실행"
	@echo ""
	@echo "로컬 개발:"
	@echo "  make install        - UV를 사용한 로컬 설치"
	@echo "  make lint           - 코드 린팅"
	@echo "  make format         - 코드 포매팅"
	@echo "  make test           - 테스트 실행"
	@echo "  make clean          - 캐시 및 빌드 아티팩트 제거"
	@echo ""
	@echo "유틸리티:"
	@echo "  make check-deps     - 의존성 확인"
	@echo "  make update-deps    - 의존성 업데이트"
	@echo "  make size           - Docker 이미지 크기 확인"
	@echo "  make import-to-container - Docker 이미지를 macOS Container로 가져오기"
	@echo ""
	@echo "버전 관리:"
	@echo "  make version        - 현재 버전 확인"
	@echo "  make bump-patch     - 패치 버전 증가 (0.0.x)"
	@echo "  make bump-minor     - 마이너 버전 증가 (0.x.0)"
	@echo "  make bump-major     - 메이저 버전 증가 (x.0.0)"
	@echo "  make release-patch  - 패치 릴리스 (bump + commit + tag)"
	@echo "  make release-minor  - 마이너 릴리스 (bump + commit + tag)"
	@echo "  make release-major  - 메이저 릴리스 (bump + commit + tag)"

# 컨테이너 타겟 (Docker Buildx로 통일 빌드)
build:
	@echo "🔨 Docker Buildx로 이미지 빌드 중 (v$(VERSION))..."
	@docker buildx build --build-arg VERSION=$(VERSION) -t ceph-automation-suite:$(VERSION) -t ceph-automation-suite:latest .
ifeq ($(CONTAINER_RUNTIME),container)
	@echo "🍎 macOS Container로 이미지 가져오기..."
	@docker save ceph-automation-suite:latest -o /tmp/ceph-automation-suite.tar
	@container images load -i /tmp/ceph-automation-suite.tar
	@rm -f /tmp/ceph-automation-suite.tar
endif

build-cache:
	@echo "🔨 Docker Buildx로 이미지 빌드 중 (캐시 사용, v$(VERSION))..."
	@docker buildx build --build-arg VERSION=$(VERSION) -t ceph-automation-suite:$(VERSION) -t ceph-automation-suite:latest .
ifeq ($(CONTAINER_RUNTIME),container)
	@echo "🍎 macOS Container로 이미지 가져오기..."
	@docker save ceph-automation-suite:latest -o /tmp/ceph-automation-suite.tar
	@container images load -i /tmp/ceph-automation-suite.tar
	@rm -f /tmp/ceph-automation-suite.tar
endif

run:
ifeq ($(CONTAINER_RUNTIME),container)
	@echo "🍎 macOS Container로 실행..."
	@container run --rm -it \
		-v $(PWD)/inventory:/opt/ceph-automation/inventory \
		-v ~/.ssh:/home/ansible/.ssh:ro \
		docker.io/library/ceph-automation-suite:latest bash
else
	@echo "🐳 Docker로 컨테이너 실행..."
	@docker run --rm -it \
		-v $(PWD)/inventory:/opt/ceph-automation/inventory \
		-v ~/.ssh:/home/ansible/.ssh:ro \
		ceph-automation-suite:latest bash
endif

shell:
ifeq ($(CONTAINER_RUNTIME),container)
	@echo "🍎 macOS Container 쉘 접속..."
	@container exec -it ceph-automation bash
else
	@echo "🐳 Docker 컨테이너 쉘 접속..."
	@docker exec -it ceph-automation bash
endif

deploy:
ifeq ($(CONTAINER_RUNTIME),container)
	@echo "🍎 macOS Container로 Ceph 클러스터 배포..."
	@container run --rm \
		-v $(PWD)/inventory:/opt/ceph-automation/inventory \
		-v ~/.ssh:/home/ansible/.ssh:ro \
		docker.io/library/ceph-automation-suite:latest \
		ansible-playbook -i inventory/hosts-scalable.yml \
		playbooks/01-deployment/complete-deployment-docker.yml
else
	@echo "🐳 Docker로 Ceph 클러스터 배포..."
	@docker run --rm \
		-v $(PWD)/inventory:/opt/ceph-automation/inventory \
		-v ~/.ssh:/home/ansible/.ssh:ro \
		ceph-automation-suite:latest \
		ansible-playbook -i inventory/hosts-scalable.yml \
		playbooks/01-deployment/complete-deployment-docker.yml
endif

validate:
ifeq ($(CONTAINER_RUNTIME),container)
	@echo "🍎 macOS Container로 클러스터 검증..."
	@container run --rm \
		-v $(PWD)/inventory:/opt/ceph-automation/inventory \
		docker.io/library/ceph-automation-suite:latest \
		ansible-playbook -i inventory/hosts-scalable.yml \
		playbooks/04-validation/validate-all.yml
else
	@echo "🐳 Docker로 클러스터 검증..."
	@docker run --rm \
		-v $(PWD)/inventory:/opt/ceph-automation/inventory \
		ceph-automation-suite:latest \
		ansible-playbook -i inventory/hosts-scalable.yml \
		playbooks/04-validation/validate-all.yml
endif

# 로컬 개발 타겟
install:
	@echo "📦 UV를 사용한 로컬 설치..."
	@bash scripts/install-with-uv.sh

install-uv:
	@echo "📦 UV 설치..."
	@curl -LsSf https://astral.sh/uv/install.sh | sh

venv:
	@echo "🐍 가상환경 생성..."
	@uv venv .venv --python 3.11
	@echo "✓ 활성화: source .venv/bin/activate"

deps:
	@echo "📚 의존성 설치..."
	@uv pip install -e .

deps-dev:
	@echo "📚 개발 의존성 설치..."
	@uv pip install -e ".[dev]"

# 코드 품질 타겟
lint:
	@echo "🔍 코드 린팅..."
	@ansible-lint playbooks/**/*.yml || true
	@yamllint -c .yamllint playbooks/**/*.yml || true

format:
	@echo "✨ 코드 포매팅..."
	@find . -name "*.py" -type f -exec ruff format {} \;

test:
	@echo "🧪 테스트 실행..."
	@pytest tests/ -v

# 유틸리티 타겟
check-deps:
	@echo "🔍 의존성 확인..."
	@uv pip list

update-deps:
	@echo "⬆️  의존성 업데이트..."
	@uv pip install --upgrade -e .

size:
	@echo "📊 Docker 이미지 크기:"
	@docker images ceph-automation-suite:latest --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

clean:
	@echo "🧹 클린업..."
	@rm -rf .venv __pycache__ .pytest_cache .ansible-cache
	@rm -f *.pyc 2>/dev/null || true
	@rm -f logs/*.log 2>/dev/null || true
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@docker-compose down -v 2>/dev/null || true

clean-docker:
	@echo "🐳 Docker 클린업..."
	@docker-compose down -v 2>/dev/null || true
	@docker rmi ceph-automation-suite:latest 2>/dev/null || true
ifeq ($(CONTAINER_RUNTIME),container)
	@echo "🍎 Container 이미지 클린업..."
	@container images rm docker.io/library/ceph-automation-suite:latest 2>/dev/null || true
endif

# Docker에서 Container로 이미지 가져오기
import-to-container:
	@echo "📦 Docker 이미지를 Container로 가져오기..."
	@docker save ceph-automation-suite:latest -o /tmp/ceph-automation-suite.tar
	@container images load -i /tmp/ceph-automation-suite.tar
	@rm -f /tmp/ceph-automation-suite.tar

# 캐시 디렉토리 생성
cache-dir:
	@mkdir -p .ansible-cache logs

# 인벤토리 초기화
init-inventory:
	@echo "📝 인벤토리 파일 초기화..."
	@cp inventory/hosts-scalable.yml.example inventory/hosts-scalable.yml
	@echo "✓ inventory/hosts-scalable.yml 생성됨 - 실제 호스트 정보를 입력하세요"

# 전체 초기화
init: cache-dir init-inventory install
	@echo "✅ 프로젝트 초기화 완료!"

# 버전 관련 타겟
version:
	@echo "현재 버전: v$(VERSION)"

update-version:
	@echo "📦 버전을 $(VERSION)으로 업데이트 중..."
	@./scripts/update-version.sh
	@echo "✅ 버전 업데이트 완료!"

bump-patch:
	@echo "🔧 Patch 버전 증가..."
	@./scripts/bump-version.sh patch

bump-minor:
	@echo "✨ Minor 버전 증가..."
	@./scripts/bump-version.sh minor

bump-major:
	@echo "🚀 Major 버전 증가..."
	@./scripts/bump-version.sh major

release-patch: bump-patch
	@git add -A
	@git commit -m "chore: bump version to v$$(cat VERSION)"
	@git tag -a v$$(cat VERSION) -m "Release v$$(cat VERSION)"
	@echo "✅ Patch 릴리스 준비 완료! 'git push && git push --tags'로 배포하세요."

release-minor: bump-minor
	@git add -A
	@git commit -m "chore: bump version to v$$(cat VERSION)"
	@git tag -a v$$(cat VERSION) -m "Release v$$(cat VERSION)"
	@echo "✅ Minor 릴리스 준비 완료! 'git push && git push --tags'로 배포하세요."

release-major: bump-major
	@git add -A
	@git commit -m "chore: bump version to v$$(cat VERSION)"
	@git tag -a v$$(cat VERSION) -m "Release v$$(cat VERSION)"
	@echo "✅ Major 릴리스 준비 완료! 'git push && git push --tags'로 배포하세요."

tag:
	@echo "🏷️  Git 태그 v$(VERSION) 추가..."
	@git tag -a v$(VERSION) -m "Release v$(VERSION)"
	@echo "✅ 태그 생성 완료! 'git push --tags'로 푸시할 수 있습니다."

# Container-Compose 관련
install-container-compose:
	@echo "📦 Container-Compose 설치..."
	@chmod +x scripts/setup-container-compose.sh
	@./scripts/setup-container-compose.sh

compose-up:
ifdef CONTAINER_COMPOSE_EXISTS
	@echo "🚀 Container-Compose로 서비스 시작..."
	@$(COMPOSE_CMD) up -d
else
	@echo "⚠️  Container-Compose가 설치되지 않았습니다."
	@echo "실행: make install-container-compose"
endif

compose-down:
ifdef CONTAINER_COMPOSE_EXISTS
	@echo "🛑 Container-Compose 서비스 중지..."
	@$(COMPOSE_CMD) down
else
	@echo "⚠️  Container-Compose가 설치되지 않았습니다."
endif

compose-ps:
ifdef CONTAINER_COMPOSE_EXISTS
ifeq ($(CONTAINER_RUNTIME),container)
	@echo "⚠️  Container-Compose는 'ps' 명령을 지원하지 않습니다."
	@echo "대신 'container ps'를 사용하세요."
else
	@docker-compose ps
endif
else
	@echo "⚠️  Container-Compose가 설치되지 않았습니다."
endif

compose-logs:
ifdef CONTAINER_COMPOSE_EXISTS
ifeq ($(CONTAINER_RUNTIME),container)
	@echo "⚠️  Container-Compose는 'logs' 명령을 지원하지 않습니다."
	@echo "대신 'container logs <container-name>'을 사용하세요."
else
	@docker-compose logs -f
endif
else
	@echo "⚠️  Container-Compose가 설치되지 않았습니다."
endif