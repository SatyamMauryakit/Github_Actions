# Github_Actions

A reference repository that demonstrates an end-to-end **DevSecOps pipeline** using **GitHub Actions** for a simple Flask application packaged with Docker.

This repo includes:
- A small Flask app (`app.py` + `run.py`)
- Docker image build instructions (`Dockerfile`)
- A runtime definition using Docker Compose (`docker-compose.yml`)
- Multiple reusable GitHub Actions workflows under `.github/workflows/`

---

## Repository structure

```text
.
├── .github
│   └── workflows
│       ├── code-quality.yml
│       ├── dependency-scan.yml
│       ├── deploy-app.yml
│       ├── deploy-server.yml
│       ├── devsecops-pipeline.yml
│       ├── docker-lint.yml
│       ├── docker_build_push.yml
│       ├── image-scan.yml
│       ├── python_matrix.yml
│       └── secrets-scan.yml
├── templates
│   └── index.html
├── app.py
├── run.py
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

---

## Application overview

- **Framework:** Flask
- **Entry point:** `run.py`
- **Default port:** `80`
- **UI template:** `templates/index.html`

### Run locally (Python)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run.py
```

Open: `http://localhost:80`

### Run locally (Docker)

```bash
docker build -t github-action-1:local .
docker run --rm -p 80:80 github-action-1:local
```

### Run locally (Docker Compose)

`docker-compose.yml` expects two environment variables:
- `DOCKER_USERNAME`
- `DOCKER_TAG`

Example:

```bash
export DOCKER_USERNAME=<your-dockerhub-username>
export DOCKER_TAG=local

# If the image exists locally, compose can use it
docker compose up -d
```

---

## GitHub Actions: what this repository demonstrates

This repository shows a typical **CI/CD + security** pipeline:

1. **Code quality checks** (lint + SAST)
2. **Dependency vulnerability scan**
3. **Secrets scan**
4. **Dockerfile lint**
5. **Build and push container image**
6. **Container image vulnerability scan**
7. **Deploy to server** (via SSH + Docker Compose)

The main pipeline is defined in:
- `.github/workflows/devsecops-pipeline.yml`

It runs automatically on:
- `push` to the `main` branch

---

## Workflows explained

> Many workflows here are **reusable workflows** triggered by `workflow_call`.
> The `devsecops-pipeline.yml` workflow composes them together using `uses: ./.github/workflows/<file>.yml`.

### 1) Code Quality (`code-quality.yml`)
**Trigger:** `workflow_call` (reusable)

What it does:
- Runs `flake8` on `app.py`
- Runs `bandit` on `app.py` (SAST)
- Uses a **matrix** of Python versions (`3.11`, `3.12`, `3.13`)

### 2) Dependency Scan (`dependency-scan.yml`)
**Trigger:** `workflow_call` (reusable)

What it does:
- Runs `pip-audit -r requirements.txt`

### 3) Secrets Scan (`secrets-scan.yml`)
**Trigger:** `workflow_call` (reusable)

What it does:
- Runs `gitleaks/gitleaks-action@v2`
- Uses `fetch-depth: 0` to scan the full git history

### 4) Dockerfile Lint (`docker-lint.yml`)
**Trigger:** `workflow_call` (reusable)

What it does:
- Runs `hadolint` on `Dockerfile`

### 5) Build + Push Image (`docker_build_push.yml`)
**Trigger:** `workflow_call` (reusable)

What it does:
- Logs into DockerHub
- Builds and pushes the image to DockerHub

Tags pushed:
- `<DOCKER_USERNAME>/github-action-1:<branch>`
- `<DOCKER_USERNAME>/github-action-1:latest`
- `<DOCKER_USERNAME>/github-action-1:<commit-sha>`

### 6) Image Vulnerability Scan (`image-scan.yml`)
**Trigger:** `workflow_call` (reusable)

What it does:
- Runs Trivy scan on the pushed image tag `<commit-sha>`
- Fails the pipeline if any **CRITICAL** vulnerabilities are found (`exit-code: 1`)

### 7) Deploy to server (`deploy-server.yml`)
**Trigger:** `workflow_call` (reusable)

What it does:
- SSH to an EC2/VM server
- Installs Docker + Compose
- Copies `docker-compose.yml` to `~/devops`
- Logs into DockerHub
- Runs `docker compose up -d --build --force-recreate --pull always`

### 8) Manual deploy on self-hosted runner (`deploy-app.yml`)
**Trigger:** `workflow_dispatch`

What it does:
- Runs on a **self-hosted** runner
- Deploys locally using Docker Compose

### 9) Python matrix lint example (`python_matrix.yml`)
**Trigger:** `workflow_dispatch`

What it does:
- A standalone example of running `flake8` across a Python version matrix

---

## Required GitHub Variables & Secrets

This repository uses both **Variables** (`Settings → Secrets and variables → Actions → Variables`) and **Secrets**.

### Variables
- `DOCKER_USERNAME`

### Secrets
- `DOCKERHUB_TOKEN` (DockerHub access token/password)
- `EC2_SSH_HOST` (server public IP / DNS)
- `EC2_SSH_USERNAME` (e.g., `ubuntu`)
- `EC2_SSH_KEY` (private key for SSH)

> Tip: `deploy-server.yml` and the image workflows use `secrets: inherit` when called from the main pipeline, so you only manage secrets in one place.

---

## How to use the pipeline

### Run full DevSecOps pipeline
1. Commit and push to `main`
2. Open the **Actions** tab and watch **DevSecOps end to end Pipeline**

### Run manual workflows
In the **Actions** tab:
- Run **Deploy Flask App** (`deploy-app.yml`)
- Run **Python lint** (`python_matrix.yml`)

---

## Notes / improvements

- Consider pinning all Python dependencies to exact versions for reproducible scans.
- Consider adding unit tests and running them before building the image.
- Consider adding environment protection rules for production deployments.

---

## Useful links

- Workflows directory: https://github.com/SatyamMauryakit/Github_Actions/tree/main/.github/workflows
- Actions page: https://github.com/SatyamMauryakit/Github_Actions/actions
