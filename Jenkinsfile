pipeline {
  agent any

  options {
    timestamps()
  }

  environment {
    // Flask app port (do NOT use 8080 because Jenkins is already on 8080)
    APP_PORT = "5000"
    // Where Jenkins will keep the running app venv + pid file on the Jenkins machine
    DEPLOY_DIR = "${WORKSPACE}\\_deploy"
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Unit tests (pytest)') {
      steps {
        // Windows-friendly: use the Python Launcher (py) which is commonly installed
        bat '''
          py -m venv .venv
          call .venv\\Scripts\\activate
          pip install -r requirements.txt -r requirements-dev.txt
          set PYTHONPATH=%CD%
          pytest -q
        '''
      }
    }

    stage('Deploy (run locally on Jenkins machine)') {
      steps {
        powershell '''
          $ErrorActionPreference = "Stop"

          New-Item -ItemType Directory -Force -Path "$env:DEPLOY_DIR" | Out-Null

          # Copy app + requirements into a stable deploy folder so it can run outside the Jenkins build workspace
          Copy-Item -Force "$env:WORKSPACE\\app.py" "$env:DEPLOY_DIR\\app.py"
          Copy-Item -Force "$env:WORKSPACE\\requirements.txt" "$env:DEPLOY_DIR\\requirements.txt"

          $venvPath = Join-Path $env:DEPLOY_DIR "venv"
          $pythonExe = Join-Path $venvPath "Scripts\\python.exe"
          $pipExe = Join-Path $venvPath "Scripts\\pip.exe"

          if (!(Test-Path $pythonExe)) {
            py -m venv $venvPath
          }

          & $pipExe install --no-input --upgrade pip
          & $pipExe install --no-input -r (Join-Path $env:DEPLOY_DIR "requirements.txt")

          # Stop previous process (if any)
          $pidFile = Join-Path $env:DEPLOY_DIR "app.pid"
          if (Test-Path $pidFile) {
            $oldPid = Get-Content $pidFile -ErrorAction SilentlyContinue
            if ($oldPid) {
              try {
                Stop-Process -Id ([int]$oldPid) -Force -ErrorAction Stop
              } catch {
                # ignore if already stopped
              }
            }
            Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
          }

          # Start app in background (so Jenkins job can finish while app keeps running)
          $env:APP_PORT = "$env:APP_PORT"
          $startInfo = @{
            FilePath = $pythonExe
            ArgumentList = @("app.py")
            WorkingDirectory = $env:DEPLOY_DIR
            WindowStyle = "Hidden"
            PassThru = $true
          }
          $p = Start-Process @startInfo

          Set-Content -Path $pidFile -Value $p.Id
          Write-Host ("Started Flask app pid={0} on port {1}" -f $p.Id, $env:APP_PORT)
        '''
      }
    }
  }

  post {
    always {
      echo "Pipeline finished."
    }
  }
}

