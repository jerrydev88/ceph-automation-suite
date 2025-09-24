# Ceph Architecture

Ceph 공식 문서 기반 상세 아키텍처 가이드

## 📊 아키텍처 개요

```mermaid
graph TB
    subgraph "Client Layer"
        RBD_Client[RBD Client]
        CephFS_Client[CephFS Client]
        S3_Client[S3/Swift Client]
    end

    subgraph "Interface Layer"
        LIBRBD[librbd]
        LIBCEPHFS[libcephfs]
        RADOSGW[RGW]
    end

    subgraph "Core Storage Layer - RADOS"
        LIBRADOS[librados]
        MON[Monitor Cluster]
        MGR[Manager]
        OSD1[OSD.1]
        OSD2[OSD.2]
        OSD3[OSD.3]
        OSDN[OSD.N]
    end

    RBD_Client --> LIBRBD
    CephFS_Client --> LIBCEPHFS
    S3_Client --> RADOSGW

    LIBRBD --> LIBRADOS
    LIBCEPHFS --> LIBRADOS
    RADOSGW --> LIBRADOS

    LIBRADOS --> MON
    LIBRADOS --> OSD1
    LIBRADOS --> OSD2
    LIBRADOS --> OSD3
    LIBRADOS --> OSDN

    MON --> MGR
```

## 🔧 계층별 상세 아키텍처

### 1. 클라이언트 계층 (Client Layer)

클라이언트는 Ceph 클러스터와 상호작용하는 애플리케이션 및 사용자입니다.

#### 클라이언트 타입

- **Thick Clients**: librados를 직접 사용 (RBD, CephFS)
- **Thin Clients**: HTTP/S3 프로토콜 사용 (RGW)
- **Kernel Clients**: 커널 모듈 통합 (krbd, kcephfs)

#### 클라이언트 아키텍처

```mermaid
graph LR
    subgraph "Application"
        App[Application]
    end

    subgraph "Client Libraries"
        App --> LibRBD[librbd]
        App --> LibCephFS[libcephfs]
        App --> S3SDK[S3 SDK]
    end

    subgraph "Protocol"
        LibRBD --> RADOS_Proto[RADOS Protocol]
        LibCephFS --> RADOS_Proto
        S3SDK --> HTTP[HTTP/S3]
    end

    RADOS_Proto --> Cluster[Ceph Cluster]
    HTTP --> RGW[RGW] --> Cluster
```

### 2. RADOS 계층 (Core Storage)

RADOS는 Ceph의 핵심 객체 스토리지 시스템입니다.

#### RADOS 구성 요소

```mermaid
graph TB
    subgraph "RADOS Cluster"
        subgraph "Monitor Quorum"
            MON1[MON.1<br/>Leader]
            MON2[MON.2<br/>Peon]
            MON3[MON.3<br/>Peon]
            MON1 -.->|Paxos| MON2
            MON2 -.->|Paxos| MON3
            MON3 -.->|Paxos| MON1
        end

        subgraph "Manager Active/Standby"
            MGR1[MGR.1<br/>Active]
            MGR2[MGR.2<br/>Standby]
        end

        subgraph "OSD Cluster"
            OSD1[OSD.1]
            OSD2[OSD.2]
            OSD3[OSD.3]
            OSD4[OSD.4]
            OSD5[OSD.5]
            OSD6[OSD.6]
        end

        MON1 --> MGR1
        MON1 --> OSD1
        MON1 --> OSD2
        MON1 --> OSD3
    end
```

### 3. 데이터 플로우 아키텍처

#### 쓰기 작업 플로우

```mermaid
sequenceDiagram
    participant Client
    participant MON
    participant Primary_OSD
    participant Replica_OSD1
    participant Replica_OSD2

    Client->>MON: 1. Get Cluster Map
    MON->>Client: 2. Return Map + Auth

    Note over Client: 3. CRUSH 계산

    Client->>Primary_OSD: 4. Write Request
    Primary_OSD->>Replica_OSD1: 5. Replicate
    Primary_OSD->>Replica_OSD2: 5. Replicate

    Replica_OSD1->>Primary_OSD: 6. ACK
    Replica_OSD2->>Primary_OSD: 6. ACK

    Primary_OSD->>Client: 7. Write Complete
```

