#!/bin/bash
cd /app
export PYTHONPATH=/app:$PYTHONPATH
uvicorn app.main:app --host 0.0.0.0 --port $PORT
