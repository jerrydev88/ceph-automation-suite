# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 🚨 중요: 언어 설정 / IMPORTANT: Language Setting

**이 프로젝트는 한국어 사용자를 위해 개발되었습니다. 모든 응답과 설명은 한국어를 우선으로 제공해야 합니다.**

**This project was developed for Korean users. All responses and explanations should be provided in Korean as the primary language.**

- 코드 주석: 한국어 우선
- 오류 메시지 설명: 한국어로 제공
- 기술 문서: 한국어 작성
- 커밋 메시지: 한국어 권장

## Commands and Development Tasks

### Building and Testing

```bash
# Install dependencies
pip install -r requirements.txt

# Validate Ansible playbooks syntax
ansible-playbook --syntax-check playbooks/**/*.yml

# Run with verbose output for debugging
ansible-playbook -i inventory/hosts-scalable.yml playbooks/[playbook].yml -vvv

# Dry run (check mode)
ansible-playbook -i inventory/hosts-scalable.yml playbooks/[playbook].yml --check

# List available tags in a playbook
ansible-playbook -i inventory/hosts-scalable.yml playbooks/[playbook].yml --list-tags

# Run specific tags only
ansible-playbook -i inventory/hosts-scalable.yml playbooks/[playbook].yml --tags "tag1,tag2"
```

### Core Deployment Commands

```bash
# Complete cluster deployment (main entry point)
ansible-playbook -i inventory/hosts-scalable.yml playbooks/01-deployment/complete-deployment.yml

# Ubuntu 24.04 compatibility fix (run first if using Ubuntu 24.04)
ansible-playbook -i inventory/hosts-scalable.yml playbooks/00-preparation/fix-ubuntu24.yml

# Individual deployment steps
ansible-playbook -i inventory/hosts-scalable.yml playbooks/01-deployment/bootstrap.yml
ansible-playbook -i inventory/hosts-scalable.yml playbooks/01-deployment/post-bootstrap.yml

# Service configuration
ansible-playbook -i inventory/hosts-scalable.yml playbooks/02-services/configure-cephfs.yml
ansible-playbook -i inventory/hosts-scalable.yml playbooks/02-services/configure-rgw.yml
ansible-playbook -i inventory/hosts-scalable.yml playbooks/02-services/configure-rbd.yml

# Validation suite
ansible-playbook -i inventory/hosts-scalable.yml playbooks/04-validation/validate-all.yml
```

## High-Level Architecture

### Project Purpose

This is an enterprise Ansible automation suite for Ceph distributed storage clusters, extending cephadm-ansible with production-ready workflows. It provides comprehensive automation for deployment, configuration, operations, validation, and maintenance of Ceph clusters.

### Key Design Principles

1. **Layered Playbook Structure**: Numbered directories (00-90) indicate execution order and lifecycle phases
2. **Central Configuration**: Variables managed through `group_vars/all.yml` and inventory files
3. **Ubuntu 24.04 Compatibility**: Special handling for Ubuntu 24.04 LTS with Squid (19.x) support
4. **Idempotent Operations**: All playbooks designed to be safely re-runnable
5. **Modular Service Configuration**: Separate playbooks for each storage service (CephFS, RGW, RBD)

### Directory Structure and Purpose

- **`playbooks/00-preparation/`**: Pre-deployment setup (Ubuntu fixes, SSH keys, disk preparation)
- **`playbooks/01-deployment/`**: Cluster bootstrap and initial deployment
- **`playbooks/02-services/`**: Storage service configuration (CephFS, RGW, RBD, CSI)
- **`playbooks/03-operations/`**: Day-2 operations (snapshots, time sync, FSID management)
- **`playbooks/04-validation/`**: Automated testing and health validation
- **`playbooks/90-maintenance/`**: Cleanup and removal operations
- **`inventory/`**: Host definitions using scalable patterns (monitors also serve as OSDs/managers)
- **`group_vars/`**: Centralized variable management with Ubuntu version mappings

### Critical Configuration Files

1. **`inventory/hosts-scalable.yml`**: Defines cluster topology with IP addresses and role assignments
2. **`group_vars/all.yml`**: Global variables including Ubuntu-to-Ceph repository mappings
3. **`ansible.cfg`**: Performance tuning and SSH optimization settings

### Integration Points

- **cephadm-ansible**: This suite depends on and extends cephadm-ansible for core Ceph operations
- **Kubernetes CSI**: Provides CSI user management for Kubernetes integration
- **Ubuntu Repository Management**: Dynamic mapping of Ubuntu versions to compatible Ceph repositories

### Ubuntu 24.04 Special Handling

Ubuntu 24.04 requires special treatment due to cephadm package structure changes:
1. Must create `/var/lib/cephadm` directory before package installation
2. May need `dpkg --configure -a` to fix broken package states
3. Uses Jammy (22.04) repositories as fallback for missing Noble packages

### Variable Hierarchy

Variables are resolved in this order:
1. Command-line overrides (`-e` flags)
2. Playbook-level vars
3. `group_vars/all.yml`
4. Inventory variables
5. Ansible defaults

### Service Configuration Pattern

Each service follows a consistent pattern:
1. Pool creation with specific PG numbers
2. Service deployment with placement specs
3. User/credential creation
4. Validation playbook for verification

### Validation Strategy

The validation playbooks (`04-validation/`) check:
- Cluster health status (HEALTH_OK)
- Service availability and placement
- Pool existence and configuration
- User/credential functionality
- Network connectivity
- Time synchronization
