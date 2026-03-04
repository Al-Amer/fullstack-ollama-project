#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

# Create logs folder first
mkdir -p logs

echo "Starting fullstack project..."

# 1) FRONTEND: install and build/start dev server
echo "-> Setting up frontend..."
cd frontend
if [ ! -d node_modules ]; then
  npm install
fi
# start frontend in background (Vite default dev server)
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend started (PID $FRONTEND_PID). Logs: ../logs/frontend.log"
cd "$ROOT"

# 2) NODE BACKEND
echo "-> Setting up Node backend..."
cd backend/backend-node
if [ ! -d node_modules ]; then
  npm install
fi
node server.js > ../logs/backend-node.log 2>&1 &
NODE_PID=$!
echo "Node backend started (PID $NODE_PID). Logs: ../logs/backend-node.log"
cd "$ROOT"

# 3) PYTHON BACKEND
echo "-> Setting up Python backend..."
cd backend/backend-python
if [ ! -d venv ]; then
  python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt
# start FastAPI via uvicorn
uvicorn app:app --host 0.0.0.0 --port 8001 > ../logs/backend-python.log 2>&1 &
PY_PID=$!
deactivate
echo "Python backend started (PID $PY_PID). Logs: ../logs/backend-python.log"
cd "$ROOT"

# Create logs dir if not existing
mkdir -p logs

echo "All processes started. Frontend -> http://localhost:5173 (Vite default)."
echo "Node backend -> http://localhost:8000"
echo "Python backend -> http://localhost:8001"
echo "To stop: kill $FRONTEND_PID $NODE_PID $PY_PID (or use pkill -f uvicorn / node / vite)"

# tail logs (optional): we won't block here; user can tail logs manually
# Save PIDs to file
echo $FRONTEND_PID > logs/frontend.pid
echo $NODE_PID > logs/node.pid
echo $PY_PID > logs/python.pid