#### 읽기 작업 플로우

```mermaid
sequenceDiagram
    participant Client
    participant MON
    participant Primary_OSD

    Client->>MON: 1. Get Cluster Map (캐시 확인)
    MON->>Client: 2. Return Map (필요시)

    Note over Client: 3. CRUSH 계산

    Client->>Primary_OSD: 4. Read Request
    Primary_OSD->>Client: 5. Return Data
```

## 🗺️ CRUSH 맵 구조

### CRUSH 계층 구조

```mermaid
graph TD
    Root[Root: default]
    Root --> DC1[Datacenter: dc1]
    Root --> DC2[Datacenter: dc2]

    DC1 --> Rack1[Rack: rack1]
    DC1 --> Rack2[Rack: rack2]

    Rack1 --> Host1[Host: ceph1]
    Rack1 --> Host2[Host: ceph2]

    Rack2 --> Host3[Host: ceph3]
    Rack2 --> Host4[Host: ceph4]

    Host1 --> OSD1[OSD.1]
    Host1 --> OSD2[OSD.2]

    Host2 --> OSD3[OSD.3]
    Host2 --> OSD4[OSD.4]

    Host3 --> OSD5[OSD.5]
    Host3 --> OSD6[OSD.6]

    Host4 --> OSD7[OSD.7]
    Host4 --> OSD8[OSD.8]
```

### CRUSH 알고리즘 플로우

```mermaid
graph LR
    Object[Object Name] --> Hash[Hash Function]
    Hash --> PG_ID[PG ID]
    PG_ID --> CRUSH[CRUSH Algorithm]

    subgraph "CRUSH Calculation"
        CRUSH --> Rule[CRUSH Rule]
        Rule --> Map[CRUSH Map]
        Map --> OSDs[OSD Set]
    end

    OSDs --> Primary[Primary OSD]
    OSDs --> Replicas[Replica OSDs]
```

## 📁 스토리지 서비스 아키텍처

### RBD (Block Storage)

```mermaid
graph TB
    subgraph "RBD Architecture"
        VM[Virtual Machine]
        VM --> QEMU[QEMU/KVM]
        QEMU --> LIBRBD[librbd]

        Container[Container]
        Container --> CSI[Ceph CSI]
        CSI --> LIBRBD

        LIBRBD --> Objects[4MB Objects]
        Objects --> Pool[RBD Pool]
        Pool --> OSDs[OSD Cluster]
    end
```

**RBD 특징:**
- 블록 디바이스 추상화
- 씬 프로비저닝
- 스냅샷 및 클론
- 이미지 레이어링

### CephFS (File System)

```mermaid
graph TB
    subgraph "CephFS Architecture"
        Client[CephFS Client]
        Client --> MDS_Active[MDS Active]
        Client --> MDS_Standby[MDS Standby]

        MDS_Active --> Meta_Pool[Metadata Pool]
        MDS_Active --> Data_Pool[Data Pool]

        Meta_Pool --> OSD_Meta[Metadata OSDs]
        Data_Pool --> OSD_Data[Data OSDs]

        MDS_Active -.->|Failover| MDS_Standby
    end
```

**CephFS 구성 요소:**
- **MDS**: 메타데이터 서버
- **Metadata Pool**: 파일 시스템 메타데이터
- **Data Pool**: 실제 파일 데이터

### RGW (Object Storage)

```mermaid
graph TB
    subgraph "RGW Architecture"
        S3Client[S3 Client]
        SwiftClient[Swift Client]

        S3Client --> RGW1[RGW Instance 1]
        SwiftClient --> RGW2[RGW Instance 2]

        RGW1 --> Index[Index Pool]
        RGW1 --> Data[Data Pool]
        RGW2 --> Index
        RGW2 --> Data

        subgraph "Pools"
            Index --> OSD_Index[Index OSDs]
            Data --> OSD_Data[Data OSDs]
        end

        RGW1 -.->|Load Balance| RGW2
    end
```

