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

## Jenkins pipeline stages (brief)

The `Jenkinsfile` runs these stages:

- **Checkout**: pulls the latest code from the GitHub repo into the Jenkins workspace.
- **Unit tests (pytest)**:
  - creates a Python virtual environment in the workspace (`.venv`)
  - installs app + dev dependencies
  - runs `pytest` to validate the app (build fails if tests fail)
- **Deploy (run locally on Jenkins machine)**:
  - copies `app.py` + `requirements.txt` into a stable folder: `WORKSPACE\\_deploy`
  - creates/updates a separate virtual environment under `_deploy\\venv`
  - stops the previously deployed Flask process (via `_deploy\\app.pid`) if it exists
  - starts Flask in the background and writes logs:
    - `_deploy\\app.stdout.log`
    - `_deploy\\app.stderr.log`
  - runs a health check against `http://localhost:5000/health` and fails the build if the app is not reachable

