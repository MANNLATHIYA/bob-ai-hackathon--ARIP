# Clinical Trial Risk Monitor & Protocol Deviation Detector

> **Trial Sentinel** is an explainable, synthetic-data-only hackathon demo that detects protocol deviations, prioritizes risky sites, and creates human-reviewable CAPA drafts before issues compound.

![Python](https://img.shields.io/badge/Python-3.11+-123c31) ![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-059669) ![React](https://img.shields.io/badge/React-TypeScript-2563eb) ![Data](https://img.shields.io/badge/Data-100%25_synthetic-e86f51)

## Team

- **Team name:** ARIP TEAM
- **Team lead:** Mann Lathiya
- **Contact:** lathiyamann49@gmail.com

## Problem statement

A global trial can generate thousands of visits across hundreds of sites. Missed visits, incorrect dosing, prohibited co-medications, and incomplete assessments can remain buried until monitoring or an audit—too late for inexpensive intervention. Clinical Risk Managers, CRAs, and Sponsor QA teams need a live, explainable worklist that shows where risk is accumulating and why.

## Solution

Trial Sentinel ingests a machine-readable protocol and synthetic patient-visit records, applies deterministic compliance rules, optionally reviews ambiguous notes through a swappable LLM adapter, assigns an impact-oriented severity, and ranks all 200 sites with a transparent risk formula. Every finding retains its protocol clause, rationale, confidence, and source. Users can drill into a site trend and export a structured CAPA draft as PDF or DOCX.

The local demo works fully without an API key. “IBM Bob” is represented by the modular Python orchestration boundary connecting ingestion, deviation detection, severity classification, scoring, and CAPA generation.

## Key features

- Deterministic detection of missed/out-of-window visits, dose amount, route, banned medications, and missing assessments
- Optional OpenAI-compatible or Anthropic note review behind one `LLMClient` interface
- Rule-first severity classification: `MAJOR`, `MINOR`, or `ADMINISTRATIVE`, with rationale and protocol traceability
- 0–100 site-risk ranking using seven documented leading indicators and Low/Medium/High/Critical bands
- Sortable risk table, visual bands, deviation filtering, site drill-down, and monthly trend chart
- One-click CAPA generation with root-cause hypothesis, corrective/preventive actions, owner, target date, effectiveness check, and PDF/DOCX export
- Deterministic generator for 200 fictional sites, 1,000 fictional participants, and exactly 5,000 fictional visits
- FastAPI OpenAPI documentation, SQLite local persistence, Docker Compose, backend tests, and GitHub Actions CI

## Tech stack

| Layer | Technology |
|---|---|
| API and orchestration | Python 3.11+, FastAPI, Pydantic |
| Storage | SQLAlchemy + SQLite (database URL is replaceable) |
| Rules and scoring | Typed deterministic Python modules |
| AI | Optional OpenAI-compatible Chat Completions or Anthropic Messages API |
| Reports | ReportLab PDF + python-docx |
| Frontend | React, TypeScript, Tailwind CSS, Recharts, Lucide |
| Operations | Docker, Docker Compose, GitHub Actions |

## Repository structure

```text
├── src/
│   ├── ingestion/          # CSV/JSON and HL7-like VIS parser
│   ├── deviation_engine/   # deterministic rules, severity, LLM adapters
│   ├── risk_scoring/       # explicit weighted site model
│   ├── capa_generator/     # narrative and PDF/DOCX exports
│   ├── api/                # FastAPI, schemas, persistence, seeding
│   └── frontend/           # React + TypeScript + Tailwind dashboard
├── data/
│   ├── generate_synthetic.py
│   └── sample/             # protocol; CSVs materialize on first run
├── docs/                   # problem, solution, architecture, setup
├── demo/                   # screenshot/video placeholders
├── presentation/           # eight-slide submission outline
├── tests/                  # engine, scoring, API integration tests
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── submission.yaml
```

## How to run

### Docker (recommended)

```bash
cp .env.example .env
docker compose up --build
```

Open the dashboard at <http://localhost:3000> and API docs at <http://localhost:8000/docs>. The first API start creates the entire synthetic dataset and analyzes it. An API key is not needed.

### Local

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python data/generate_synthetic.py
uvicorn src.api.main:app --reload
```

Then, in another terminal:

```bash
cd src/frontend
npm install
npm run dev
```

See [docs/setup-guide.md](docs/setup-guide.md) for LLM configuration and verification commands.

## API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/patients` | Paginated fictional participants, optional site filter |
| GET | `/visits` | Paginated synthetic visits, optional site filter |
| GET | `/deviations` | Severity/site/date-filtered findings |
| GET | `/sites/risk` | Ranked 0–100 site risk with monthly trends |
| GET | `/sites/{site_id}` | Site, risk, and recent findings |
| POST | `/capa/generate` | Draft CAPA by deviation or site; Markdown/PDF/DOCX |

## Demo

1. Open **Site overview** and inspect the risk-ranked worklist.
2. Select a high-risk site to view monitoring recency, Major count, and trend.
3. Open **Deviation feed**, filter severity, and inspect the cited clause and rationale.
4. Click **Generate CAPA PDF** on any finding.

The final video link belongs in `demo/demo-video-link.txt`; final screenshots belong in `demo/screenshots/`.

## Clinical and regulatory design notes

The severity labels are operational demo conventions informed by protocol compliance, record quality, monitoring, and noncompliance controls in ICH E6(R2); they are not asserted to be an ICH-defined taxonomy. The full rule mapping, exact risk weights, AI controls, and data flow are documented in [docs/architecture.md](docs/architecture.md).

## Known limitations

- All shipped/generated data is synthetic. The system must not be used with real participant data in its current form.
- LLM findings and severity suggestions require qualified human review and sign-off for any regulatory or clinical use.
- No live EHR, EDC, CTMS, ePRO, laboratory, or safety-system integration exists; ingestion adapters are demonstration connectors.
- Authentication and authorization are intentionally simplified for a local hackathon demo.
- The application is not validated against 21 CFR Part 11, EU Annex 11, sponsor SOPs, computer-system validation, or production GxP controls.
- It does not provide medical advice, automated eligibility decisions, or autonomous safety reporting.
- The risk weights and thresholds are transparent assumptions, not clinically calibrated or prospectively validated.
- CAPA root causes are hypotheses; investigation, approval, effectiveness checks, signatures, and audit trails remain human responsibilities.

## Responsible use

Use only fictional data. Keep LLM credentials server-side, follow organizational governance, and require investigator/QA review of every material decision. This repository demonstrates earlier risk visibility; it is not a replacement for clinical judgment, monitoring plans, or controlled quality processes.
