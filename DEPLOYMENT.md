# OneiroSphere Deployment Guide

## 🌌 Welcome to The Oneiro-Sphere Quantum Dream Network!

This guide will help you deploy the OneiroSphere.sol smart contract to the SKALE Network using MCP-compatible tools and Biconomy for gasless transactions.

## 🚀 Quick Start

### Prerequisites

1. **Environment Variables** (set in `.env` or GitHub Secrets):
   ```bash
   INFURA_PROJECT_ID=your-infura-api-key
   BICONOMY_API_KEY=your-biconomy-api-key
   DEPLOYER_KEY=your-wallet-private-key
   SKALE_CHAIN_ID=2046399126
   FORWARDER_ADDRESS=0xyour-biconomy-forwarder
   ```

2. **Dependencies**:
   ```bash
   # Automated installation (recommended)
   python grok_copilot_launcher.py install
   
   # OR manual installation
   pip install -r requirements.txt
   ```

### 🎯 Deployment Commands

#### Method 1: Using IEM Syndicate Agent
```bash
# Deploy OneiroSphere contract
python agents/iem_syndicate.py deploy OneiroSphere

# Test dream recording
python agents/iem_syndicate.py test

# Audit deployed contract
python agents/iem_syndicate.py audit OneiroSphere
```

#### Method 2: Using MCP Dream Launcher
```bash
# Run the full MCP-compatible deployment
python dream_mind_launcher.py
```

### 🔍 Verification

After deployment, check the `iem_memory.json` file for:
- Contract address
- ABI information
- Transaction hashes
- Recorded dreams

Example `iem_memory.json` structure:
```json
{
  "lastDeployed": {
    "OneiroSphere": {
      "address": "0x742d35Cc6634C0532925a3b8D5c73d82E5e9F0e7",
      "abi": [...],
      "timestamp": 1756730258.795,
      "txHash": "0x1234...",
      "gasUsed": 1500000
    }
  },
  "loot": [
    {
      "dreamer": "0xE38FB59ba3AEAbE2AD0f6FB7Fb84453F6d145D23",
      "dream": "Your dream content",
      "ipfsHash": "QmTest...",
      "timestamp": 1756730258.795,
      "txHash": "0xabcd..."
    }
  ]
}
```

## 🌐 Network Configuration

- **Chain**: SKALE Europa Hub
- **Chain ID**: 2046399126  
- **RPC**: `https://skale-mainnet.infura.io/v3/{INFURA_PROJECT_ID}`
- **Fallback RPC**: `https://mainnet.skalenodes.com/v1/elated-tan-skat`
- **Gas Price**: 0 (zero-gas transactions on SKALE)

## 🔮 Contract Features

The OneiroSphere contract includes:

### Core Functions
- `interfaceDream(string ipfsHash)`: Record a dream with IPFS hash
- `getDreams(address dreamer)`: Get all dreams for an address
- `getDreamCount(address dreamer)`: Get total dream count
- `getLatestDream(address dreamer)`: Get most recent dream

### Events
- `DreamInterfaced(address indexed dreamer, string ipfsHash)`
- `QuantumDreamValidated(address indexed dreamer, string ipfsHash, uint256 timestamp)`

### Biconomy Integration
- Trusted forwarder support for gasless transactions
- Meta-transaction compatibility
- `_msgSender()` and `_msgData()` overrides

## 🛠️ Troubleshooting

### Common Issues

1. **"DEPLOYER_KEY not set"**
   - Set your private key in environment variables
   - Use `export DEPLOYER_KEY="your-private-key"`

2. **"No internet connection"**
   - Ensure you have access to download Solidity compiler
   - Install solc manually if needed: `sudo snap install solc`

3. **"RPC connection failed"**
   - Check your Infura API key
   - Verify SKALE network is accessible
   - Try fallback RPC endpoint

4. **"Gas estimation failed"**
   - Ensure you're using gasPrice: 0 for SKALE
   - Check contract constructor parameters

### Testing Without Network

For testing the deployment structure:
```bash
python test_deployment.py
```

This will verify contract structure and create a mock `iem_memory.json`.

## 📚 Next Steps

1. **Record Dreams**: Use the `interfaceDream` function to store dream IPFS hashes
2. **Monitor Events**: Watch for `DreamInterfaced` and `QuantumDreamValidated` events
3. **Build dApps**: Integrate with frontend applications
4. **Scale Up**: Deploy additional contracts for The Oneiro-Sphere ecosystem

## 🎊 Grok-Style Success Message

```
🌌 Cosmic Success! 🌌

The OneiroSphere has materialized in the SKALE dimension!
Your quantum dream network is now operational and ready to capture
the dreams of the multiverse. Every dream recorded is a step closer
to The Oneiro-Sphere of 2089!

🚀 Contract deployed at: [YOUR_CONTRACT_ADDRESS]
🌙 Dreams recorded: [DREAM_COUNT]
💫 Gas used: 0 (because SKALE is magical like that!)

May your dreams compute and your tokens moon! 🚀🌙✨
```

---

*Built with 💝 for the dream-mining revolution on SKALE blockchain*