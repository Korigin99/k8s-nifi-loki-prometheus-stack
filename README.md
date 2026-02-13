FlowKube: NiFi-K8s Dynamic Job Automation & Monitoring
FlowKube는 Apache NiFi를 컨트롤 타워로 사용하여 Kubernetes(k3s) 클러스터 내에 Python 작업용 Pod를 동적으로 생성하고, 발생하는 로그와 메트릭을 PLG(Prometheus, Loki, Grafana) 스택으로 통합 모니터링하는 자동화 프로젝트입니다.

🚀 프로젝트 개요
Dynamic Orchestration: NiFi가 K8s API를 통해 필요한 시점에만 Python 컨테이너를 실행합니다.

Multi-Functional Workers: CPU 부하 테스트, 로그 스트리밍, I/O 작업 등 다양한 목적의 Python 모듈을 제공합니다.

Full-Stack Monitoring: Fluent Bit을 통한 로그 수집(Loki) 및 NiFi API 기반 메트릭 수집(Prometheus)을 지원합니다.

📂 프로젝트 구조
Plaintext
├── k8s/                # Kubernetes 매니페스트 (Namespace, RBAC, NiFi 배포)
├── python/             # Python 작업 모듈 및 Dockerfile
├── nifi/               # NiFi Flow 정의 파일 (JSON)
└── monitoring/         # 모니터링 스택 설정 (Helm, Fluent Bit)
🛠️ 주요 구성 요소
1. Infrastructure (K8s)
Namespace: nifi-system (관리용), python-jobs (작업용)

RBAC: NiFi가 python-jobs 네임스페이스에서 Pod를 제어할 수 있는 권한 부여

NiFi: Apache NiFi 2.6.0 (HTTPS 기반)

2. Python Workers
Basic: 단순 실행 확인용 (app.py)

CPU Worker: 소수 계산을 통한 CPU 부하 시뮬레이션 (app_cpu.py)

Log Worker: 다양한 로그 레벨(INFO, WARN, ERROR) 테스트용 (app_log.py)

3. NiFi Pipeline
Generate: Pod 생성용 JSON 템플릿 생성

Transform: 실행 시점마다 고유한 Pod ID 부여 (PLACEHOLDER 치환)

Authorize: K8s ServiceAccount 토큰 획득

Execute: K8s API 호출을 통한 Pod 생성

⚡ 퀵 스타트
1. 환경 준비 (Rancher Desktop / k3s)
PowerShell
# 네임스페이스 및 권한 설정
kubectl apply -f k8s/00-namespaces.yaml
kubectl apply -f k8s/nifi-rbac.yaml

# NiFi 배포
kubectl apply -f k8s/nifi-deployment.yaml
2. Python 이미지 빌드
PowerShell
cd python
docker build -t test-python:cpu --build-arg APP_FILE=app_cpu.py .
docker build -t test-python:log --build-arg APP_FILE=app_log.py .
3. NiFi 접속 및 플로우 로드
URL: https://localhost:8443/nifi (포트 포워딩 필요)

계정: admin / AdminPassword123

설정: NiFi_Flow.json을 가져온 후 InvokeHTTP의 URL 및 인증 확인

📊 모니터링 연동 (PLG Stack)
Prometheus: NiFi 메트릭 API(.../nifi-api/flow/metrics/prometheus) 수집

Loki: Fluent Bit이 수집한 python-jobs 네임스페이스 로그 저장

Grafana: 통합 대시보드를 통한 실시간 작업 현황 시각화