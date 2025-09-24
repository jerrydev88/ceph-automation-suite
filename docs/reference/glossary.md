# Ceph 용어 사전 (Glossary)

Ceph 공식 문서 기반 종합 용어 정리

## A

### ACL (Access Control List)
접근 제어 목록. RGW에서 버킷과 객체에 대한 접근 권한을 정의합니다.

### Active MDS
현재 활성 상태로 클라이언트 요청을 처리하는 메타데이터 서버입니다.

### Admin Socket
Ceph 데몬과 로컬 통신을 위한 Unix 도메인 소켓입니다. `/var/run/ceph/` 디렉토리에 위치합니다.

### Affinity
CRUSH가 특정 OSD나 호스트를 선호하도록 하는 설정입니다.

### At-Rest Encryption
저장된 데이터를 암호화하는 기능. OSD와 RGW에서 지원됩니다.

## B

### Backfill
새 OSD가 클러스터에 추가되거나 장애 복구 시 데이터를 재분배하는 과정입니다.

### Balancer
PG를 OSD 간에 균등하게 분배하여 부하를 분산시키는 Manager 모듈입니다.

### Bucket (RGW)
객체 스토리지에서 객체들을 담는 컨테이너. S3 버킷과 동일한 개념입니다.

### Bucket (CRUSH)
CRUSH 계층에서 장치들을 그룹화하는 단위입니다.

### BlueStore
Ceph의 기본 OSD 백엔드 스토리지 엔진. 블록 장치에 직접 쓰기를 수행합니다.

### Bootstrap
Ceph 클러스터의 초기 설정 과정. 첫 번째 Monitor와 Manager를 생성합니다.

## C

### Cache Tier
자주 사용되는 데이터를 SSD 풀에 캐싱하는 계층입니다.

### Capability (caps)
CephX 인증 시스템에서 클라이언트의 권한을 정의하는 것입니다.

### Ceph
통합 분산 스토리지 시스템. 이름은 애완용 문어 "Cephalopod"에서 유래했습니다.

### Cephadm
컨테이너를 사용하여 Ceph를 배포하고 관리하는 오케스트레이션 도구입니다.

### CephFS
POSIX 호환 분산 파일 시스템 서비스입니다.

### CephX
Ceph의 인증 프로토콜. Kerberos와 유사한 티켓 기반 시스템입니다.

### Client
Ceph 클러스터와 상호작용하는 사용자나 애플리케이션입니다.

### Cluster Map
클러스터의 현재 토폴로지와 상태를 나타내는 맵의 집합입니다.

### Consistency Group
여러 RBD 이미지에 대해 일관된 스냅샷을 생성하는 기능입니다.

### CRUSH (Controlled Replication Under Scalable Hashing)
데이터 배치를 결정하는 의사 무작위 알고리즘입니다.

### CRUSH Map
클러스터의 물리적 토폴로지를 정의하는 데이터 구조입니다.

### CRUSH Rule
데이터 배치 정책을 정의하는 규칙입니다.

### CSI (Container Storage Interface)
Kubernetes와 같은 컨테이너 오케스트레이터와 통합하기 위한 표준 인터페이스입니다.

## D

### Dashboard
웹 기반 Ceph 클러스터 관리 인터페이스입니다.

### Data Pool
실제 데이터가 저장되는 풀입니다.

### Deep Scrub
데이터 내용까지 검증하는 상세한 스크러빙 작업입니다.

### Degraded
복제본이 부족한 상태. 데이터는 여전히 사용 가능하지만 위험한 상태입니다.

### Device Class
OSD 장치의 타입 (hdd, ssd, nvme)을 분류하는 것입니다.

## E

### Epoch
클러스터 맵의 버전 번호입니다.

### Erasure Coding (EC)
데이터와 패리티를 분산하여 스토리지 효율성을 높이는 방법입니다.

### Erasure Code Profile
삭제 코딩 풀의 파라미터 (k+m, 플러그인 등)를 정의합니다.

## F

### Failure Domain
장애가 격리되는 범위 (호스트, 랙, 데이터센터 등)입니다.

### FileStore
레거시 OSD 백엔드. 현재는 BlueStore로 대체되었습니다.

### FSID (File System ID)
클러스터의 고유 식별자 UUID입니다.

### Full Ratio
OSD가 쓰기를 거부하는 사용률 임계값입니다. 기본값은 95%입니다.

## G

### Gateway
RGW (RADOS Gateway)를 지칭하는 약어입니다.

## H

### Health Check
클러스터 상태를 모니터링하는 검사 항목들입니다.

### Heartbeat
OSD 간 생존 확인을 위한 주기적 메시지입니다.

## I

### Image (RBD)
블록 디바이스를 나타내는 RBD 객체입니다.

### Inconsistent
스크러빙 중 발견된 데이터 불일치 상태입니다.

### In-Flight Encryption
네트워크 전송 중 데이터를 암호화하는 것입니다.

## J

### Journal
OSD의 쓰기 로그. BlueStore에서는 WAL이 이 역할을 합니다.

