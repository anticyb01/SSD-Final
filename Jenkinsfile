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

          if (!(Test-Path $pythonExe)) {
            py -m venv $venvPath
          }

          # Use python -m pip (more reliable than calling pip.exe directly)
          & $pythonExe -m pip install --no-input --upgrade pip
          & $pythonExe -m pip install --no-input -r (Join-Path $env:DEPLOY_DIR "requirements.txt")

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
          # Prevent Jenkins from killing the deployed process after the step ends
          # (Jenkins process tree killer targets processes with the build cookie)
          $oldCookie = $env:JENKINS_NODE_COOKIE
          $env:JENKINS_NODE_COOKIE = "dontKillMe"

          $stdoutLog = Join-Path $env:DEPLOY_DIR "app.stdout.log"
          $stderrLog = Join-Path $env:DEPLOY_DIR "app.stderr.log"

          $startInfo = @{
            FilePath = $pythonExe
            ArgumentList = @("app.py")
            WorkingDirectory = $env:DEPLOY_DIR
            WindowStyle = "Hidden"
            PassThru = $true
            RedirectStandardOutput = $stdoutLog
            RedirectStandardError = $stderrLog
          }
          $p = Start-Process @startInfo

          # Restore cookie for the rest of the build
          $env:JENKINS_NODE_COOKIE = $oldCookie

          Set-Content -Path $pidFile -Value $p.Id
          Write-Host ("Started Flask app pid={0} on port {1}" -f $p.Id, $env:APP_PORT)

          # Health check: fail the build if the app is not actually listening
          $url = "http://localhost:$env:APP_PORT/health"
          $ok = $false
          for ($i = 0; $i -lt 20; $i++) {
            try {
              $r = Invoke-RestMethod -Uri $url -TimeoutSec 2
              if ($r.status -eq "healthy") { $ok = $true; break }
            } catch {
              Start-Sleep -Seconds 1
            }
          }

          if (-not $ok) {
            Write-Host "Health check failed: $url"
            if (Test-Path $stdoutLog) { Write-Host "---- stdout (tail) ----"; Get-Content $stdoutLog -Tail 200 }
            if (Test-Path $stderrLog) { Write-Host "---- stderr (tail) ----"; Get-Content $stderrLog -Tail 200 }
            throw "App did not become healthy on port $env:APP_PORT"
          }
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

