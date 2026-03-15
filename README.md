# Representment Agent Demo

A full-stack demo of an AI-powered chargeback representment agent for merchants. The agent receives chargeback disputes from banks (mock Chase protocol), investigates order and payment history, decides whether to defend or accept, and generates a formal representment note — all visualized in real time through a web UI.

## Architecture

```
┌──────────────────────────────┐      ┌─────────────────────┐
│  React Frontend (Vite + TS)  │ SSE  │  FastAPI Backend     │
│  - Dashboard                 │◄────►│  - REST API          │
│  - Case Detail + Timeline    │      │  - LangChain Agent   │
│  - Representment Note Viewer │      │  - Mock Bank API     │
└──────────────────────────────┘      │  - SQLite Database   │
                                      └────────┬────────────┘
                                               │ OpenAI-compat
                                               ▼
                                      ┌─────────────────────┐
                                      │  LLM on B300 GPU    │
                                      │  (vLLM + Qwen 3.5)  │
                                      └─────────────────────┘
```

## Prerequisites

- Python 3.9+ (3.13 recommended)
- Node.js 18+
- [uv](https://docs.astral.sh/uv/) — fast Python package manager
- An OpenAI-compatible LLM endpoint (ChatGPT API, or vLLM on B300 GPU)

## Quick Start

### 1. Backend

```bash
cd backend

# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install dependencies
uv venv
uv pip install -r requirements.txt

# Configure the LLM endpoint
cp .env.example .env
# Edit .env with your API key / endpoint (see Configuration below)

# Start the API server
uv run uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

The backend will:
- Create a SQLite database (`representment.db`) on first startup
- Seed it with demo customer, order, and payment data
- Pre-load a chargeback case from Chase (CB-2026-0314)

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server (proxies /api to backend at localhost:8080)
npm run dev
```

Open http://localhost:5173 in your browser.

## Demo Walkthrough

1. **Dashboard** — You'll see a pre-seeded chargeback case from Chase Bank: a $1,249.99 dispute by "John Smith" claiming fraud.

2. **Click the case** to open the detail view.

3. **Click "Resolve with Agent"** — The LangChain agent will:
   - Look up "John Smith" in the customer database
   - Retrieve his order history (Samsung TV delivered to his registered address)
   - Retrieve his payment history (3 successful purchases with the same Chase card)
   - Analyze the evidence against the chargeback claim
   - Decide to **defend** (strong evidence of legitimate transaction)
   - Generate a formal representment note
   - Submit it to the mock Chase bank API

4. **Watch the timeline** — Each agent step appears in real time via Server-Sent Events.

5. **Read the representment note** — A formal defense letter citing delivery confirmation, customer history, and payment authentication.

6. **Simulate more chargebacks** — Click "Simulate Chase Chargeback" on the dashboard to create additional cases.

## Serving a Model on B300 GPU

Two SLURM scripts are provided in `scripts/` to serve an open-source model via vLLM:

### Batch Job (unattended, 8 hours)

```bash
# On the cluster login node
sbatch scripts/serve_model.sh

# Check status
squeue --me

# View logs for connection info
tail -f logs/vllm-<JOB_ID>.out
```

### Interactive Session (quick testing, 2 hours)

```bash
./scripts/serve_interactive.sh
```

### Connecting to the GPU Model

Once vLLM is running, the logs will print the GPU node hostname. Create an SSH tunnel from your local machine:

```bash
ssh -L 8000:<gpu-node-hostname>:8000 <login-node>
```

Then update `backend/.env`:

```
LLM_BASE_URL=http://localhost:8000/v1
LLM_MODEL_NAME=Qwen/Qwen3.5-27B
LLM_API_KEY=dummy-key
```

Restart the backend and the agent will use the B300 GPU model.

### Using a Different Model

```bash
MODEL_NAME=meta-llama/Llama-3.1-70B-Instruct sbatch scripts/serve_model.sh
```

## Configuration

| Environment Variable | Default | Description |
|---|---|---|
| `LLM_BASE_URL` | `https://api.openai.com/v1` | Base URL of the OpenAI-compatible LLM API |
| `LLM_MODEL_NAME` | `gpt-4o` | Model name to use for inference |
| `LLM_API_KEY` | (empty) | API key for the LLM endpoint |
| `DATABASE_URL` | `sqlite:///./representment.db` | SQLAlchemy database connection string |

## Project Structure

```
backend/
  main.py                      # FastAPI entry point
  config.py                    # Environment config
  agent/
    representment_agent.py     # LangChain agent + tools + SSE streaming
    prompts.py                 # System prompt + representment note template
  mock_bank/
    bank_api.py                # Mock Chase bank chargeback protocol
    schemas.py                 # Pydantic models for bank communication
  database/
    db.py                      # SQLite/SQLAlchemy setup
    models.py                  # ORM models (Customer, Order, Payment, Chargeback)
    seed_data.py               # Demo data seeder
  routes/
    chargebacks.py             # Chargeback CRUD + agent resolve (SSE)
    bank_webhook.py            # Mock bank webhook + submission endpoints

frontend/
  src/
    App.tsx                    # App shell + routing
    pages/
      Dashboard.tsx            # Case list + simulate button
      CaseDetail.tsx           # Case detail + agent timeline + representment note
    components/
      AgentTimeline.tsx        # Real-time agent step visualization
      ChargebackCard.tsx       # Case summary card
      RepresentmentNote.tsx    # Formal letter renderer
      StatusBadge.tsx          # Status indicator badge
    hooks/
      useAgentStream.ts        # SSE EventSource hook
    api/
      client.ts                # API client

scripts/
  serve_model.sh               # SLURM batch job for vLLM on B300
  serve_interactive.sh          # SLURM interactive session for vLLM on B300
```
