# Deployment Guide

## Option A: Docker Compose (single machine / VM)

1. `cp .env.example .env` and fill in `ANTHROPIC_API_KEY` if desired.
2. `docker compose up --build -d`
3. Backend on port 8000, frontend on port 5173 (nginx serving the built SPA).
4. For a production VM, put nginx/Caddy in front for TLS and point it at
   ports 5173 (frontend) and 8000 (API), or bake the API URL into the
   frontend build (`--build-arg VITE_API_URL=https://api.yourdomain.com`).

## Option B: Vercel (frontend) + Render (backend)

### Backend on Render

1. Push the repo to GitHub.
2. On Render: New -> Web Service -> connect the repo, root directory
   `backend/`.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables: `ANTHROPIC_API_KEY`, `LLM_PROVIDER=anthropic`,
   `FRONTEND_URL=https://<your-vercel-app>.vercel.app`, `MAX_UPLOAD_MB=25`.
6. Add a persistent disk (Render Disks) mounted at `/opt/render/project/src/backend/uploads`
   and `/opt/render/project/src/backend/generated` if you need uploads/models
   to survive redeploys (otherwise they reset on each deploy).
7. Deploy; note the resulting URL, e.g. `https://your-api.onrender.com`.

### Frontend on Vercel

1. On Vercel: New Project -> import the repo, root directory `frontend/`.
2. Framework preset: Vite.
3. Build command: `npm run build`; Output directory: `dist`.
4. Environment variable: `VITE_API_URL=https://your-api.onrender.com`.
5. Deploy. Update the backend's `FRONTEND_URL` env var to match the deployed
   Vercel URL so CORS allows it, then redeploy the backend.

## Environment variable summary

| Variable | Where | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | backend | Enables LLM explanations; omit to run without AI |
| `LLM_PROVIDER` | backend | Currently only `anthropic` supported |
| `FRONTEND_URL` | backend | CORS allow-origin |
| `BACKEND_URL` | backend | Informational; not required by code |
| `MAX_UPLOAD_MB` | backend | Upload size limit |
| `VITE_API_URL` | frontend | Base URL the SPA calls |

## Post-deploy checklist

- [ ] `GET /api/health` returns `{"status": "ok"}`
- [ ] CORS allows the deployed frontend origin
- [ ] File upload works end-to-end (small CSV)
- [ ] `.env` / secrets are not committed to git
- [ ] Backend logs do not show unhandled tracebacks reaching clients (500s
      return a generic message; details are server-side only)
