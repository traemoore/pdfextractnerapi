REM Push images to container registry
start cmd /c ""
@REM start cmd /c "docker push us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieworker:latest"

@echo off

REM Log start of script
echo %date% %time% Script started
echo %date% %time% Api Script started >> script.log

REM Push ie-api image to container registry
echo %date% %time% Pushing ie-api image to container registry...
echo %date% %time% Pushing ie-api image to container registry... >> script.log
start cmd /c "docker push us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieapi:latest" && (

  REM Create ie-api deployment in Kubernetes
  echo %date% %time% Creating ie-api deployment in Kubernetes...
  echo %date% %time% Creating ie-api deployment in Kubernetes... >> script.log
  start cmd /c "kubectl create deployment ie-api --image=us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieapi:latest" && (

    REM Scale ie-api deployment
    echo %date% %time% Scaling ie-api deployment...
    echo %date% %time% Scaling ie-api deployment... >> script.log
    start cmd /c "kubectl scale deployment ie-api --replicas=1" && (

      REM Expose ie-api deployment as LoadBalancer service
      echo %date% %time% Exposing ie-api deployment as LoadBalancer service...
      echo %date% %time% Exposing ie-api deployment as LoadBalancer service... >> script.log
      start cmd /c "kubectl expose deployment ie-api --type=LoadBalancer --port=8000 --target-port=8000" && (

        REM Autoscale ie-api deployment
        echo %date% %time% Autoscaling ie-api deployment...
        echo %date% %time% Autoscaling ie-api deployment... >> script.log
        start cmd /c "kubectl autoscale deployment ie-api --cpu-percent=80 --min=1 --max=5"

      )
    )
  )
)


REM Log start of script
echo %date% %time% Worker Script started
echo %date% %time% Script started >> script.log

REM Push ieworker image to container registry
echo %date% %time% Pushing ieworker image to container registry...
echo %date% %time% Pushing ieworker image to container registry... >> script.log
start cmd /c "docker push us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieworker:latest" && (

  REM Create ieworker deployment in Kubernetes
  echo %date% %time% Creating ieworker deployment in Kubernetes...
  echo %date% %time% Creating ieworker deployment in Kubernetes... >> script.log
  start cmd /c "kubectl create deployment ie-worker --image=us-central1-docker.pkg.dev/red-charger-383023/insights-extractor/ieworker:latest" && (

    REM Scale ieworker deployment
    echo %date% %time% Scaling ieworker deployment...
    echo %date% %time% Scaling ieworker deployment... >> script.log
    start cmd /c "kubectl scale deployment ie-worker --replicas=2" && (

      REM Autoscale ieworker deployment
      echo %date% %time% Autoscaling ieworker deployment...
      echo %date% %time% Autoscaling ieworker deployment... >> script.log
      start cmd /c "kubectl autoscale deployment ie-worker --cpu-percent=80 --min=1 --max=5"

    )
  )
)

REM Log end of script
echo %date% %time% Deployment Script completed
echo %date% %time% Deployment Script completed >> script.log


@REM for debugging
@REM kubectl get pods

@REM ---
@REM apiVersion: "v1"
@REM kind: "Service"
@REM metadata:
@REM   name: "ie-api-service"
@REM   namespace: "default"
@REM   labels:
@REM     app: "ie-api"
@REM spec:
@REM   ports:
@REM   - protocol: "TCP"
@REM     port: 8000
@REM   selector:
@REM     app: "ie-api"
@REM   type: "LoadBalancer"
@REM   loadBalancerIP: ""