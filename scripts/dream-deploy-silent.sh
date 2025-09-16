#!/bin/bash
# 🌌 dream-deploy-silent.sh
# Autonomous Deployment: Dream-mind-lucid on SKALE (ABBA Consensus)
# Mode: No Questions. No Interruptions. No Copilot.
# GitHub Gene AI — 2040-Compliant

set -euo pipefail  # Strict mode: fail fast, no input, no mercy

export DEBIAN_FRONTEND=noninteractive
export PYTHONUNBUFFERED=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

# >>>>>>>>>>>>>>>>>>>>>>>>>>
# CONFIGURATION (Silent Mode)
# <<<<<<<<<<<<<<<<<<<<<<<<<<

PROJECT_DIR="$(mktemp -d -p /tmp dream-silence.XXXXXX)"
LOG_FILE="$PROJECT_DIR/deploy.log"
RPC_URL="http://127.0.0.1:1234"
CHAIN_ID="54173"
DEPLOYER_KEY="0x16db936de7342b075849d74a66460007772fab88cf4ab509a3487f23398823d6"
SDK_DIR="$PROJECT_DIR/skale-sdk"
DREAM_DIR="$PROJECT_DIR/dream"
CONSENSUS_DIR="$PROJECT_DIR/skale-consensus"
MEMORY_FILE="$DREAM_DIR/iem_memory.json"

mkdir -p "$PROJECT_DIR/logs"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "🌌 INITIATING SILENT DEPLOYMENT: DREAM-MIND-LUCID ON SKALE"
echo "📍 Workspace: $PROJECT_DIR"
echo "🔒 Autonomous Mode: Active — No Input Accepted"

# >>>>>>>>>>>>>>>>>>>>>>>>>>
# STEP 1: DEPENDENCIES
# <<<<<<<<<<<<<<<<<<<<<<<<<<

echo "📦 Installing dependencies silently..."

if ! command -v git &> /dev/null; then
  sudo apt-get update > /dev/null && sudo apt-get install -y git jq python3 python3-pip docker.io > /dev/null
fi

if ! command -v docker &> /dev/null; then
  echo "❌ Docker not available" && exit 1
fi

# Ensure Docker is running
sudo systemctl is-active docker || sudo systemctl start docker > /dev/null 2>&1 || true

# >>>>>>>>>>>>>>>>>>>>>>>>>>
# STEP 2: CLONE REPOS
# <<<<<<<<<<<<<<<<<<<<<<<<<<

echo "🔁 Cloning repositories..."

git clone --quiet https://github.com/skalenetwork/skale-consensus.git "$CONSENSUS_DIR" &
git clone --quiet https://github.com/skalenetwork/skale-sdk.git "$SDK_DIR" &
git clone --quiet https://github.com/imfromfuture3000-Android/Dream-mind-lucid.git "$DREAM_DIR" &

wait

# >>>>>>>>>>>>>>>>>>>>>>>>>>
# STEP 3: LAUNCH LOCAL SKALE CHAIN
# <<<<<<<<<<<<<<<<<<<<<<<<<<

echo "🚀 Launching local SKALE chain (ABBA Consensus)..."
cd "$SDK_DIR"

# Run in background, no output unless error
./run.sh > "$PROJECT_DIR/logs/skale.log" 2>&1 &

# Wait for RPC to be live
echo "⏳ Waiting for RPC at $RPC_URL..."
for i in {1..30}; do
  if curl -s --head --fail "$RPC_URL" >/dev/null 2>&1; then
    echo "✅ Chain is live"
    break
  fi
  sleep 2
done

if ! curl -s --head --fail "$RPC_URL" >/dev/null 2>&1; then
  echo "❌ RPC not available after 60s" >&2
  exit 1
fi

# >>>>>>>>>>>>>>>>>>>>>>>>>>
# STEP 4: PREPARE DREAM ENV
# <<<<<<<<<<<<<<<<<<<<<<<<<<

cd "$DREAM_DIR"

echo "🧠 Preparing Dream-mind-lucid environment..."

# Install Python deps silently
if [ -f "requirements.txt" ]; then
  pip install -r requirements.txt --quiet > /dev/null 2>&1 || true
fi

# Set env vars
export SKALE_RPC="$RPC_URL"
export SKALE_CHAIN_ID="$CHAIN_ID"
export DEPLOYER_KEY="$DEPLOYER_KEY"
export WEB3_PROVIDER_URI="$RPC_URL"
export GAS_PRICE="0"
export GAS_LIMIT="20000000"

# Patch config if needed (free gas)
if [ -f "config.json.in" ]; then
  sed -i 's/"gas_price".*/"gas_price": "0",/' config.json.in || true
fi

# >>>>>>>>>>>>>>>>>>>>>>>>>>
# STEP 5: DEPLOY CONTRACT
# <<<<<<<<<<<<<<<<<<<<<<<<<<

echo "⚡ Deploying IEMDreams.sol to SKALE Chain ID: $CHAIN_ID"

# Run deployment — assumes iem_syndicate.py has a 'deploy' silent mode
python3 agents/iem_syndicate.py deploy > /dev/null 2>&1 || {
  echo "❌ Deployment script failed" >&2
  echo "📋 Check logs: $LOG_FILE"
  exit 1
}

# >>>>>>>>>>>>>>>>>>>>>>>>>>
# STEP 6: AUDIT & REPORT
# <<<<<<<<<<<<<<<<<<<<<<<<<<

if [ -f "$MEMORY_FILE" ]; then
  CONTRACT_ADDRESS=$(jq -r '.contract_address // empty' "$MEMORY_FILE" 2>/dev/null)
  TX_HASH=$(jq -r '.tx_hash // empty' "$MEMORY_FILE" 2>/dev/null)

  if [[ -n "$CONTRACT_ADDRESS" && "$CONTRACT_ADDRESS" != "null" ]] && \
     [[ -n "$TX_HASH" && "$TX_HASH" != "null" ]]; then

    echo "✅ DEPLOYMENT COMPLETE"
    echo "🔗 Contract: $CONTRACT_ADDRESS"
    echo "🔖 Tx Hash: $TX_HASH"
    echo "🌐 RPC: $RPC_URL"
    echo "🆔 Chain ID: $CHAIN_ID"
    echo "💤 Autonomous task finished. No further action."

    # Optional: Print minimal output for parsing
    echo "{\"status\":\"success\",\"contract\":\"$CONTRACT_ADDRESS\",\"tx\":\"$TX_HASH\"}"

    # Exit cleanly
    exit 0
  else
    echo "❌ Deployment succeeded but memory file incomplete" >&2
    exit 1
  fi
else
  echo "❌ Deployment failed: iem_memory.json not found" >&2
  exit 1
fi

# >>>>>>>>>>>>>>>>>>>>>>>>>>
# STEP 7: POST-DEPLOY (Optional Background Agents)
# <<<<<<<<<<<<<<<<<<<<<<<<<<

# Uncomment to run looter in background
# python3 agents/iem_looter.py listen &

# Cleanup on exit
trap 'kill $(jobs -p) 2>/dev/null || true; exit' SIGINT SIGTERM EXIT

# End of script
