# Login Page — GitHub + Azure Deployment Guide

## Project Structure

```
├── login.html       ← Frontend (static login UI)
├── app.py           ← Python/Flask backend (auth API)
├── requirements.txt ← Python dependencies
└── startup.txt      ← Azure App Service startup command
```

---

## How the pieces fit together

| Layer | File | Where it runs |
|-------|------|---------------|
| UI | `login.html` | Any static host (GitHub Pages or served by Flask) |
| API | `app.py` | Azure App Service (Python) |
| HTTPS | — | Azure terminates TLS automatically |

---

## Local Development

```bash
pip install -r requirements.txt
python app.py          # runs on http://localhost:5000
```

Open `http://localhost:5000` — Flask serves `login.html` and handles `/api/login`.

Demo credential: `demo@example.com` / `password123`

---

## GitHub Pages (frontend only)

1. Push `login.html` to a repo (e.g. `gh-pages` branch or `/docs` folder).
2. Enable GitHub Pages in repo Settings → Pages.
3. Update `login.html` fetch URL to point at your Azure API:
   ```js
   const res = await fetch('https://<your-app>.azurewebsites.net/api/login', { ... });
   ```

---

## Azure App Service Deployment

### Option A — Azure CLI

```bash
# 1. Create a resource group + App Service plan
az group create --name rg-login-demo --location eastus
az appservice plan create --name plan-login --resource-group rg-login-demo \
    --sku B1 --is-linux

# 2. Create the web app (Python 3.11)
az webapp create --name <YOUR_APP_NAME> --resource-group rg-login-demo \
    --plan plan-login --runtime "PYTHON:3.11"

# 3. Set the startup command
az webapp config set --name <YOUR_APP_NAME> --resource-group rg-login-demo \
    --startup-file "gunicorn --bind=0.0.0.0:8000 --workers=2 app:app"

# 4. Deploy code
az webapp deploy --name <YOUR_APP_NAME> --resource-group rg-login-demo \
    --src-path . --type zip
```

### Option B — GitHub Actions (CI/CD)

1. In Azure Portal → your App Service → Deployment Center → GitHub.
2. Authorize and select your repo/branch.
3. Azure auto-generates a workflow file in `.github/workflows/`.

HTTPS is enabled automatically on `*.azurewebsites.net`.

---

## Production Checklist

- [ ] Replace the in-memory `USERS` dict with a real database (e.g. Azure Cosmos DB, PostgreSQL).
- [ ] Hash passwords with `bcrypt` — never store plaintext.
- [ ] Issue JWTs or signed sessions on successful login.
- [ ] Set `ALLOWED_ORIGINS` env variable to your actual frontend domain.
- [ ] Remove or change the demo credential in `app.py`.
- [ ] Enable Azure Application Insights for logging.
