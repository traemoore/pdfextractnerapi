@echo off
start cmd /c "docker build -t gumit/ieapi -f api.dockerfile ."
start cmd /c "docker build -t gumit/ieprocessor -f processor.dockerfile ."
