#!/usr/bin/env bash
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "Stopping fullstack project..."

if [ -f logs/frontend.pid ]; then
  kill $(cat logs/frontend.pid) 2>/dev/null || true
  rm logs/frontend.pid
  echo "Frontend stopped."
fi

if [ -f logs/node.pid ]; then
  kill $(cat logs/node.pid) 2>/dev/null || true
  rm logs/node.pid
  echo "Node backend stopped."
fi

if [ -f logs/python.pid ]; then
  kill $(cat logs/python.pid) 2>/dev/null || true
  rm logs/python.pid
  echo "Python backend stopped."
fi

echo "All services stopped."
