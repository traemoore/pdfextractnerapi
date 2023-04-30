@echo off
set GAR_LOCATION=us-central1
set PROJECT_ID=red-charger-383023
set REPOSITORY=insights-extractor

echo %date% %time% Building ieapi image...
start /wait cmd /c "docker build -t %GAR_LOCATION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY%/ieapi:latest  -f api.dockerfile ." & (
  echo %date% %time% Pushing ieapi image to container registry...
  start /wait cmd /c "docker push us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieapi:latest"
)

echo %date% %time% Building ieworker image...
start /wait cmd /c "docker build -t %GAR_LOCATION%-docker.pkg.dev/%PROJECT_ID%/%REPOSITORY%/ieworker:latest  -f worker.dockerfile ." & (
  echo %date% %time% Pushing ieworker image to container registry...
  start /wait cmd /c "docker push us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieworker:latest"
)


@REM docker build -t us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieapi:latest -f api.dockerfile .
@REM docker build -t us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieworker:latest -f worker.dockerfile .

