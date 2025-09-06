#!/bin/bash

# AI-Generated Script for Forking and Adapting Dream-mind-lucid to SKALE Consensus

# Step 1: Clone repositories
git clone https://github.com/skalenetwork/skale-consensus.git dream-consensus-fork
cd dream-consensus-fork
git clone https://github.com/skalenetwork/skale-sdk.git sdk
git clone https://github.com/imfromfuture3000-Android/Dream-mind-lucid.git dream

# Step 2: Build the consensus (for reference, as SDK uses pre-built skaled)
cd sdk
./run.sh &  # Start local SKALE chain in background (HTTP: http://127.0.0.1:1234, WS: ws://127.0.0.1:1233, Chain ID: 54173)
sleep 10  # Wait for chain to start

# Step 3: Adapt Dream deployment to local SKALE chain
cd ../dream
# Install dependencies
pip install -r requirements.txt

# Set environment variables for local chain
export SKALE_RPC=http://127.0.0.1:1234
export SKALE_CHAIN_ID=54173
export DEPLOYER_KEY=0x16db936de7342b075849d74a66460007772fab88cf4ab509a3487f23398823d6  # Use test private key from SDK

# Modify config if needed for free deployment (edit config.json.in in SDK if required)

# Step 4: Deploy the contract
python agents/iem_syndicate.py deploy

# Step 5: Audit and report
python agents/iem_syndicate.py audit

# Extract and report contract address and tx hash
if [ -f "iem_memory.json" ]; then
  CONTRACT_ADDRESS=$(jq -r '.contract_address' iem_memory.json)
  TX_HASH=$(jq -r '.tx_hash' iem_memory.json)
  echo "Deployment Complete!"
  echo "Contract Address: $CONTRACT_ADDRESS"
  echo "Transaction Hash: $TX_HASH"
else
  echo "Deployment failed. Check logs."
fi

# Step 6: Run event monitoring
python agents/iem_looter.py &

# Cleanup on exit (optional)
trap "kill 0" EXIT
