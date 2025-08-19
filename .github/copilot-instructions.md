# Copilot Instructions for Flask-React TODO App

## Project Architecture
- **Monorepo structure**: `frontend/` (React/TypeScript) and `backend/` (Flask/Python) are separate, each with its own README and build/test workflows.
- **Backend**: Flask app in `backend/application.py`, organized with MVC pattern. Models in `backend/flaskr/models/`, routes in `backend/flaskr/routes/`, controllers in `backend/flaskr/controllers/`, schemas in `backend/flaskr/schemas/`. Uses SQLAlchemy ORM, Flask-Migrate for migrations, JWT for auth, and Flask-Smorest for REST API and schema validation.
- **Frontend**: React app in `frontend/`, using TypeScript, TailwindCSS, Zustand, React Query, ShadcnUI, and React Router. API calls are made via Axios to the backend REST endpoints.
- **Database**: SQLite file at `backend/data.db`. Migrations managed via Flask-Migrate (`flask db upgrade`).

## Developer Workflows
- **Backend setup**:
  1. Create and activate Python venv: `python -m venv venv` → `venv\Scripts\activate` (Windows).
  2. Install dependencies: `pip install -r requirements.txt`.
  3. Set `JWT_SECRET_KEY` in `.env`.
  4. Run server: `flask run` (serves at `http://127.0.0.1:5000`).
  5. API docs: `http://localhost:5000/docs` (Swagger UI).
  6. (Optional) Reset DB: delete `data.db`, run `flask db upgrade`, then `python seed.py` to seed initial data.
- **Frontend setup**:
  1. `cd frontend`
  2. `npm install`
  3. `npm run dev` (serves at `http://localhost:5173`)

## Project-Specific Patterns
- **API endpoints**: All routes are versioned under `/api/v1/` (see `backend/flaskr/routes/`).
- **Auth**: JWT-based, issued via `/api/v1/auth/sign-in`.
- **Models**: See `backend/flaskr/models/` for table structure. Use SQLAlchemy conventions.
- **Frontend API integration**: See `frontend/src/services/api/` for Axios setup and API calls. State managed via Zustand (`frontend/src/stores/`).
- **Testing**: Backend tests in `backend/tests/`. Use pytest. Frontend tests in `frontend/src/test/`.
- **Migrations**: Alembic scripts in `backend/migrations/versions/`.

## Integration Points
- **REST API**: Frontend communicates with backend via REST. All endpoints return JSON.
- **Swagger UI**: For API exploration and documentation (`/docs`).
- **Seed data**: Use `backend/seed.py` to populate initial DB values.

## Conventions & Tips
- **File naming**: Use snake_case for Python, kebab-case or PascalCase for React components.
- **Environment variables**: Backend expects `.env` for secrets (esp. JWT key).
- **Cross-component communication**: Frontend state via Zustand; backend via Flask blueprints/controllers.
- **Preview images**: See `preview/` for UI/API screenshots.

## Key Files & Directories
- `backend/application.py`: Flask app entry point
- `backend/flaskr/routes/`: API route definitions
- `backend/flaskr/models/`: SQLAlchemy models
- `frontend/src/`: Main React app source
- `frontend/src/services/api/`: API integration
- `backend/seed.py`: DB seeding script
- `backend/migrations/`: Alembic migration scripts

---
For more details, see the respective `README.md` files in `frontend/` and `backend/`.
