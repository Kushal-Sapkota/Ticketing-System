# Ticketing System — DevOps Project

IT Helpdesk ticketing system used as a platform to apply a full DevOps pipeline from containerization to monitoring.

**Stack:** FastAPI · PostgreSQL · Redis · React (Vite) · Nginx

---

## Pipeline Overview
GitHub → Jenkins → Docker Hub → Kubernetes → Prometheus/Grafana

**Kubernetes workloads:**

| Component | Kind | Details |
|-----------|------|---------|
| Backend | Deployment | 2 replicas, HPA (2–5), `/health` probes |
| Frontend | Deployment | Nginx, serves React build |
| PostgreSQL | StatefulSet | PV/PVC for persistence |
| Redis | Deployment | Session/cache store |
| Ingress | Ingress | nginx, routes `/api/*` and `/` |

---

## Phases

**Phase 1 — Containerization**
- Multistage Dockerfiles for backend (Python/venv) and frontend (Node → Nginx)
- Non-root users, health checks, named volumes
- Docker Compose v2 with service health dependencies

**Phase 2 — CI/CD (Jenkins)**
- Declarative pipeline: Checkout → Build → Push → Deploy
- Images pushed to Docker Hub as `kushal81/ticketing-backend` and `kushal81/ticketing-frontend`
- Secrets injected via Jenkins credentials, `.env` generated at deploy time

**Phase 3 — Kubernetes**
- Namespace: `ticketing`
- PostgreSQL as StatefulSet with PV/PVC
- Backend with 2 replicas, liveness/readiness probes on `/health`
- Ingress routing `/api/*` to backend, `/` to frontend
- HPA on backend (2–5 replicas, 70% CPU threshold)
- ResourceQuota on namespace

**Phase 4 — Helm**
- Full stack packaged as a Helm chart under `helm/ticketing/`
- `values.yaml` controls image tags, replicas, resources, ingress host
- Deploy: `helm install ticketing helm/ticketing/ --namespace ticketing`

**Phase 5 — Monitoring**
- `kube-prometheus-stack` installed via Helm in `monitoring` namespace
- `prometheus-fastapi-instrumentator` exposes `/metrics` on backend
- ServiceMonitor scrapes both backend replicas every 15s
- Grafana dashboards for HTTP request rate, latency, pod resource usage

---

## Local Setup

### Prerequisites
- Docker + Docker Compose v2
- Minikube + kubectl
- Helm v3
- Jenkins (native)

### Run with Docker Compose
```bash
cp .env.example .env
# fill in secrets, then:
docker compose up --build
```
Access: `http://localhost:3000`

### Run with Kubernetes
```bash
minikube start
helm install ticketing helm/ticketing/ --namespace ticketing --create-namespace
echo "$(minikube ip) ticketing.local" | sudo tee -a /etc/hosts
```
Access: `http://ticketing.local`

### Run with Jenkins
- Add `dockerhub-credentials` (Docker Hub token) to Jenkins global credentials
- Add `ticketing-jwt-secret` and `ticketing-db-password` as Secret Text credentials
- Create Pipeline job pointing to this repo, branch `main`, script path `Jenkinsfile`

---

## Repository Structure
.
├── backend/            # FastAPI application
├── frontend/           # React + Vite application
├── helm/ticketing/     # Helm chart
├── k8s/                # Raw Kubernetes manifests
├── Jenkinsfile         # CI/CD pipeline
└── docker-compose.yml

---

## Images
- `kushal81/ticketing-backend`
- `kushal81/ticketing-frontend`
