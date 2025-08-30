# Dream-Mind-Lucid: Complete Deployment Guide

## 🌟 Project Overview

Dream-Mind-Lucid is a complete decentralized investment platform built on SKALE Network for dream-mining, cognitive staking, and oracle access. This repository contains all necessary components for deployment and operation.

### 💎 Tokenomics
- **DREAM**: 777,777,777 tokens - Governance and rewards
- **SMIND**: 777,777,777 tokens - Cognitive staking and validation
- **LUCID**: 333,333,333 tokens - Oracle access and Lucid Gates

### 🏗️ Architecture
- **Zero-gas transactions** on SKALE Europa Hub
- **Professional investment features** with yield generation
- **Quantum dream network** via OneiroSphere
- **IPFS integration** for dream storage
- **Automated deployment** via GitHub Actions

## 📁 Repository Structure

```
Dream-mind-lucid/
├── contracts/                   # Smart contracts
│   ├── IEMDreams.sol           # DREAM token with staking & rewards
│   ├── OneiroSphere.sol        # Quantum dream network
│   ├── SMindToken.sol          # SMIND cognitive staking token
│   └── LucidToken.sol          # LUCID oracle access token
├── agents/                      # Python management scripts
│   ├── iem_syndicate.py        # Multi-agent deployment system
│   └── iem_looter.py           # Dedicated event monitoring
├── .github/workflows/          # CI/CD automation
│   └── deploy-verify.yml       # Complete deployment pipeline
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
```bash
# Install Python 3.11+
pip install -r requirements.txt

# Set environment variables
export SKALE_RPC="https://mainnet.skalenodes.com/v1/elated-tan-skat"
export DEPLOYER_KEY="your-private-key"
export SKALE_CHAIN_ID="2046399126"
```

### Deployment
```bash
# Deploy all contracts
python agents/iem_syndicate.py deploy-all

# Check deployment status
python agents/iem_syndicate.py status

# Run security audit
python agents/iem_syndicate.py audit

# Start event monitoring
python agents/iem_looter.py
```

## 💼 Investment Features

### Dream Mining
- Submit dreams to earn DREAM tokens
- AI-powered quality scoring (coherence, novelty, emotion)
- Automatic reward distribution based on dream quality

### Staking & Yield
- Stake DREAM tokens for yield generation
- Configurable reward rates (default: 1% daily)
- Emergency withdrawal functionality

### MindNode Validation
- Stake SMIND tokens to become a validator
- Earn rewards for validating dream quality
- Accuracy tracking and reputation system

### Lucid Gates
- Pay LUCID tokens to access prediction oracles
- Tiered access based on dream quality scores
- Oracle credits system for regular users

## 🔧 Management Commands

### Deployment Agent
```bash
# Deploy specific contract
python agents/iem_syndicate.py deploy-single --contract IEMDreams

# Full ecosystem deployment
python agents/iem_syndicate.py deploy-all
```

### Auditor Agent
```bash
# Security audit all contracts
python agents/iem_syndicate.py audit
```

### Oracle Agent
```bash
# Update network state
python agents/iem_syndicate.py oracle
```

### OneiroSphere Agent
```bash
# Interface dream with IPFS
python agents/iem_syndicate.py oneirosphere --dream "Your dream text"

# Test IPFS connectivity
python agents/iem_syndicate.py ipfs-test
```

### Event Monitoring
```bash
# Start dedicated event monitor
python agents/iem_looter.py
```

## 🤖 GitHub Actions Deployment

The repository includes a complete CI/CD pipeline:

### Environments
- **Staging**: Automatic deployment on `develop` branch
- **Production**: Automatic deployment on `main` branch

### Required Secrets
```bash
DEPLOYER_KEY=your-private-key-here
```

### Workflow Features
- ✅ Code validation and linting
- ✅ Security auditing
- ✅ Contract compilation testing
- ✅ Automated deployment
- ✅ Post-deployment verification
- ✅ Monitoring activation

## 🔐 Security Features

### Smart Contract Security
- Owner-only functions for critical operations
- Emergency withdrawal mechanisms
- Reentrancy protection
- Input validation and bounds checking

### Operational Security
- Source code hashing for integrity verification
- On-chain bytecode verification
- Comprehensive event logging
- Real-time monitoring and alerting

## 📊 Investment Metrics

### Platform Metrics
- Total Value Locked (TVL) in staking
- Dream submission rates
- Validator participation
- Oracle usage statistics

### Token Metrics
- Circulating supply tracking
- Yield distribution rates
- Staking ratios
- Reward claim frequency

## 🌐 Network Information

- **Network**: SKALE Europa Hub
- **Chain ID**: 2046399126
- **RPC Endpoint**: https://mainnet.skalenodes.com/v1/elated-tan-skat
- **Explorer**: https://elated-tan-skale.explorer.mainnet.skalenodes.com
- **Gas Cost**: Zero (SKALE feature)

## 🔮 Future Roadmap

### Phase 1 (Current) - Foundation
- ✅ Complete token ecosystem
- ✅ Dream recording and validation
- ✅ Basic staking and rewards
- ✅ Automated deployment

### Phase 2 - Enhancement
- 🔄 Advanced AI dream scoring
- 🔄 Cross-chain token bridges
- 🔄 NFT dream collections
- 🔄 Governance voting system

### Phase 3 - The Oneiro-Sphere
- 🌌 Quantum consciousness interfaces
- 🌌 Parallel reality exploration
- 🌌 Neural network integrations
- 🌌 Post-scarcity economy features

## 📞 Support & Contact

For deployment support, investment inquiries, or technical assistance:

1. **GitHub Issues**: Open an issue in this repository
2. **Deployment Logs**: Check GitHub Actions workflows
3. **Network Status**: Monitor via `iem_looter.py`
4. **Contract Verification**: Use SKALE Explorer

## ⚖️ License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Powered by SKALE Network | Built for the Future of Investment**

*Dream-Mind-Lucid: Where dreams become digital assets and consciousness drives value.*