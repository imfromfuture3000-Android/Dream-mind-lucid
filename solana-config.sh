# Solana Dream-Mind-Lucid Configuration
# Environment variables for Solana deployment

# Helius RPC Configuration
export HELIUS_RPC="https://mainnet.helius-rpc.com/?api-key=16b9324a-5b8c-47b9-9b02-6efa868958e5"
export HELIUS_WS="wss://mainnet.helius-rpc.com/?api-key=16b9324a-5b8c-47b9-9b02-6efa868958e5"
export HELIUS_API_KEY="16b9324a-5b8c-47b9-9b02-6efa868958e5"

# Treasury Configuration
export TREASURY_ADDRESS="4eJZVbbsiLAG6EkWvgEYEWKEpdhJPFBYMeJ6DBX98w6a"

# Deployment Configuration (set your own private key)
# export DEPLOYER_KEY="your-base58-encoded-private-key-here"
export SYNDICATE_SIMULATE="1"  # Set to "0" for real deployment

# Token Supply Configuration
export DREAM_SUPPLY="777777777"
export SMIND_SUPPLY="777777777" 
export LUCID_SUPPLY="333333333"

# Network Configuration
export SOLANA_CLUSTER="mainnet-beta"

# MEV Protection Configuration
export MEV_PROTECTION_ENABLED="true"
export MIN_SOL_REBATE="1000000"  # 0.001 SOL minimum rebate

echo "✅ Solana configuration loaded"
echo "🌐 RPC: $HELIUS_RPC"
echo "🏛️ Treasury: $TREASURY_ADDRESS"
echo "🛡️ MEV Protection: $MEV_PROTECTION_ENABLED"