## 🔄 Placement Group (PG) 아키텍처

### PG 매핑 구조

```mermaid
graph TD
    subgraph "Object to PG Mapping"
        Obj1[Object 1] --> PG1[PG 1.0]
        Obj2[Object 2] --> PG1
        Obj3[Object 3] --> PG2[PG 1.1]
        Obj4[Object 4] --> PG2
    end

    subgraph "PG to OSD Mapping"
        PG1 --> OSD_Set1[OSD Set: 1,3,5]
        PG2 --> OSD_Set2[OSD Set: 2,4,6]
    end

    subgraph "Physical OSDs"
        OSD_Set1 --> OSD1[OSD.1<br/>Primary]
        OSD_Set1 --> OSD3[OSD.3<br/>Replica]
        OSD_Set1 --> OSD5[OSD.5<br/>Replica]

        OSD_Set2 --> OSD2[OSD.2<br/>Primary]
        OSD_Set2 --> OSD4[OSD.4<br/>Replica]
        OSD_Set2 --> OSD6[OSD.6<br/>Replica]
    end
```

### PG 상태 머신

```mermaid
stateDiagram-v2
    [*] --> Creating
    Creating --> Active

    Active --> Active_Clean: All replicas in sync
    Active --> Active_Recovery: Missing objects
    Active --> Active_Backfilling: Adding new OSD

    Active_Recovery --> Active_Clean: Recovery complete
    Active_Backfilling --> Active_Clean: Backfill complete

    Active_Clean --> Active_Scrubbing: Scheduled scrub
    Active_Scrubbing --> Active_Clean: Scrub complete

    Active --> Peering: OSD failure
    Peering --> Active: Peering complete

    Active --> Inactive: Not enough OSDs
    Inactive --> Active: OSDs available
```

## 🔐 인증 및 보안 아키텍처

### CephX 인증 플로우

```mermaid
sequenceDiagram
    participant Client
    participant Monitor
    participant OSD

    Client->>Monitor: 1. Auth Request + Username
    Monitor->>Monitor: 2. Verify Credentials
    Monitor->>Client: 3. Session Key + Ticket

    Client->>OSD: 4. Request + Ticket
    OSD->>OSD: 5. Verify Ticket
    OSD->>Client: 6. Authorized Access

    Note over Client,OSD: Tickets have TTL and capabilities
```

### 보안 계층

```mermaid
graph TB
    subgraph "Security Layers"
        Network[Network Encryption<br/>In-transit]
        Auth[CephX Authentication]
        Caps[Capabilities<br/>Authorization]
        Encryption[At-rest Encryption<br/>OSD/RGW]
    end

    Network --> Auth
    Auth --> Caps
    Caps --> Encryption
```

## 🚀 고가용성 아키텍처

### Monitor Quorum

```mermaid
graph TB
    subgraph "Monitor HA"
        direction LR
        MON1[Monitor 1<br/>Leader]
        MON2[Monitor 2<br/>Peon]
        MON3[Monitor 3<br/>Peon]
        MON4[Monitor 4<br/>Peon]
        MON5[Monitor 5<br/>Peon]

        MON1 -.->|Paxos Consensus| MON2
        MON1 -.->|Paxos Consensus| MON3
        MON1 -.->|Paxos Consensus| MON4
        MON1 -.->|Paxos Consensus| MON5
    end

    Note1[Quorum = 3 for 5 monitors]
```

### 장애 도메인

```mermaid
graph TD
    subgraph "Failure Domains"
        subgraph "Rack 1"
            Host1[Host 1]
            Host2[Host 2]
        end

        subgraph "Rack 2"
            Host3[Host 3]
            Host4[Host 4]
        end

        subgraph "Rack 3"
            Host5[Host 5]
            Host6[Host 6]
        end

        Object[Object: 3 Replicas]
        Object --> Host1
        Object --> Host3
        Object --> Host5

        Note1[각 복제본은 다른 Rack에 배치]
    end
```

## 📈 확장성 아키텍처

### 수평 확장

