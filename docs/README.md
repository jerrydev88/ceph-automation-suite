# Cephadm-Ansible 문서

이 문서는 cephadm-ansible 프로젝트의 포괄적인 가이드와 참조 자료를 제공합니다.

## 📚 문서 구조

### [🚀 시작하기](./getting-started/)
- [프로젝트 소개](./getting-started/introduction.md)
- [빠른 시작 가이드](./getting-started/quick-start.md)
- [실제 환경 빠른 시작](./getting-started/real-world-quickstart.md) 🆕
- [기본 개념](./getting-started/concepts.md)
- [아키텍처 개요](./getting-started/architecture.md)

### [📦 설치 및 설정](./installation/)
- [시스템 요구사항](./installation/requirements.md)
- [설치 가이드](./installation/install.md)
- [Ubuntu 24.04 (Noble) 지원](./installation/ubuntu-noble-support.md) 🆕
- [초기 설정](./installation/initial-setup.md)

### [📖 플레이북 가이드](./playbooks/)
- [플레이북 개요](./playbooks/overview.md)
- [핵심 플레이북](./playbooks/core-playbooks.md)
- [커스텀 플레이북](./playbooks/custom-playbooks.md)
- [실행 워크플로우](./playbooks/workflows.md)

### [✅ 검증 및 테스트](./validation/) 🆕
- [자동 검증 시스템](./validation/automated-validation.md)
- [클러스터 상태 검증](./validation/cluster-health.md)
- [스토리지 서비스 검증](./validation/storage-services.md)
- [CSI 사용자 검증](./validation/csi-validation.md)
- [검증 플레이북 사용법](./validation/validation-playbooks.md)

### [⚙️ 구성 관리](./configuration/)
- [인벤토리 구성](./configuration/inventory.md) 🆕
- [중앙 구성 파일](./configuration/central-config.md)
- [스토리지 서비스 구성](./configuration/storage-services.md)
- [Kubernetes 통합](./configuration/kubernetes-integration.md)
- [RGW 및 S3 설정](./configuration/rgw-s3.md)

### [🔧 운영 가이드](./operations/)
- [일상 운영 작업](./operations/daily-operations.md)
- [스냅샷 관리](./operations/snapshot-management.md)
- [사용자 및 권한 관리](./operations/user-management.md)
- [모니터링 및 유지보수](./operations/monitoring.md)
- [문제 해결](./operations/troubleshooting.md)

### [💻 개발 가이드](./development/)
- [개발 환경 설정](./development/dev-environment.md)
- [기여 가이드라인](./development/contributing.md)
- [테스트 전략](./development/testing.md)
- [모범 사례](./development/best-practices.md)

### [📋 참조 문서](./reference/)
- [변수 참조](./reference/variables.md)
- [플레이북 API](./reference/playbook-api.md)
- [명령어 참조](./reference/commands.md)
- [용어집](./reference/glossary.md)

---

## 🎯 빠른 링크

### 주요 작업별 가이드

| 작업 | 문서 링크 |
|------|-----------|
| Ceph 클러스터 초기 설정 | [빠른 시작 가이드](./getting-started/quick-start.md) |
| 실제 환경 배포 가이드 | [실제 환경 빠른 시작](./getting-started/real-world-quickstart.md) |
| 완전 자동화 배포 | [complete-deployment.yml 사용법](./playbooks/custom-playbooks.md#complete-deployment) |
| Ubuntu 24.04에서 Ceph 설치 | [Ubuntu Noble 지원 가이드](./installation/ubuntu-noble-support.md) |
| 인벤토리 구성 | [인벤토리 구성 가이드](./configuration/inventory.md) |
| 스토리지 서비스 구성 | [스토리지 서비스 구성](./configuration/storage-services.md) |
| 클러스터 검증 및 테스트 | [검증 플레이북 사용법](./validation/validation-playbooks.md) 🆕 |
| RGW 사용자 관리 | [사용자 및 권한 관리](./operations/user-management.md) |
| 스냅샷 생성 및 관리 | [스냅샷 관리](./operations/snapshot-management.md) |
| Kubernetes CSI 설정 | [Kubernetes 통합](./configuration/kubernetes-integration.md) |
| 클러스터 제거 | [운영 가이드 - 클러스터 제거](./operations/daily-operations.md#cluster-removal) |

### 플레이북 빠른 참조

| 카테고리 | 플레이북 | 용도 | 문서 |
|---------|----------|------|------|
| **핵심** | `cephadm-preflight.yml` | 호스트 준비 | [핵심 플레이북](./playbooks/core-playbooks.md#preflight) |
| **핵심** | `cephadm-clients.yml` | 클라이언트 설정 | [핵심 플레이북](./playbooks/core-playbooks.md#clients) |
| **핵심** | `cephadm-purge-cluster.yml` | 클러스터 제거 | [핵심 플레이북](./playbooks/core-playbooks.md#purge) |
| **배포** | `playbooks/01-deployment/complete-deployment.yml` | 완전 자동화 배포 | [커스텀 플레이북](./playbooks/custom-playbooks.md#complete-deployment) |
| **배포** | `playbooks/01-deployment/bootstrap.yml` | 클러스터 부트스트랩 | [커스텀 플레이북](./playbooks/custom-playbooks.md#bootstrap) |
| **서비스** | `playbooks/02-services/configure-*.yml` | 스토리지 서비스 구성 | [커스텀 플레이북](./playbooks/custom-playbooks.md#services) |
| **검증** | `playbooks/04-validation/validate-all.yml` | 전체 시스템 검증 | [커스텀 플레이북](./playbooks/custom-playbooks.md#validation) |
| **운영** | `playbooks/03-operations/*.yml` | 운영 작업 | [커스텀 플레이북](./playbooks/custom-playbooks.md#operations) |

---

## 📊 프로젝트 현황

- **브랜치**: devel
- **지원 Ceph 버전**: Pacific, Quincy, Reef, Squid
- **지원 플랫폼**: RHEL 8/9, CentOS 8/9, Ubuntu 20.04/22.04/24.04

## 🤝 기여하기

프로젝트에 기여하려면 [기여 가이드라인](./development/contributing.md)을 참조하세요.

## 📝 라이선스

이 프로젝트는 Apache-2.0 라이선스 하에 배포됩니다.

## 🔗 관련 링크

- [Ceph 공식 문서](https://docs.ceph.com/)
- [cephadm 문서](https://docs.ceph.com/en/latest/cephadm/)
- [Ansible 문서](https://docs.ansible.com/)
- [프로젝트 GitHub](https://github.com/ceph/cephadm-ansible)

---

*최종 업데이트: 2025-09-24*
