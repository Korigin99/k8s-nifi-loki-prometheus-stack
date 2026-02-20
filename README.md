# FlowKube

**NiFi + Kubernetes 기반 동적 Job 오케스트레이션 & PLG 모니터링**

Apache NiFi를 컨트롤 타워로 사용해 Kubernetes 클러스터에서 Python 작업 Pod를 동적으로 생성하고, Fluent Bit → Loki → Grafana로 로그를 수집·조회할 수 있는 자동화 프로젝트입니다.

---

## 특징

| 구분 | 설명 |
|------|------|
| **동적 오케스트레이션** | NiFi가 K8s API를 호출해 필요한 시점에만 Python 컨테이너를 실행합니다. |
| **다양한 워커** | 기본 실행, CPU 부하, 로그 생성 등 목적별 Python 모듈을 제공합니다. |
| **통합 로그 모니터링** | Fluent Bit이 Pod 로그를 수집해 Loki에 전송하고, Grafana에서 잡별로 조회할 수 있습니다. |

---

## 프로젝트 구조

```
├── k8s/                    # Kubernetes 매니페스트
│   ├── 00-namespaces.yaml  # flowkube-admin, flowkube-jobs 네임스페이스
│   ├── nifi-rbac.yaml      # NiFi용 RBAC (Pod 생성/조회/삭제)
│   ├── nifi-deployment.yaml# NiFi Deployment & Service
│   └── fluent-bit-fix.yaml # Loki 연동 시 Fluent Bit labelmap (job_type 등)
├── python/                 # Python 워커 및 이미지
│   ├── app_basic.py        # 단순 실행 확인
│   ├── app_cpu.py          # CPU 부하 (소수 계산)
│   ├── app_log.py          # 로그 레벨 테스트 (INFO/WARN/ERROR)
│   ├── Dockerfile
│   └── requirements.txt
└── nifi/
    └── NiFi-Kube-Python.json   # NiFi 플로우 정의 (가져오기용)
```

---

## 주요 구성 요소

### 1. 인프라 (Kubernetes)

- **네임스페이스**
  - `flowkube-admin`: NiFi 배포
  - `flowkube-jobs`: Python 작업 Pod 실행
- **RBAC**: ServiceAccount `nifi-sa`(flowkube-admin)가 `flowkube-jobs`에서 Pod 생성·조회·삭제 가능
- **NiFi**: `apache/nifi:2.6.0`, HTTPS 8443, 단일 사용자 로그인

### 2. Python 워커

| 파일 | 용도 |
|------|------|
| `app_basic.py` | Pod 이름·타임스탬프 출력, 동작 확인 |
| `app_cpu.py` | 소수 계산으로 CPU 부하 시뮬레이션 |
| `app_log.py` | 15개 Task, INFO/WARN/ERROR 랜덤 로그 (모니터링 테스트용) |

### 3. NiFi 플로우

1. **GenerateFlowFile** — Pod 생성용 JSON 템플릿 생성  
2. **ReplaceText** — `PLACEHOLDER`를 타임스탬프로 치환해 Pod 이름 고유화  
3. **ExecuteStreamCommand** — ServiceAccount 토큰을 읽어 `k8s.token` 속성에 저장  
4. **InvokeHTTP** — K8s API `POST .../pods` 로 Pod 생성 (Bearer 토큰 인증)  
5. **LogAttribute** — 응답 로깅

플로우 JSON의 `namespace`·`HTTP URL`을 실제 사용하는 네임스페이스(`flowkube-jobs` 등)에 맞게 수정해야 합니다.

---

## 빠른 시작

### 사전 요구사항

- Kubernetes 클러스터 (k3s, Rancher Desktop 등)
- `kubectl` 설정 완료
- Rancher Desktop (`containerd`) + `nerdctl` (Python 이미지 빌드용)

### 1. 네임스페이스 및 NiFi 배포

```bash
kubectl apply -f k8s/00-namespaces.yaml
kubectl apply -f k8s/nifi-rbac.yaml
kubectl apply -f k8s/nifi-deployment.yaml
```

NiFi 서비스 접속을 위해 포트 포워딩:

```bash
kubectl port-forward -n flowkube-admin svc/nifi 8443:8443
```

### 2. Python 워커 이미지 빌드

기본 워커 및 CPU/로그 워커 이미지를 빌드합니다. (레지스트리에 푸시하려면 태그를 자신의 이미지 주소로 변경하세요.)

