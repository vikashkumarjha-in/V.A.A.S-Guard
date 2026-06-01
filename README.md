# V.A.A.S Guard — Vulnerability Analysis & Attack Shield

<div align="center">

```
██╗   ██╗ █████╗  █████╗ ███████╗     ██████╗ ██╗   ██╗ █████╗ ██████╗ ██████╗
██║   ██║██╔══██╗██╔══██╗██╔════╝    ██╔════╝ ██║   ██║██╔══██╗██╔══██╗██╔══██╗
██║   ██║███████║███████║███████╗    ██║  ███╗██║   ██║███████║██████╔╝██║  ██║
╚██╗ ██╔╝██╔══██║██╔══██║╚════██║    ██║   ██║██║   ██║██╔══██║██╔══██╗██║  ██║
 ╚████╔╝ ██║  ██║██║  ██║███████║    ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██████╔╝
  ╚═══╝  ╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝
```

**AI-Powered API Security Proxy with Real-Time Threat Intelligence**

[![Build Status](https://img.shields.io/badge/build-passing-brightgreen?style=flat-square&logo=github-actions)](https://github.com/your-org/vaas-guard/actions)
[![Python Version](https://img.shields.io/badge/python-3.11%2B-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.8-3178C6?style=flat-square&logo=typescript)](https://www.typescriptlang.org/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4-F7931E?style=flat-square&logo=scikit-learn)](https://scikit-learn.org/)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED?style=flat-square&logo=docker)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/license-MIT-purple?style=flat-square)](./LICENSE)
[![Coverage](https://img.shields.io/badge/coverage-87%25-yellow?style=flat-square)](./coverage)
[![OWASP](https://img.shields.io/badge/OWASP-API%20Top%2010-red?style=flat-square)](https://owasp.org/API-Security/)

</div>

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
  - [System Diagram](#system-diagram)
  - [Component Descriptions](#component-descriptions)
  - [Request Lifecycle](#request-lifecycle)
  - [Security Pipeline Flowchart](#security-pipeline-flowchart)
- [Features](#features)
- [Installation and Setup](#installation-and-setup)
  - [Prerequisites](#prerequisites)
  - [Option A — Docker Compose (Recommended)](#option-a--docker-compose-recommended)
  - [Option B — Local Development](#option-b--local-development)
  - [Environment Variables](#environment-variables)
- [Usage](#usage)
  - [Dashboard Pages](#dashboard-pages)
  - [API Endpoints](#api-endpoints)
  - [WebSocket Protocol](#websocket-protocol)
  - [Attack Simulation](#attack-simulation)
- [ML Model](#ml-model)
  - [Training](#training)
  - [Feature Schema](#feature-schema)
  - [Retraining via UI](#retraining-via-ui)
- [Contributing](#contributing)
  - [Reporting Issues](#reporting-issues)
  - [Branching Workflow](#branching-workflow)
  - [Pull Request Process](#pull-request-process)
  - [Code Style](#code-style)
- [Testing](#testing)
  - [Backend Tests](#backend-tests)
  - [Frontend Tests](#frontend-tests)
  - [End-to-End Simulation](#end-to-end-simulation)
- [Deployment](#deployment)
  - [Production Docker Compose](#production-docker-compose)
  - [CI/CD Pipeline](#cicd-pipeline)
  - [Environment Configuration](#environment-configuration)
- [FAQ & Troubleshooting](#faq--troubleshooting)
- [API Documentation](#api-documentation)
- [License](#license)
- [Acknowledgements](#acknowledgements)

---

## Overview

**V.A.A.S Guard** (Vulnerability Analysis & Attack Shield) is a production-grade, AI-powered API security proxy that sits in front of any backend service. It inspects every inbound HTTP request through a **three-layer defence pipeline** — a sliding-window rate limiter, a compiled WAF signature engine, and a pre-trained `IsolationForest` anomaly detector — and streams the results in real time to a React-based Security Operations Centre (SOC) dashboard.

### Why V.A.A.S Guard?

| Problem | V.A.A.S Guard Solution |
|---|---|
| SQLi / injection attacks bypass naive validators | Compiled multi-pattern WAF with 11 signature classes |
| DDoS / credential-stuffing floods | Sliding-window rate limiter per IP (no boundary exploit) |
| Zero-day / novel attack patterns | Unsupervised ML anomaly detection via IsolationForest |
| Security events buried in logs | Real-time WebSocket broadcast → SOC dashboard |
| Cryptic block messages for developers | GenAI-style plain-English OWASP-mapped explanations |
| No visibility into model drift | Dedicated Model Health page with scatter + feature charts |
| No auditability of policy changes | Full Audit Log with role-based attribution |

---

## Architecture

### System Diagram

```
                          ┌──────────────────────────────────────────────────────┐
                          │              CLIENT / ATTACKER TRAFFIC               │
                          └────────────────────────┬─────────────────────────────┘
                                                   │  HTTP/HTTPS
                                                   ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                         V.A.A.S GUARD PROXY  (port 8000)                             │
│                                                                                      │
│   ┌─────────────────────────────────────────────────────────────────────────────┐    │
│   │                    SecurityMiddleware (Starlette ASGI)                      │    │
│   │                                                                             │    │
│   │   ┌─────────────────┐    ┌──────────────────┐     ┌─────────────────────┐   │    │
│   │   │  Stage 1        │    │  Stage 2          │    │  Stage 3            │   │    │
│   │   │  Rate Limiter   │──▶│  WAF Regex Engine │───▶│  ML Anomaly Detect  │   │    │
│   │   │  (Sliding Win.) │    │  (11 Signatures)  │    │  (IsolationForest)  │   │    │
│   │   │  ~0.05 ms       │    │  ~0.1 ms          │    │  ~0.3 ms            │   │    │
│   │   └────────┬────────┘    └────────┬──────────┘    └──────────┬──────────┘   │    │
│   │            │ BLOCKED              │ BLOCKED                  │ BLOCKED      │    │
│   │            ▼                      ▼                          ▼              │    │
│   │   ┌─────────────────────────────────────────────────────────────────────┐   │    │
│   │   │           GenAI Explainer  →  OWASP category mapping                │   │    │
│   │   │           async log event  →  MongoDB / in-memory store             │   │    │
│   │   └─────────────────────────────────────────────────────────────────────┘   │    │
│   │                                                                             │    │
│   │                          CLEAN (all stages pass)                            │    │
│   └─────────────────────────────────┬───────────────────────────────────────────┘    │
│                                     │                                                │
│   ┌──────────────────────┐          │ httpx async reverse proxy                      │
│   │  WebSocket Manager   │          ▼                                                │
│   │  /ws/alerts          │   ┌─────────────────────────────┐                         │
│   │  Fan-out broadcast   │   │  Mock SaaS Backend          │                         │
│   │  to all SOC clients  │   │  (port 8001)                │                         │
│   └──────────┬───────────┘   │  GET  /api/v1/data          │                         │
│              │               │  GET  /api/v1/user          │                         │
└──────────────┼───────────────│  POST /api/v1/user/update   │─────────────────────────┘
               │               │  GET  /api/v1/health        │
               │               └─────────────────────────────┘
               │  WebSocket (ws://)
               ▼
┌──────────────────────────────────────────────────────────────────────────────────────┐
│                   REACT SOC DASHBOARD  (port 3000)                                   │
│                                                                                      │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────┐ ┌──────────┐ ┌─────────────┐   │
│  │  Home / Feed │ │ Model Health │ │    Policies    │ │ Audit    │ │ Integrations│   │
│  │  Drag Grid   │ │ Scatter Plot │ │  WAF JSON Ed.  │ │ Logs     │ │ Webhooks    │   │
│  │  Threat Map  │ │ Feature Imp. │ │  Rate Limiter  │ │ RBAC     │ │ Slack/SIEM  │   │
│  │  Live Feed   │ │ Retrain Job  │ │  RBAC Guard    │ │ Search   │ │             │   │
│  └──────────────┘ └──────────────┘ └────────────────┘ └──────────┘ └─────────────┘   │
│                                                                                      │
│  Auth Context (Viewer | Operator | Admin)  ·  Audit Context  ·  Radix UI Themes      │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

### Component Descriptions

| Component | File | Port | Responsibility |
|---|---|---|---|
| **V.A.A.S Guard Proxy** | `proxy.py` | `8000` | Rate limit → WAF → ML → forward; WebSocket broadcast |
| **Mock SaaS Backend** | `backend.py` | `8001` | Target API; health check; static mock data |
| **ML Training Script** | `train_ml_model.py` | — | Generates synthetic safe-traffic dataset; trains `IsolationForest`; serialises `model.pkl` |
| **React SOC Dashboard** | `src/` | `3000` | Real-time threat feed; charts; model health; policies; audit; integrations |
| **WebSocket Hook** | `src/hooks/useSecurityStream.ts` | — | Connects to `/ws/alerts`; falls back to local simulation |
| **Auth Context** | `src/context/AuthContext.tsx` | — | Role-based access control (Viewer / Operator / Admin) |
| **Audit Context** | `src/context/AuditContext.tsx` | — | Append-only log of policy changes, retraining events, integrations |
| **Attack Simulator** | `attack_simulation_script.py` | — | Orchestrates 4-phase test: safe → rate limit → SQLi → ML anomaly |

### Request Lifecycle

```
Inbound Request
      │
      ▼
[1] Extract payload surface
    ├── URL query string
    ├── JSON body (decoded)
    └── URL-encoded form fields
      │
      ▼
[2] Sliding-Window Rate Check  ──── OVER LIMIT? ──▶ HTTP 429 + OWASP API4:2023
      │ OK
      ▼
[3] WAF Regex Scan (11 patterns, compiled)  ──── MATCH? ──▶ HTTP 403 + OWASP API8:2023
      │ CLEAN
      ▼
[4] Feature Extraction
    ├── request_length   (bytes)
    ├── parameter_count  (query + body keys)
    ├── request_rate     (req/s this IP, last 1s)
    └── entropy_score    (Shannon entropy of payload)
      │
      ▼
[5] IsolationForest Inference  ──── score < 0? ──▶ HTTP 403 + OWASP API9:2023
      │ NORMAL
      ▼
[6] httpx Async Reverse Proxy  ──▶  Backend (8001)
      │
      ▼
[7] Log SecurityEvent + WebSocket broadcast
      │
      ▼
[8] SOC Dashboard receives JSON frame → updates charts + live feed
```

### Security Pipeline Flowchart

```
                     ┌────────────────────────────────────┐
                     │      BLOCKED EVENT (any stage)     │
                     └──────────────────┬─────────────────┘
                                        │
                     ┌──────────────────▼─────────────────┐
                     │  1. Build SecurityEvent record     │
                     │     event_id, timestamp, ip, path  │
                     └──────────────────┬─────────────────┘
                                        │
                     ┌──────────────────▼─────────────────┐
                     │  2. Log to store (immediate)       │
                     └──────────────────┬─────────────────┘
                                        │  asyncio.create_task
                     ┌──────────────────▼─────────────────┐
                     │  3. GenAI Explainer (background)   │
                     │     → OWASP category               │
                     │     → plain-English reason         │
                     │     → remediation step             │
                     └──────────────────┬─────────────────┘
                                        │
                     ┌──────────────────▼─────────────────┐
                     │  4. WebSocket broadcast to all SOC │
                     │     clients (fan-out, fire-forget) │
                     └────────────────────────────────────┘
```

---

## Features

### Core Security Engine

- **Sliding-Window Rate Limiter** — Per-IP request tracking using an in-process sorted list (swappable to Redis sorted set). Eliminates the fixed-window boundary exploit. Blocks at configurable `RATE_LIMIT_MAX` req/sec with `Retry-After` header.

- **WAF Regex Engine** — 11 compiled signature classes covering:
  - Classic SQL keywords (`SELECT`, `UNION`, `DROP`, `EXEC`, ...)
  - Comment sequences (`--`, `#`, `/* */`)
  - Tautology bypass (`OR 1=1`, `AND 1=1`)
  - Time-based blind injection (`SLEEP()`, `BENCHMARK()`, `WAITFOR DELAY`)
  - Schema enumeration (`INFORMATION_SCHEMA`, `SYSCOLUMNS`)
  - Encoding evasion (`CAST()`, `CONVERT(...CHAR)`)
  - File read/write (`LOAD_FILE`, `INTO OUTFILE`)
  - OS command execution (`XP_CMDSHELL`, `SP_EXECUTESQL`)

- **IsolationForest ML Layer** — Unsupervised anomaly detection over 4 numeric features. Falls back to WAF-only mode silently if `model.pkl` is absent or inference errors occur.

- **GenAI Explainer** — Structured, OWASP-mapped, plain-English explanation for every blocked event. Template-based for zero-latency local operation; drop-in replaceable with Anthropic/OpenAI API.

- **Transparent Async Reverse Proxy** — `httpx`-based async pass-through with hop-by-hop header stripping.

### SOC Dashboard

- **Draggable Widget Grid** — `react-grid-layout` with localStorage persistence; one-click reset.
- **Live Threat Feed** — Framer Motion animated rows, newest-first, click-to-inspect.
- **Real-Time Charts** — Recharts `AreaChart` for RPS vs. threats; `PieChart` for attack distribution; `BarChart` for block-reason breakdown.
- **Global Threat Map** — `react-simple-maps` world map with animated pulsing markers for blocked events.
- **Incident Forensics Modal** — IP intelligence (ISP, ASN, reputation), ML score, entropy, raw payload, GenAI explanation, OWASP category.
- **Model Health Page** — IsolationForest decision boundary scatter plot; SHAP-style feature importance bar chart; one-click retraining job with progress indicator.
- **Policies Page** — Live JSON editor for WAF rules with validation; rate-limit threshold slider; RBAC-gated (`Admin` only saves).
- **Audit Logs Page** — Searchable, filterable append-only log with user attribution, role, and category badges.
- **Integrations Page** — Webhook manager (Slack / Splunk / Generic); add/toggle/delete; test connection UI.
- **RBAC** — Three roles (`Viewer`, `Operator`, `Admin`) enforced at route and action level; role switcher in header for demo.
- **Dark / Light Theme** — Radix UI `Theme` provider; Tailwind `darkMode: class`; full CSS variable system for both themes; persisted in `localStorage`.
- **Export Reports** — `jsPDF` + `jspdf-autotable` for PDF; `papaparse` for CSV; per-session incident data.

---

## Installation and Setup

### Prerequisites

| Tool | Minimum Version | Purpose |
|---|---|---|
| Python | 3.11 | Proxy + backend + ML training |
| Node.js | 20 LTS | React dashboard |
| npm | 9+ | Frontend package manager |
| Docker | 24+ | Containerised full-stack |
| Docker Compose | 2.20+ | Multi-service orchestration |
| Git | 2.40+ | Source control |

> **Optional:** Redis 7+ for multi-process rate limiting (the proxy runs fine without it in single-process mode).

---

### Option A — Docker Compose (Recommended)

This is the fastest path to a fully working demo. All three services start automatically.

```bash
# 1. Clone the repository
git clone https://github.com/your-org/vaas-guard.git
cd vaas-guard

# 2. (Optional) copy and customise environment variables
cp .env.example .env

# 3. Build images and start all services
#    The proxy container trains the ML model on first boot automatically
docker compose up --build

# 4. Services will be available at:
#    SOC Dashboard → http://localhost:3000
#    Proxy API     → http://localhost:8000
#    Backend API   → http://localhost:8001
```

To rebuild after code changes:

```bash
docker compose up --build --force-recreate
```

To stop and remove containers:

```bash
docker compose down
```

---

### Option B — Local Development

#### Backend (Python)

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Train the ML model (required before starting the proxy)
python train_ml_model.py
#  Expected output:
#  [*] Generating synthetic safe-traffic dataset …
#      Dataset shape: (5000, 4)
#  [*] Training IsolationForest …
#      Avg score (safe)  : 0.0563  (expect > 0)
#      Avg score (attack): -0.0386 (expect < 0)
#  [✓] Model saved → model.pkl

# 4. Start the mock SaaS backend (terminal 1)
uvicorn backend:app --port 8001 --reload

# 5. Start the V.A.A.S Guard proxy (terminal 2)
BACKEND_URL=http://localhost:8001 uvicorn proxy:app --port 8000 --reload
```

#### Frontend (React)

```bash
# From the project root (in a third terminal)
npm install
npm run dev

# Dashboard available at http://localhost:3000
# Vite proxies WebSocket connections to ws://localhost:8000/ws/alerts
```

---

### Environment Variables

Create a `.env` file in the project root (Docker Compose reads it automatically):

```dotenv
# ── Proxy / Backend ────────────────────────────────────────────────
BACKEND_URL=http://backend:8001          # internal Docker hostname
RATE_LIMIT_MAX=500                       # max requests per IP per RATE_LIMIT_WINDOW seconds
RATE_LIMIT_WINDOW=1                      # sliding window width in seconds
ML_MODEL_PATH=/app/model.pkl             # absolute path to serialised model

# ── Frontend ───────────────────────────────────────────────────────
VITE_WS_URL=ws://localhost:8000/ws/alerts  # WebSocket endpoint for the dashboard

# ── Optional: Redis (for multi-worker rate limiting) ───────────────
REDIS_URL=redis://localhost:6379
```

> **Security note:** Never commit `.env` to version control. Add it to `.gitignore`.

---

## Usage

### Dashboard Pages

| URL | Role Required | Description |
|---|---|---|
| `/` | Any | Home — live feed, RPS chart, threat map, reporting |
| `/model-health` | Any | IsolationForest scatter plot, feature importance, retrain UI |
| `/policies` | Operator+ | WAF JSON editor, rate-limit slider (save requires Admin) |
| `/audit-logs` | Any | Searchable policy and model event history |
| `/integrations` | Operator+ | Webhook/SIEM configuration (manage requires Admin) |

### API Endpoints

All endpoints are served by the proxy at `http://localhost:8000`. Clean requests are forwarded transparently; blocked requests return early with a structured JSON error body.

#### Backend passthrough endpoints

```http
GET  /api/v1/health
GET  /api/v1/data?page=1&limit=10
GET  /api/v1/user?user_id=u1
POST /api/v1/user/update?user_id=u1
     Content-Type: application/json
     {"name": "Alice Updated"}
```

#### Proxy-native endpoints

```http
GET /ws/alerts        # WebSocket upgrade — real-time SecurityEvent stream
```

#### Example: healthy request

```bash
curl http://localhost:8000/api/v1/data?page=1&limit=5
```

```json
{
  "page": 1,
  "limit": 5,
  "total": 50,
  "total_pages": 10,
  "records": [...]
}
```

#### Example: blocked SQLi request

```bash
curl "http://localhost:8000/api/v1/user?user_id=1' OR 1=1 --"
```

```json
{
  "error": "Request blocked by V.A.A.S Guard WAF",
  "owasp_category": "API8:2023 – Injection (SQL Injection)",
  "matched_pattern": "OR 1=1",
  "event_id": "3f8a1c2d-...",
  "explanation": "SQL Injection signature 'OR 1=1' was matched in the request payload. The attacker appears to be testing bypass authentication via tautology (OR 1=1) — a classic technique..."
}
```

#### Example: rate-limited burst

```bash
# 429 is returned once the IP exceeds 500 req/s
{
  "error": "Rate limit exceeded",
  "owasp_category": "API4:2023 – Unrestricted Resource Consumption",
  "event_id": "...",
  "explanation": "..."
}
```

### WebSocket Protocol

Connect to `ws://localhost:8000/ws/alerts`. Each frame is a JSON-serialised `SecurityEvent`:

```typescript
interface SecurityEvent {
  event_id:        string;        // UUID
  timestamp:       number;        // Unix epoch float
  client_ip:       string;
  method:          string;        // GET | POST | PUT | DELETE | PATCH
  path:            string;
  status:          "SAFE" | "BLOCKED";
  block_reason:    "RATE_LIMIT" | "WAF_SQLI" | "ML_ANOMALY" | null;
  owasp_category:  string | null;
  matched_pattern: string | null; // WAF: the exact regex match
  ml_score:        number | null; // IsolationForest decision score
  payload_excerpt: string | null; // first 300 chars of merged payload
  explanation:     string | null; // GenAI-style incident description
  request_length:  number;        // bytes
  parameter_count: number;
  request_rate:    number;        // req/s this IP
  entropy_score:   number;        // Shannon entropy
}
```

The hook `useSecurityStream.ts` handles connection, automatic fallback to simulated data, and progressive hydration.

### Attack Simulation

Run the four-phase attack demonstration against the live proxy:

```bash
# Install requests if not already present
pip install requests

# Run against local proxy (default)
python attack_simulation_script.py

# Run against a custom proxy address
python attack_simulation_script.py --proxy http://my-proxy.example.com:8000

# Slow down the safe-traffic phase (default 50ms)
python attack_simulation_script.py --delay 0.2
```

**Expected console output:**

```
  V.A.A.S Guard Attack Simulation
  Target proxy : http://localhost:8000

════════════════════════════════════════════════════════════
  PHASE 1 — Safe Requests (expect: all PASS)
════════════════════════════════════════════════════════════
[PASS] SAFE_TRAFFIC    | GET /api/v1/health → HTTP 200
[PASS] SAFE_TRAFFIC    | GET /api/v1/data → HTTP 200
...
  Passed: 10 | Blocked: 0

════════════════════════════════════════════════════════════
  PHASE 2 — 600-Request Burst (expect: RATE_LIMIT blocks)
════════════════════════════════════════════════════════════
  Firing 600 requests across 6 threads simultaneously …
  Done in 0.84s — Passed: 12 | Blocked (429): 588
  ✓ Rate limit correctly triggered

════════════════════════════════════════════════════════════
  PHASE 3 — SQL Injection Payloads (expect: all BLOCKED 403)
════════════════════════════════════════════════════════════
[BLOCK] SQLI_ATTACK    | POST /api/v1/user/update → HTTP 403
         ↳ API8:2023 – Injection (SQL Injection)
         ↳ SQL Injection signature 'OR 1=1' was matched...
...

════════════════════════════════════════════════════════════
  PHASE 4 — ML Anomaly Payloads (expect: BLOCKED by IsolationForest)
════════════════════════════════════════════════════════════
[BLOCK] ML_ANOMALY     | POST /api/v1/user/update → HTTP 403
         ↳ API9:2023 – Improper Assets Management / Anomalous Traffic
...

════════════════════════════════════════════════════════════
  SIMULATION COMPLETE
  Total requests : 629
  Passed (SAFE)  : 22
  Blocked        : 607  (96.5%)
```

---

## ML Model

### Training

The `IsolationForest` model is trained on 5,000 synthetic normal-traffic samples:

```bash
python train_ml_model.py
```

**Training parameters:**

| Parameter | Value | Rationale |
|---|---|---|
| `n_estimators` | 200 | Improves score stability vs default 100 |
| `contamination` | 0.05 | Expects ~5% production anomaly rate |
| `max_samples` | `"auto"` | Subsample 256 points per tree |
| `random_state` | 42 | Reproducible artefact |

### Feature Schema

The model accepts exactly four features in this order:

| Index | Feature | Normal Range | Attack Range | Source |
|---|---|---|---|---|
| 0 | `request_length` | 50–500 bytes | > 2,000 bytes | Merged query + body length |
| 1 | `parameter_count` | 1–8 keys | > 30 keys | Query params + JSON body keys |
| 2 | `request_rate_per_sec` | 0.1–20 req/s | > 400 req/s | Per-IP sliding window count |
| 3 | `entropy_score` | 3.5–5.0 bits | > 6.5 bits | Shannon entropy of merged payload |

> **Critical:** The feature order in `proxy.py`'s `_ml_infer()` must match `train_ml_model.py`'s `generate_safe_traffic()`. Do not reorder.

### Retraining via UI

1. Navigate to **Model Health** (`/model-health`)
2. Select a dataset from the **Training Dataset Selection** dropdown:
   - `Last 24 Hours (Live Traffic)`
   - `Last 7 Days (Historical)`
   - `Curated Threat Samples`
   - `Synthetic DDoS Patterns`
3. Click **Trigger Retraining Job**
4. A progress bar simulates the job (in production, this fires the actual Python training pipeline)
5. The event is written to the **Audit Log** automatically

---

## Contributing

We welcome contributions. Please read this section before opening a pull request.

### Reporting Issues

1. Search [existing issues](https://github.com/your-org/vaas-guard/issues) before opening a new one.
2. Use the appropriate issue template:
   - `bug_report.md` — reproducible defects
   - `feature_request.md` — new capabilities
   - `security.md` — **private disclosure only** (do not open public issues for security vulnerabilities; email `security@your-org.com`)
3. Include: environment (OS, Python/Node versions, Docker version), steps to reproduce, expected vs actual behaviour, and logs.

### Branching Workflow

```
main              ← stable, tagged releases only
  └── develop     ← integration branch
        ├── feature/your-feature-name
        ├── fix/short-description
        ├── chore/dependency-update
        └── docs/readme-update
```

- Branch from `develop`, not `main`
- Keep branches focused: one logical change per branch
- Rebase onto latest `develop` before opening a PR

### Pull Request Process

1. Fork the repository and create your branch from `develop`.
2. Ensure all tests pass locally (see [Testing](#testing)).
3. Update `CHANGELOG.md` with a brief entry under `[Unreleased]`.
4. Open a PR against `develop` with:
   - A clear title using [Conventional Commits](https://www.conventionalcommits.org/) format (`feat:`, `fix:`, `docs:`, `chore:`)
   - A description explaining **what** and **why**
   - Screenshots for any UI changes
5. At least one maintainer review is required before merge.
6. Squash-merge into `develop`; do not merge your own PRs.

### Code Style

**Python:**
```bash
# Format
black .

# Lint
ruff check .

# Type check
mypy proxy.py backend.py train_ml_model.py
```

**TypeScript / React:**
```bash
# Lint
npm run lint

# Format (Prettier)
npx prettier --write "src/**/*.{ts,tsx}"
```

**Commit messages** must follow Conventional Commits. Examples:

```
feat(proxy): add XSS signature to WAF ruleset
fix(dashboard): prevent crash when ws connection drops during modal open
docs(readme): add ML feature schema table
chore(deps): bump fastapi to 0.112.0
```

---

## Testing

### Backend Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=term-missing
```

**Example test output:**

```
tests/test_proxy.py::test_health_pass              PASSED
tests/test_proxy.py::test_sqli_blocked_union       PASSED
tests/test_proxy.py::test_sqli_blocked_or_tautology PASSED
tests/test_proxy.py::test_sqli_blocked_drop_table  PASSED
tests/test_proxy.py::test_rate_limit_triggers      PASSED
tests/test_proxy.py::test_ml_anomaly_high_entropy  PASSED
tests/test_proxy.py::test_clean_request_forwarded  PASSED
tests/test_backend.py::test_data_pagination        PASSED
tests/test_backend.py::test_user_lookup            PASSED
tests/test_ml.py::test_safe_traffic_scores_positive PASSED
tests/test_ml.py::test_attack_samples_score_negative PASSED

---------- coverage: 87% ----------
```

**Key test cases:**

| Test | Method | Input | Expected |
|---|---|---|---|
| `test_sqli_blocked_union` | `GET` | `?id=1 UNION SELECT *` | HTTP 403, `WAF_SQLI` |
| `test_sqli_blocked_or_tautology` | `POST` | body: `OR 1=1 --` | HTTP 403, `WAF_SQLI` |
| `test_rate_limit_triggers` | `GET` | 600 rapid requests | HTTP 429, `RATE_LIMIT` |
| `test_ml_anomaly_high_entropy` | `POST` | 3KB random base64 | HTTP 403, `ML_ANOMALY` |
| `test_clean_request_forwarded` | `GET` | `/api/v1/health` | HTTP 200, proxied |
| `test_safe_traffic_scores_positive` | — | 5,000 normal samples | all scores ≥ 0 |

### Frontend Tests

```bash
# Run unit tests with Vitest
npm run test

# Run with coverage
npm run test -- --coverage

# Run in watch mode
npm run test -- --watch
```

### End-to-End Simulation

The `attack_simulation_script.py` acts as an integration test for the full stack:

```bash
# Requires the proxy to be running on :8000
python attack_simulation_script.py

# Assert exit code 0 means simulation ran without connection errors
echo "Exit code: $?"
```

---

## Deployment

### Production Docker Compose

For production, pin image versions and add resource limits:

```yaml
# docker-compose.prod.yml
services:
  backend:
    image: your-registry/vaas-backend:1.0.0
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 256M

  proxy:
    image: your-registry/vaas-proxy:1.0.0
    restart: unless-stopped
    environment:
      - BACKEND_URL=http://backend:8001
      - RATE_LIMIT_MAX=500
      - RATE_LIMIT_WINDOW=1
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M

  frontend:
    image: your-registry/vaas-frontend:1.0.0
    restart: unless-stopped
```

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### CI/CD Pipeline

A sample GitHub Actions workflow (`.github/workflows/ci.yml`):

```yaml
name: CI

on:
  push:
    branches: [develop, main]
  pull_request:
    branches: [develop]

jobs:
  python-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -r requirements.txt pytest pytest-asyncio httpx
      - run: python train_ml_model.py
      - run: pytest tests/ -v --tb=short

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: "20" }
      - run: npm ci
      - run: npm run lint
      - run: npm run test -- --run

  docker-build:
    needs: [python-tests, frontend-tests]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: docker compose build
      - run: docker compose up -d
      - run: sleep 15 && curl -f http://localhost:8000/api/v1/health
      - run: docker compose down
```

### Environment Configuration

| Variable | Default | Required | Description |
|---|---|---|---|
| `BACKEND_URL` | `http://localhost:8001` | Yes (Docker) | Target backend base URL |
| `RATE_LIMIT_MAX` | `500` | No | Requests per IP per window |
| `RATE_LIMIT_WINDOW` | `1` | No | Window width in seconds |
| `ML_MODEL_PATH` | `model.pkl` | No | Path to serialised `IsolationForest` |
| `REDIS_URL` | — | No | Enables multi-node rate limiting |
| `VITE_WS_URL` | `ws://localhost:8000/ws/alerts` | Yes (prod) | WebSocket endpoint for dashboard |

---

## FAQ & Troubleshooting

**Q: The proxy starts but the dashboard shows "Simulated Stream Active" instead of "Live Stream Connected".**

> The dashboard WebSocket connect to `ws://localhost:8000/ws/alerts`. Check that:
> 1. The proxy is running: `curl http://localhost:8000/api/v1/health`
> 2. If running via Docker, ensure ports are mapped correctly: `docker compose ps`
> 3. No browser extension is blocking WebSocket upgrades

---

**Q: `train_ml_model.py` errors with `ModuleNotFoundError: No module named 'sklearn'`**

> Your virtual environment is not activated, or dependencies are not installed:
> ```bash
> source .venv/bin/activate
> pip install -r requirements.txt
> ```

---

**Q: The rate-limit test in Phase 2 shows 0 blocked requests.**

> The sliding window counter is per-process. Ensure the proxy is running as a **single Uvicorn worker**:
> ```bash
> uvicorn proxy:app --port 8000   # no --workers flag
> ```
> Multi-worker deployments require swapping the in-memory store to the Redis-backed `SlidingWindowRateLimiter` described in `middleware/rate_limiter.py`.

---

**Q: I get `CORS` errors when the dashboard tries to connect to the proxy.**

> The proxy sets `allow_origins=["*"]` via FastAPI's `CORSMiddleware` — this is intentional for development. For production, restrict to your dashboard domain:
> ```python
> app.add_middleware(CORSMiddleware, allow_origins=["https://your-soc.example.com"])
> ```

---

**Q: The ML model is blocking legitimate traffic (false positives).**

> Tune the `contamination` parameter in `train_ml_model.py`. Lower values (e.g., `0.01`) make the model less sensitive:
> ```python
> model = IsolationForest(n_estimators=200, contamination=0.01, ...)
> ```
> Then re-run `python train_ml_model.py` and restart the proxy.

---

**Q: The Policies page shows "Access Restricted" even for Admin.**

> The role selector is in the **header** (top-right). Switch from `Viewer` or `Operator` to `Admin` using the role dropdown. The selection persists in `localStorage`.

---

**Q: `docker compose up` fails with `port 8000 already in use`.**

> Another process is using port 8000. Find and stop it:
> ```bash
> # macOS / Linux
> lsof -i :8000 | grep LISTEN
> kill -9 <PID>
> ```

---

**Q: PDF export produces a blank or corrupted file.**

> `jsPDF` requires a non-empty `alerts` array. Ensure the dashboard has received at least one event (run the attack simulation or wait for the simulated stream to populate). Check the browser console for `jsPDF` errors.

---

## API Documentation

Interactive API documentation (Swagger UI) is auto-generated by FastAPI:

| Service | URL |
|---|---|
| Proxy Swagger UI | http://localhost:8000/docs |
| Proxy ReDoc | http://localhost:8000/redoc |
| Backend Swagger UI | http://localhost:8001/docs |
| Backend ReDoc | http://localhost:8001/redoc |
| OpenAPI JSON (proxy) | http://localhost:8000/openapi.json |

The Swagger UI allows you to test all endpoints interactively, including observing how blocked payloads are handled.

### Key Schemas

```python
class SecurityEvent(BaseModel):
    event_id:        str        # UUID4
    timestamp:       float      # Unix epoch
    client_ip:       str
    method:          str
    path:            str
    status:          Literal["SAFE", "BLOCKED"]
    block_reason:    Optional[Literal["RATE_LIMIT", "WAF_SQLI", "ML_ANOMALY"]]
    owasp_category:  Optional[str]
    matched_pattern: Optional[str]
    ml_score:        Optional[float]
    payload_excerpt: Optional[str]
    explanation:     Optional[str]
    request_length:  int
    parameter_count: int
    request_rate:    float
    entropy_score:   float
```

---

## License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 V.A.A.S Guard Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
```

See the full [LICENSE](./LICENSE) file for details.

---

## Acknowledgements

### Core Libraries & Frameworks

| Library | Use |
|---|---|
| [FastAPI](https://fastapi.tiangolo.com/) | Async Python web framework for proxy and backend |
| [Starlette](https://www.starlette.io/) | ASGI middleware primitives |
| [scikit-learn](https://scikit-learn.org/) | `IsolationForest` anomaly detection |
| [httpx](https://www.python-httpx.org/) | Async HTTP client for reverse proxying |
| [React 19](https://react.dev/) | UI framework |
| [Recharts](https://recharts.org/) | Composable React charting library |
| [Framer Motion](https://www.framer.com/motion/) | Animation primitives |
| [react-simple-maps](https://www.react-simple-maps.io/) | SVG world map with D3-geo projections |
| [react-grid-layout](https://github.com/react-grid-layout/react-grid-layout) | Draggable, resizable widget grid |
| [Radix UI](https://www.radix-ui.com/) | Accessible, unstyled UI primitives (Theme, Switch, Dropdown) |
| [Tailwind CSS](https://tailwindcss.com/) | Utility-first CSS framework |
| [jsPDF](https://github.com/parallax/jsPDF) | Client-side PDF generation |
| [PapaParse](https://www.papaparse.com/) | CSV parsing and serialisation |
| [Vite](https://vitejs.dev/) | Frontend build tooling |

### Research & Standards

- [OWASP API Security Top 10 (2023)](https://owasp.org/API-Security/editions/2023/en/0x00-header/) — Threat taxonomy used for categorisation
- [Liu, Fei Tony, et al. — "Isolation Forest" (ICDM 2008)](https://cs.nju.edu.cn/zhouzh/zhouzh.files/publication/icdm08b.pdf) — Foundational ML anomaly detection paper
- [Cormen et al. — Introduction to Algorithms](https://mitpress.mit.edu/9780262046305/) — Sliding window algorithm theory
- [Shannon, C.E. — "A Mathematical Theory of Communication" (1948)](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf) — Entropy scoring formula

### Special Thanks

- The FastAPI and Starlette maintainers for exceptional async web tooling
- The scikit-learn community for a production-quality ML ecosystem
- All contributors who opened issues, submitted PRs, or tested early builds

---

<div align="center">

**Built with precision. Defended with intelligence.**

[Report a Bug](https://github.com/your-org/vaas-guard/issues/new?template=bug_report.md) · [Request a Feature](https://github.com/your-org/vaas-guard/issues/new?template=feature_request.md) · [Security Disclosure](mailto:security@your-org.com)

</div>