```mermaid
graph LR
    subgraph "Initial Cluster"
        Init_OSD[3 Nodes<br/>12 OSDs]
    end

    subgraph "Scaled Cluster"
        Scale_OSD[10 Nodes<br/>40 OSDs]
    end

    subgraph "Large Cluster"
        Large_OSD[100 Nodes<br/>400 OSDs]
    end

    Init_OSD -->|Add Nodes| Scale_OSD
    Scale_OSD -->|Add More| Large_OSD

    Note1[CRUSH가 자동으로 데이터 재분배]
```

### 성능 확장

```mermaid
graph TB
    subgraph "Performance Scaling"
        subgraph "Cache Tier"
            SSD_Pool[SSD Pool<br/>Hot Data]
        end

        subgraph "Storage Tier"
            HDD_Pool[HDD Pool<br/>Cold Data]
        end

        Client[Client] --> SSD_Pool
        SSD_Pool -->|Tier Agent| HDD_Pool

        Note1[자동 티어링으로 성능 최적화]
    end
```

## 🔧 BlueStore 아키텍처

### BlueStore 스택

```mermaid
graph TB
    subgraph "BlueStore Stack"
        Client[Ceph Client]
        Client --> OSD_Layer[OSD]
        OSD_Layer --> BlueStore[BlueStore]

        subgraph "BlueStore Components"
            BlueStore --> RocksDB[RocksDB<br/>Metadata]
            BlueStore --> BlockDevice[Block Device<br/>Direct I/O]
            BlueStore --> BlueFS[BlueFS]

            RocksDB --> BlueFS
            BlueFS --> Device[Physical Device]
            BlockDevice --> Device
        end
    end
```

### BlueStore 특징

- **직접 블록 접근**: 파일 시스템 오버헤드 제거
- **효율적 메타데이터**: RocksDB 사용
- **체크섬**: 데이터 무결성
- **압축**: 인라인 압축 지원
- **효율적 오버라이트**: Copy-on-Write 최소화

## 📊 모니터링 아키텍처

### 모니터링 스택

```mermaid
graph TB
    subgraph "Monitoring Stack"
        MGR[Ceph Manager]
        MGR --> Prometheus[Prometheus Module]
        MGR --> Dashboard[Dashboard Module]
        MGR --> Zabbix[Zabbix Module]

        Prometheus --> Grafana[Grafana]
        Dashboard --> WebUI[Web Dashboard]
        Zabbix --> ZabbixServer[Zabbix Server]

        MGR --> Telegraf[Telegraf Module]
        Telegraf --> InfluxDB[InfluxDB]
    end
```

## 🌐 네트워크 아키텍처

### 듀얼 네트워크 구성

```mermaid
graph TB
    subgraph "Network Architecture"
        subgraph "Public Network"
            Client[Clients]
            MON[Monitors]
            MGR[Managers]
            RGW[RGW]
        end

        subgraph "Cluster Network"
            OSD1[OSD 1]
            OSD2[OSD 2]
            OSD3[OSD 3]
            OSDN[OSD N]
        end

        Client -.->|Client Traffic| OSD1
        MON -.->|Monitor Traffic| OSD1

        OSD1 <-->|Replication| OSD2
        OSD2 <-->|Recovery| OSD3
        OSD3 <-->|Backfill| OSDN
    end

    Note1[Public: 10.10.2.0/24]
    Note2[Cluster: 192.168.2.0/24]
```

## 요약

Ceph 아키텍처는 RADOS를 중심으로 한 분산 객체 스토리지 시스템으로, CRUSH 알고리즘을 통해 데이터를 지능적으로 분산하고, 다양한 스토리지 인터페이스(RBD, CephFS, RGW)를 제공합니다. Monitor 쿼럼은 클러스터 상태를 관리하고, OSD는 실제 데이터를 저장하며, Manager는 모니터링과 오케스트레이션을 담당합니다. 이 모든 구성 요소가 협력하여 확장 가능하고 자가 치유가 가능한 스토리지 플랫폼을 구성합니다.

---

*이 문서는 Ceph 공식 문서(docs.ceph.com) 및 Red Hat Ceph Storage 아키텍처 가이드를 기반으로 작성되었습니다.*