```powershell
cd python
$NS = "k8s.io"
nerdctl --namespace $NS build -t test-python:basic .
nerdctl --namespace $NS build -t test-python:cpu --build-arg APP_FILE=app_cpu.py .
nerdctl --namespace $NS build -t test-python:log --build-arg APP_FILE=app_log.py .
nerdctl --namespace $NS images | findstr test-python
```

> 중요: 위 명령은 **이미지를 containerd(`k8s.io`)에 빌드**하는 단계입니다.  
> 실제 Python 작업 Pod는 NiFi `InvokeHTTP` URL의 namespace 설정에 따라 **`flowkube-jobs`**에 생성됩니다.

### 3. NiFi 플로우 가져오기

1. 브라우저에서 **https://localhost:8443/nifi** 접속  
2. 로그인: `admin` / `AdminPassword123`  
3. **Upload flow** 또는 **Import flow**로 `nifi/NiFi-Kube-Python.json` 업로드  
4. **InvokeHTTP** 프로세서에서 다음을 확인·수정:
   - **HTTP URL**: 사용 중인 네임스페이스에 맞게 (예: `https://kubernetes.default.svc/api/v1/namespaces/flowkube-jobs/pods`)
   - **SSL Context Service**: 클러스터 내부 TLS용 서비스 연결
   - **Authorization**: `Bearer ${k8s.token}` (토큰은 ExecuteStreamCommand에서 주입)

작업 Pod가 `flowkube-jobs`에 올라오는지 확인:

```powershell
kubectl get pods -n flowkube-jobs -w
```

#### Controller Service용 인증서(TrustStore) 생성

```powershell
kubectl exec -n flowkube-admin deploy/nifi -- keytool -import -alias k8s-api -file /var/run/secrets/kubernetes.io/serviceaccount/ca.crt -keystore /opt/nifi/nifi-current/conf/truststore.jks -storepass changeit -noprompt
```

---

## 모니터링 (PLG 스택)

다음은 **Loki / Fluent Bit / Prometheus(Grafana 포함)** 를 각각 설치하는 권장 절차입니다.

### 1) 네임스페이스 및 Helm Repo 준비

```powershell
kubectl apply -f monitoring/00-namespace.yaml

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo add fluent https://fluent.github.io/helm-charts
helm repo update
```

### 2) Loki 설치 (단일 노드 권장)

Rancher Desktop `k3s` 단일 노드 환경에서는 `SingleBinary` values를 사용합니다.

```powershell
# 기존 loki가 있으면 삭제 후 재설치
helm uninstall loki -n flowkube-monitoring

# 단일 노드 values 사용
helm install loki grafana/loki -n flowkube-monitoring -f monitoring/loki-single-node-values.yaml
```

멀티 노드 클러스터에서는 `monitoring/loki-multi-node-values.yaml` 또는 차트 기본 분산 모드를 사용하면 됩니다.

### 3) Fluent Bit 설치 (Loki 연동 values 사용)

```powershell
helm install fluent-bit fluent/fluent-bit -n flowkube-monitoring -f monitoring/fluent-bit-loki-values.yaml
```

이미 설치된 Fluent Bit 설정을 갱신할 때:

```powershell
helm upgrade fluent-bit fluent/fluent-bit -n flowkube-monitoring -f monitoring/fluent-bit-loki-values.yaml
kubectl rollout restart daemonset/fluent-bit -n flowkube-monitoring
```

### 4) Prometheus + Grafana 설치

```powershell
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack -n flowkube-monitoring
```

### 5) 설치 확인

```powershell
kubectl get pods -n flowkube-monitoring
```

- **Loki**: Fluent Bit이 수집한 컨테이너 로그 저장
- **Fluent Bit**: Pod 라벨(`job_type`)을 Loki로 전달
- **Prometheus**: NiFi 메트릭 엔드포인트 `/nifi-api/flow/metrics/prometheus` 스크래핑
- **Grafana**: Loki 데이터소스로 `{namespace="flowkube-jobs"}`, `{job_type="..."}` 조회

추가로 loki-stack(일괄 설치) 방식을 사용할 경우, 프로젝트의 `k8s/fluent-bit-fix.yaml`로 labelmap(`job_type`)을 보정한 뒤 Fluent Bit DaemonSet을 재시작하면 됩니다.

---

## 참고 문서

- **프로젝트 정리.txt**: 다중 잡(BASIC/CPU_LOAD/LOG_GEN) 구성, Loki 라벨 설계, Fluent Bit 화이트리스트, JSON/YAML 트러블슈팅 등 상세 정리
