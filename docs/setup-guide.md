# Setup guide

## One-command Docker demo

Prerequisite: Docker Desktop with Compose v2.

```bash
cp .env.example .env
docker compose up --build
```

Open <http://localhost:3000>. API docs are at <http://localhost:8000/docs>. No LLM key is required.

## Local development

Prerequisites: Python 3.11+ and Node.js 20+.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
python data/generate_synthetic.py
uvicorn src.api.main:app --reload
```

In a second terminal:

```bash
cd src/frontend
npm install
npm run dev
```

Open <http://localhost:5173>. The backend automatically generates sample CSV files on first start if they are absent.

## Optional LLM enrichment

Copy `.env.example` to `.env`, set `LLM_API_KEY`, and choose `LLM_PROVIDER=openai` (any compatible chat-completions endpoint through `LLM_BASE_URL`) or `LLM_PROVIDER=anthropic`. Never put a key in `VITE_*` variables. Restart the API after changing configuration.

## Verification

```bash
ruff check src tests data/generate_synthetic.py
pytest --cov=src
cd src/frontend && npm run build
```

To reset the local demo, stop the API and remove only `clinical_trial.db`; it is regenerated at the next start.

