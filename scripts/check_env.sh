#!/usr/bin/env bash
set -e

echo "Checking environment..."

# Node
if command -v node >/dev/null 2>&1; then
  echo "node: $(node -v)"
else
  echo "node: NOT FOUND"
fi

# npm
if command -v npm >/dev/null 2>&1; then
  echo "npm: $(npm -v)"
else
  echo "npm: NOT FOUND"
fi

# Python
if command -v python3 >/dev/null 2>&1; then
  echo "python3: $(python3 --version)"
else
  echo "python3: NOT FOUND"
fi

# pip
if command -v pip3 >/dev/null 2>&1; then
  echo "pip3: $(pip3 --version)"
else
  echo "pip3: NOT FOUND"
fi

# check ollama binary
if command -v ollama >/dev/null 2>&1; then
  echo "ollama binary found: $(ollama version 2>/dev/null || echo 'version unknown')"
else
  echo "ollama binary: not found in PATH"
fi

# quick test whether local Ollama HTTP responds (best-effort)
echo "Testing local Ollama HTTP endpoint at http://localhost:11434..."
if command -v curl >/dev/null 2>&1; then
  set +e
  http_code=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:11434/)
  set -e
  if [ "$http_code" = "200" ] || [ "$http_code" = "400" ] || [ "$http_code" = "404" ]; then
    echo "Ollama HTTP responded with status $http_code (OK - local HTTP reachable)."
  else
    echo "Ollama HTTP endpoint did not respond or returned status $http_code. If Ollama is local, check it's running."
  fi
else
  echo "curl not found — cannot test local Ollama HTTP endpoint."
fi

echo "Environment check complete."
