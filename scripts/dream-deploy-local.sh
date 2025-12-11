#!/bin/bash
# dream-deploy-local.sh - Local deployment without Docker dependency
set -euo pipefail

# Load .env if exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Default values
RPC_URL=${SKALE_RPC:-"http://127.0.0.1:8545"}
CHAIN_ID=${SKALE_CHAIN_ID:-"54173"}
GAS_PRICE=${GAS_PRICE:-"0"}
GAS_LIMIT=${GAS_LIMIT:-"20000000"}

echo "🌌 DREAM-MIND-LUCID LOCAL DEPLOYMENT"
echo "📍 RPC URL: $RPC_URL"
echo "🆔 Chain ID: $CHAIN_ID"

# Install dependencies
echo "📦 Installing dependencies..."
npm install --silent || true
pip install -r requirements.txt --quiet || true

# Deploy EVM contracts first
echo "⚡ Deploying EVM contracts..."
cd evm
npx hardhat run scripts/deploy.js --network local || {
    echo "❌ EVM deployment failed"
    exit 1
}

# Deploy Dream contract
echo "🧠 Deploying Dream contract..."
cd ..
python agents/iem_syndicate.py deploy || {
    echo "❌ Dream contract deployment failed"
    exit 1
}

# Start the event listener
echo "👂 Starting event listener..."
python agents/iem_looter.py listen &
LISTENER_PID=$!

# Cleanup on exit
trap 'kill $LISTENER_PID 2>/dev/null || true; exit' SIGINT SIGTERM EXIT

echo "✅ Deployment complete! Listening for events..."
wait $LISTENER_PID
