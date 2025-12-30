# SSD-Final (Flask + Jenkins Pipeline)

This repo is a minimal Flask app with:
- unit tests (pytest)
- Jenkins Pipeline (`Jenkinsfile`) to automate: clone → install deps → run tests → deploy (run app locally on the Jenkins machine)

## Run locally (without Docker)

Windows PowerShell:
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pytest -q
py app.py
```

Open:
- `http://localhost:5000/` → `{"status":"ok"}`
- `http://localhost:5000/health` → `{"status":"healthy"}`

## Jenkins note

Jenkins typically runs on `http://localhost:8080`, so this Flask app intentionally uses port `5000` by default.