## K

### Keyring
CephX 인증 키를 저장하는 파일입니다.

### krbd
커널 RBD 클라이언트 모듈입니다.

## L

### Lease
MDS가 클라이언트에게 부여하는 메타데이터 캐시 권한입니다.

### librados
RADOS와 직접 통신하기 위한 C/C++ 라이브러리입니다.

### librbd
RBD 기능을 제공하는 라이브러리입니다.

### Light Scrub
메타데이터만 검증하는 가벼운 스크러빙입니다.

## M

### Manager (MGR)
클러스터 모니터링, 메트릭, 대시보드를 담당하는 데몬입니다.

### MDS (Metadata Server)
CephFS의 메타데이터를 관리하는 서버입니다.

### Metadata Pool
CephFS 메타데이터가 저장되는 풀입니다.

### Min Size
I/O를 허용하는 최소 복제본 수입니다.

### Monitor (MON)
클러스터 맵을 관리하고 합의를 도출하는 데몬입니다.

### Monitor Quorum
과반수 이상의 Monitor가 동의하는 상태입니다.

### Multisite
여러 지역에 걸친 RGW 클러스터 구성입니다.

## N

### Namespace (RBD)
RBD 이미지를 논리적으로 그룹화하는 방법입니다.

### Near-full Ratio
경고를 발생시키는 OSD 사용률 임계값입니다. 기본값은 85%입니다.

### Network Ping
네트워크 연결성을 테스트하는 작업입니다.

## O

### Object
RADOS의 기본 저장 단위. 일반적으로 4MB 크기입니다.

### Object Gateway
RGW를 지칭하는 다른 이름입니다.

### OSD (Object Storage Daemon)
데이터를 저장하고 복제를 담당하는 데몬입니다.

### OSD Map
OSD의 상태와 위치 정보를 담은 클러스터 맵입니다.

### OSDMap Epoch
OSD 맵의 버전 번호입니다.

## P

### Paxos
Monitor 간 합의를 도출하는 분산 합의 알고리즘입니다.

### Peering
PG 내 OSD들이 상태를 동기화하는 과정입니다.

### PG (Placement Group)
객체를 그룹화하여 관리하는 단위입니다.

### PG Log
PG의 최근 작업 기록입니다.

### pg_num
풀에 있는 PG의 개수입니다.

### pgp_num
배치에 사용되는 PG의 개수입니다.

### Pool
데이터를 논리적으로 분리하는 스토리지 파티션입니다.

### Primary OSD
PG의 주 복제본을 담당하는 OSD입니다.

### Prometheus
Ceph Manager가 제공하는 메트릭을 수집하는 모니터링 시스템입니다.

## Q

### QoS (Quality of Service)
성능과 자원 사용을 제어하는 기능입니다.

### Quota
CephFS와 RGW에서 사용량을 제한하는 기능입니다.

### Quorum
Monitor들이 합의를 이루기 위한 최소 개수입니다.

## R

### RADOS (Reliable Autonomic Distributed Object Store)
Ceph의 핵심 객체 스토리지 시스템입니다.

### RBD (RADOS Block Device)
블록 스토리지 서비스입니다.

### Realm (RGW)
멀티사이트 구성의 최상위 컨테이너입니다.

### Recovery
장애 후 데이터를 복구하는 과정입니다.

### Replica
데이터의 복사본입니다.

### Replication Factor
데이터 복사본의 개수입니다. size 파라미터로 설정합니다.

### RGW (RADOS Gateway)
S3/Swift 호환 객체 스토리지 게이트웨이입니다.

### RocksDB
BlueStore에서 메타데이터 저장에 사용하는 키-밸류 데이터베이스입니다.

## S

### Scrubbing
데이터 무결성을 검증하는 백그라운드 작업입니다.

### Slow Request
설정된 시간보다 오래 걸리는 요청입니다.

### Snapshot
특정 시점의 데이터 상태를 보존하는 기능입니다.

### Standby MDS
대기 상태의 백업 메타데이터 서버입니다.

### Standby-Replay MDS
Active MDS의 로그를 지속적으로 재생하는 백업 서버입니다.

### Storage Class
EC 프로파일이나 복제 정책을 정의하는 설정입니다.

### Stripe
데이터를 여러 객체에 분산하는 방식입니다.

### Subvolume
CephFS 내의 격리된 파일 시스템 영역입니다.

### Swift
OpenStack의 객체 스토리지 API. RGW가 호환 지원합니다.

## T

### Thin Provisioning
실제 사용량만큼만 스토리지를 할당하는 방식입니다.

### Throttle
성능 제한을 설정하는 기능입니다.

### Tier
캐시 계층이나 스토리지 계층을 의미합니다.

### Tiering
데이터를 성능별로 다른 스토리지에 자동 배치하는 기능입니다.

### Trim
삭제된 블록을 정리하는 작업입니다.

## U

### Unfound
위치를 알 수 없는 객체 상태입니다.

### Upmap
특정 PG를 수동으로 재배치하는 기능입니다.

## V

