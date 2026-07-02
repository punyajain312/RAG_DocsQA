#!/usr/bin/env bash
# One-command setup and start for DocQA.
# Run this script: bash start.sh

set -e

echo ""
echo "╔══════════════════════════════════════════╗"
echo "║         DocQA — Ask Your Documents       ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# ── Step 1: Check Docker ────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
  echo "❌  Docker is not installed."
  echo ""
  echo "    Please install Docker Desktop first:"
  echo "    https://www.docker.com/products/docker-desktop/"
  echo ""
  echo "    After installing, come back and run this script again."
  exit 1
fi

if ! docker info &>/dev/null; then
  echo "❌  Docker is installed but not running."
  echo "    Please open the Docker Desktop app, wait for it to start, then run this script again."
  exit 1
fi

echo "✅  Docker is running"
echo ""

# ── Step 2: Set up .env ─────────────────────────────────────────────────────────
if [ ! -f ".env" ]; then
  echo "🔧  First-time setup — let's configure your AI provider."
  echo ""
  echo "    You have two options:"
  echo ""
  echo "    1. Anthropic Claude (best quality, requires free API key)"
  echo "       Get a key at: https://console.anthropic.com/"
  echo ""
  echo "    2. Ollama (free, runs locally, requires Ollama installed)"
  echo "       Download at: https://ollama.ai/"
  echo ""

  cp .env.example .env

  read -rp "    Enter your Anthropic API key, or press Enter to use Ollama: " api_key

  if [ -n "$api_key" ]; then
    # macOS vs Linux sed
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' "s|your-api-key-here|$api_key|" .env
    else
      sed -i "s|your-api-key-here|$api_key|" .env
    fi
    echo ""
    echo "    ✅  API key saved. Using Anthropic Claude."
  else
    if [[ "$OSTYPE" == "darwin"* ]]; then
      sed -i '' 's|LLM_PROVIDER=anthropic|LLM_PROVIDER=ollama|' .env
    else
      sed -i 's|LLM_PROVIDER=anthropic|LLM_PROVIDER=ollama|' .env
    fi
    echo ""
    echo "    ✅  Configured for Ollama (local AI)."
    echo "    ⚠️  Make sure Ollama is installed and 'llama3.2' is pulled:"
    echo "        ollama pull llama3.2"
  fi
  echo ""
else
  echo "✅  Configuration file (.env) already exists"
  echo ""
fi

# ── Step 3: Start services ──────────────────────────────────────────────────────
echo "🚀  Starting DocQA (this may take a few minutes the first time)..."
echo "    (Downloading AI models on first run — please wait)"
echo ""

docker compose up -d --build

echo ""
echo "⏳  Waiting for services to be ready..."

# Poll until the UI is available
max_wait=180
elapsed=0
while ! curl -sf http://localhost:8501/_stcore/health &>/dev/null; do
  if [ "$elapsed" -ge "$max_wait" ]; then
    echo ""
    echo "⚠️  Services are taking longer than expected to start."
    echo "    Check logs with: docker compose logs"
    break
  fi
  sleep 3
  elapsed=$((elapsed + 3))
  printf "."
done

echo ""
echo ""
echo "╔══════════════════════════════════════════╗"
echo "║                                          ║"
echo "║   ✅  DocQA is ready!                    ║"
echo "║                                          ║"
echo "║   Open your browser and go to:           ║"
echo "║   👉  http://localhost:8501              ║"
echo "║                                          ║"
echo "║   To stop: docker compose down           ║"
echo "║                                          ║"
echo "╚══════════════════════════════════════════╝"
echo ""

# Try to open the browser automatically
if command -v open &>/dev/null; then
  open http://localhost:8501
elif command -v xdg-open &>/dev/null; then
  xdg-open http://localhost:8501
fi
