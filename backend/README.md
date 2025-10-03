# Healthcare AI Assistant - Backend (FastAPI)

This backend provides REST endpoints for:
- Patient CRUD: /patients
- Patient chat history: /patients/{id}/history
- Chat send: /chat/send

Environment configuration uses .env.
See `.env.example` for required variables.

Run locally:
- python -m venv .venv && source .venv/bin/activate
- pip install -r requirements.txt
- export $(grep -v '^#' .env | xargs)  # or set env vars via your shell
- uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

OpenAPI spec:
- Visit /docs
- Generate file: `python -m src.api.generate_openapi`
