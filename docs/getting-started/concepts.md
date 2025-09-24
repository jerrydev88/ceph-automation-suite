# Ceph Core Concepts

이 문서는 Ceph 공식 문서를 기반으로 작성된 핵심 개념 가이드입니다.

## 📚 목차

1. [Ceph란 무엇인가?](#ceph란-무엇인가)
2. [핵심 구성 요소](#핵심-구성-요소)
3. [데이터 저장 방식](#데이터-저장-방식)
4. [스토리지 서비스 타입](#스토리지-서비스-타입)
5. [핵심 알고리즘](#핵심-알고리즘)

## Ceph란 무엇인가?

**Ceph**는 확장성, 신뢰성, 성능을 목표로 설계된 오픈소스 분산 스토리지 플랫폼입니다. 단일 스토리지 클러스터에서 객체 스토리지, 블록 스토리지, 파일 시스템을 통합 제공합니다.

### 주요 특징

- **통합 스토리지**: 객체(S3/Swift), 블록(RBD), 파일(CephFS)를 하나의 클러스터에서 제공
- **확장성**: 페타바이트 규모까지 수평 확장 가능
- **자가 치유**: 자동 복구, 리밸런싱, 장애 감지
- **소프트웨어 정의**: 일반 하드웨어에서 실행 가능

## 핵심 구성 요소

### RADOS (Reliable Autonomic Distributed Object Store)

Ceph의 기반이 되는 객체 스토리지 시스템입니다. 모든 데이터는 RADOS 객체로 저장됩니다.

**주요 기능:**
- 객체 복제 및 분산
- 장애 감지 및 복구
- 데이터 일관성 보장
- 자동 리밸런싱

### Ceph Daemons

#### 1. Monitor (MON)

- **역할**: 클러스터 맵 관리, 클러스터 상태 모니터링
- **특징**:
  - 클러스터 멤버십 관리
  - 인증 및 권한 부여
  - Paxos 알고리즘으로 합의 도출
  - 일반적으로 홀수 개(3, 5, 7) 배포

#### 2. OSD (Object Storage Daemon)

- **역할**: 실제 데이터 저장 및 처리
- **특징**:
  - 디스크당 하나의 OSD
  - 데이터 복제 및 복구
  - 스크러빙(데이터 무결성 검사)
  - 피어링 및 리커버리

#### 3. Manager (MGR)

- **역할**: 모니터링 메트릭, 대시보드, 오케스트레이션
- **특징**:
  - Prometheus 메트릭 제공
  - 웹 대시보드 호스팅
  - 클러스터 통계 수집
  - Active/Standby 구성

#### 4. MDS (Metadata Server)

- **역할**: CephFS 메타데이터 관리
- **특징**:
  - 파일 시스템 메타데이터 캐싱
  - 디렉토리 계층 관리
  - Active/Standby 또는 Active/Active 구성
  - 동적 서브트리 파티셔닝

## 데이터 저장 방식

### Object Storage 개념

모든 데이터는 객체(Object)로 저장됩니다:

1. **파일 → 객체 변환**
   - 파일이 4MB 청크로 분할
   - 각 청크가 RADOS 객체가 됨
   - 객체 ID = Pool ID + Object Name Hash

2. **객체 배치**
   - CRUSH 알고리즘이 객체 위치 결정
   - PG(Placement Group)에 매핑
   - PG는 OSD 세트에 매핑

### Pools

**Pool**은 논리적 스토리지 파티션입니다:

- **복제 풀(Replicated Pool)**
  - 데이터를 N개 복사본으로 저장
  - 빠른 읽기, 간단한 구성
  - 스토리지 효율성 낮음 (3x 오버헤드)

- **삭제 코딩 풀(Erasure Coded Pool)**
  - 데이터를 K개 데이터 청크 + M개 코딩 청크로 분할
  - 스토리지 효율성 높음
  - 계산 오버헤드 존재
  - 대용량 콜드 데이터에 적합

### Placement Groups (PG)

**PG**는 객체와 OSD 사이의 추상화 계층입니다:

- **목적**:
  - 객체를 그룹화하여 관리
  - 복제 단위
  - 리밸런싱 단위
  - 복구 단위

- **PG 수 계산**:
  ```
  Total PGs = (OSD 수 × 100) / 복제 팩터
  Pool당 PG = Total PGs / Pool 수
  ```

## 스토리지 서비스 타입

### 1. RBD (RADOS Block Device)

**블록 스토리지 서비스**

- **용도**: VM 디스크, 데이터베이스 스토리지
- **특징**:
  - 씬 프로비저닝
  - 스냅샷 및 클론
  - 이미지 레이어링
  - 라이브 마이그레이션

### 2. CephFS (Ceph File System)

**POSIX 호환 분산 파일 시스템**

- **용도**: 공유 파일 스토리지, 홈 디렉토리
- **특징**:
  - POSIX 시맨틱
  - 동적 메타데이터 파티셔닝
  - 스냅샷
  - 다중 Active MDS

### 3. RGW (RADOS Gateway)

**객체 스토리지 게이트웨이**

- **용도**: S3/Swift 호환 객체 스토리지
- **특징**:
  - S3 API 호환
  - Swift API 호환
  - 멀티테넌시
  - 버킷 복제

## 핵심 알고리즘

### CRUSH (Controlled Replication Under Scalable Hashing)

**데이터 배치 알고리즘**

CRUSH는 데이터가 저장될 위치를 의사 무작위로 계산합니다:

1. **CRUSH Map**
   - 클러스터 토폴로지 정의
   - 계층 구조: Root → Datacenter → Rack → Host → OSD
   - 장애 도메인 정의

2. **CRUSH Rules**
   - 데이터 배치 정책
   - 복제본 분산 규칙
   - 장애 도메인 격리

3. **장점**
   - 중앙 조회 테이블 불필요
   - 클라이언트가 직접 OSD 위치 계산
   - 확장 시 최소한의 데이터 이동

### Peering & Recovery

**데이터 일관성 및 복구 메커니즘**

1. **Peering**
   - PG 내 OSD 간 상태 동기화
   - 권위 있는 로그 확립
   - 복구 계획 수립

2. **Recovery**
   - 누락된 객체 복구
   - 장애 OSD 데이터 재구성
   - 우선순위 기반 복구

### Scrubbing

**데이터 무결성 검증**

- **Light Scrub**: 메타데이터 검증
- **Deep Scrub**: 데이터 내용 검증
- 주기적 실행 (일일/주간)
- 비트 로트 감지 및 수정

## Best Practices

### 클러스터 설계

1. **Monitor 배치**
   - 홀수 개 배포 (3, 5, 7)
   - 서로 다른 장애 도메인에 분산
   - 낮은 레이턴시 네트워크

2. **OSD 설계**
   - 디스크당 하나의 OSD
   - SSD를 WAL/DB로 활용
   - 적절한 PG 수 설정

3. **네트워크 설계**
   - Public Network: 클라이언트 트래픽
   - Cluster Network: OSD 간 복제 트래픽
   - 최소 10Gbps 권장

### 성능 튜닝

1. **PG 수 최적화**
   - OSD당 100-200 PG 목표
   - pg_autoscale 활용

2. **캐싱 전략**
   - BlueStore 캐시 튜닝
   - RocksDB 설정 최적화

3. **하드웨어 고려사항**
   - NVMe for 메타데이터
   - HDD for 콜드 데이터
   - 충분한 RAM (OSD당 4GB+)

## 요약

Ceph는 RADOS를 기반으로 한 통합 스토리지 플랫폼으로, CRUSH 알고리즘을 통해 데이터를 지능적으로 분산하고, 자가 치유 기능을 통해 높은 가용성을 제공합니다. Monitor, OSD, Manager, MDS 데몬들이 협력하여 블록(RBD), 파일(CephFS), 객체(RGW) 스토리지를 단일 클러스터에서 제공합니다.

---

*이 문서는 Ceph 공식 문서(docs.ceph.com) 및 Red Hat Ceph Storage 문서를 기반으로 작성되었습니다.*