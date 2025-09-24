# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.0.1] - 2025-09-24

### 🎉 Initial Release

#### Added
- 초기 프로젝트 구조 설정
- Alpine Linux 기반 Docker 이미지 (645MB)
- UV/UVX를 사용한 현대적인 Python 패키지 관리
- cephadm-ansible 통합
- Ansible 플레이북 구조
  - 00-preparation: 준비 작업
  - 01-deployment: 클러스터 배포
  - 02-services: 서비스 구성 (CephFS, RGW, RBD)
  - 03-operations: 운영 작업
  - 04-validation: 자동화 검증
  - 90-maintenance: 유지보수 작업
- Docker와 macOS Container 지원
- Container-Compose 통합
- 포괄적인 Makefile 워크플로우
- 한국어 우선 문서화

#### Infrastructure
- Multi-stage Docker 빌드
- Docker buildx 지원
- macOS native container 지원
- Git 저장소 초기화

#### Documentation
- README.md (한국어)
- CLAUDE.md (AI 지원 문서)
- DOCKER_USAGE.md
- MACOS_CONTAINER.md

[Unreleased]: https://github.com/mocomsys/ceph-automation-suite/compare/v0.0.1...HEAD
[0.0.1]: https://github.com/mocomsys/ceph-automation-suite/releases/tag/v0.0.1