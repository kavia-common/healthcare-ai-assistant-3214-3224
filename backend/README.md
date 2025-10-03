# Healthcare AI Assistant - Backend (FastAPI)

This backend provides REST endpoints for:
- Patient CRUD: /patients
- Patient chat history: /patients/{id}/history
- Chat send: /chat/send

Database (local development):
- Uses SQLite by default with a local file database at `./dev.db`.
- Configure via `DATABASE_URL` in `.env` (defaults to `sqlite:///./dev.db`).
- Example alternative: point to a different SQLite file: `sqlite:///./my_local.db`.

Environment configuration uses .env.
See `.env.example` for required variables.

Run locally:
- python -m venv .venv && source .venv/bin/activate
- pip install -r requirements.txt
- cp .env.example .env  # update values if needed
- export $(grep -v '^#' .env | xargs)  # or set env vars via your shell
- uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

OpenAPI spec:
- Visit /docs
- Generate file: `python -m src.api.generate_openAPI`

Notes:
- To use a production-grade DB, set `DATABASE_URL` to your target (e.g., PostgreSQL). SQLite remains the default for local dev.
- Flake8 is configured via `.flake8` to exclude the local virtual environment (`.venv`) and vendor packages from linting. If you see linter errors coming from site-packages, ensure you run flake8 from the `backend/` directory so exclusion patterns apply.
