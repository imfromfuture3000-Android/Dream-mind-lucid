# Dream-Mind-Lucid Deployment Configuration
# Set these environment variables for deployment

# Required Environment Variables:
export INFURA_PROJECT_ID="your-infura-api-key"
export BICONOMY_API_KEY="your-biconomy-api-key" 
export DEPLOYER_KEY="your-wallet-private-key"
export SKALE_CHAIN_ID="2046399126"
export FORWARDER_ADDRESS="0xyour-biconomy-forwarder"

# Example deployment commands:
# 1. Deploy OneiroSphere contract:
#    python agents/iem_syndicate.py deploy OneiroSphere
#
# 2. Test dream recording:
#    python agents/iem_syndicate.py test
#
# 3. Audit deployed contract:
#    python agents/iem_syndicate.py audit OneiroSphere

# Network Configuration:
# SKALE Europa Hub: Chain ID 2046399126
# RPC Endpoint: https://skale-mainnet.infura.io/v3/{INFURA_PROJECT_ID}
# Zero gas fees - gasPrice: 0