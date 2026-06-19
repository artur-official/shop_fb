@echo off
echo Starting API Server...
uvicorn api:app --host 0.0.0.0 --port 8000
pause