### Version (Object)
객체의 버전 번호입니다. RGW에서 버전 관리에 사용됩니다.

### Volume (RBD)
RBD 이미지를 지칭하는 다른 용어입니다.

## W

### WAL (Write-Ahead Log)
BlueStore에서 쓰기 성능을 위한 로그입니다.

### Weight
CRUSH에서 OSD의 상대적 용량을 나타내는 값입니다.

### Writeback
캐시 모드 중 하나. 쓰기를 캐시에만 하고 나중에 백엔드로 플러시합니다.

### Write-through
캐시 모드 중 하나. 쓰기를 캐시와 백엔드에 동시에 수행합니다.

## Z

### Zap
OSD 디스크를 초기화하는 작업입니다.

### Zone (RGW)
멀티사이트 구성에서 데이터 센터나 지역을 나타냅니다.

### Zone Group (RGW)
여러 Zone을 묶은 그룹입니다.

## 약어 정리

| 약어 | 전체 이름 | 설명 |
|------|-----------|------|
| ACL | Access Control List | 접근 제어 목록 |
| API | Application Programming Interface | 애플리케이션 프로그래밍 인터페이스 |
| CDS | Ceph Distributed Storage | Ceph 분산 스토리지 |
| CephFS | Ceph File System | Ceph 파일 시스템 |
| CRUSH | Controlled Replication Under Scalable Hashing | 확장 가능한 해싱 기반 제어 복제 |
| CSI | Container Storage Interface | 컨테이너 스토리지 인터페이스 |
| EC | Erasure Coding | 삭제 코딩 |
| FSID | File System ID | 파일 시스템 식별자 |
| HA | High Availability | 고가용성 |
| HDD | Hard Disk Drive | 하드 디스크 드라이브 |
| I/O | Input/Output | 입출력 |
| K8s | Kubernetes | 쿠버네티스 |
| MDS | Metadata Server | 메타데이터 서버 |
| MGR | Manager | 매니저 |
| MON | Monitor | 모니터 |
| NFS | Network File System | 네트워크 파일 시스템 |
| NVMe | Non-Volatile Memory Express | 비휘발성 메모리 익스프레스 |
| OSD | Object Storage Daemon | 객체 스토리지 데몬 |
| PG | Placement Group | 배치 그룹 |
| POSIX | Portable Operating System Interface | 이식 가능 운영체제 인터페이스 |
| QoS | Quality of Service | 서비스 품질 |
| RADOS | Reliable Autonomic Distributed Object Store | 신뢰성 있는 자율 분산 객체 저장소 |
| RBD | RADOS Block Device | RADOS 블록 디바이스 |
| RGW | RADOS Gateway | RADOS 게이트웨이 |
| S3 | Simple Storage Service | 심플 스토리지 서비스 |
| SSD | Solid State Drive | 솔리드 스테이트 드라이브 |
| TTL | Time To Live | 유효 시간 |
| UUID | Universally Unique Identifier | 범용 고유 식별자 |
| WAL | Write-Ahead Log | 미리 쓰기 로그 |

## 주요 명령어 용어

| 명령어 | 설명 |
|--------|------|
| `ceph -s` | 클러스터 상태 확인 |
| `ceph health` | 클러스터 건강 상태 |
| `ceph osd tree` | OSD 토폴로지 표시 |
| `ceph df` | 클러스터 사용량 확인 |
| `ceph osd pool ls` | 풀 목록 조회 |
| `ceph orch` | 오케스트레이션 명령 |
| `cephadm` | Ceph 배포 관리 도구 |
| `radosgw-admin` | RGW 관리 명령 |
| `rbd` | RBD 관리 명령 |
| `rados` | RADOS 직접 접근 명령 |

## 성능 관련 용어

| 용어 | 설명 | 일반 값 |
|------|------|---------|
| IOPS | 초당 입출력 작업 수 | SSD: 10K+, HDD: 100-200 |
| Throughput | 데이터 전송률 | GB/s 단위 |
| Latency | 응답 지연 시간 | ms 단위 |
| Queue Depth | 대기 중인 I/O 요청 수 | 1-256 |
| Cache Hit Ratio | 캐시 적중률 | 백분율 |

## 상태 코드

| 상태 | 의미 | 조치 |
|------|------|------|
| HEALTH_OK | 정상 상태 | 조치 불필요 |
| HEALTH_WARN | 경고 상태 | 모니터링 필요 |
| HEALTH_ERR | 오류 상태 | 즉시 조치 필요 |
| active+clean | PG 정상 상태 | 조치 불필요 |
| degraded | 복제본 부족 | 복구 대기 |
| undersized | 복제본 부족 | OSD 추가 필요 |
| peering | 동기화 중 | 대기 |
| recovering | 복구 중 | 대기 |
| backfilling | 백필 중 | 대기 |
| inconsistent | 불일치 발견 | 복구 필요 |

---

*이 용어 사전은 Ceph 공식 문서(docs.ceph.com)와 Red Hat Ceph Storage 문서를 기반으로 작성되었습니다.*