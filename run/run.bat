@echo off
start cmd /c "docker run -p 8000:8000 gumit/ieapi"
start cmd /c "docker run gumit/ieprocessor"
