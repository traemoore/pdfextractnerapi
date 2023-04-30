@echo off
set GAR_LOCATION=us-central1
set PROJECT_ID=red-charger-383023
set REPOSITORY=insights-extractor

start cmd /c "docker build -t %GAR_LOCATION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY%/ieapi:latest  -f api.dockerfile ."
start cmd /c "docker build -t %GAR_LOCATION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY%/ieworker:latest  -f worker.dockerfile ."

@REM docker build -t us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieapi:latest -f worker.dockerfile ."
@REM docker build -t us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieworker:latest -f worker.dockerfile ."

