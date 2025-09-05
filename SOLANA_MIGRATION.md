# Solana Migration Guide

## 🚀 Dream-Mind-Lucid Solana Deployment

This repository has been enhanced to support **Solana blockchain** with SPL Token 2022 standards and MEV protection, while maintaining backward compatibility with the original SKALE implementation.

### 🌟 New Solana Features

- **SPL Token 2022**: Enhanced token standards for DREAM, SMIND, and LUCID tokens
- **MEV Protection**: Automatic SOL rebates via post-trade backruns
- **Helius RPC**: High-performance Solana RPC with WebSocket support
- **Zero-Risk Arbitrage**: Built-in protection against toxic MEV
- **Treasury Integration**: Unified treasury at `4eJZVbbsiLAG6EkWvgEYEWKEpdhJPFBYMeJ6DBX98w6a`

### 🛠️ Quick Start (Solana)

1. **Install Dependencies**:
   ```bash
   pip install solana anchorpy spl-token aiohttp base58
   ```

2. **Configure Environment**:
   ```bash
   source solana-config.sh
   export DEPLOYER_KEY="your-base58-private-key"  # Optional for real deployment
   ```

3. **Deploy to Solana**:
   ```bash
   python agents/solana_dream_syndicate.py deploy
   ```

4. **Test Dream Recording**:
   ```bash
   python agents/solana_dream_syndicate.py test-dream
   ```

5. **Test MEV Protection**:
   ```bash
   python agents/solana_dream_syndicate.py test-mev
   ```

### 🌐 Network Configuration

- **RPC**: `https://mainnet.helius-rpc.com/?api-key=16b9324a-5b8c-47b9-9b02-6efa868958e5`
- **WebSocket**: `wss://mainnet.helius-rpc.com/?api-key=16b9324a-5b8c-47b9-9b02-6efa868958e5`
- **Treasury**: `4eJZVbbsiLAG6EkWvgEYEWKEpdhJPFBYMeJ6DBX98w6a`
- **API Key**: `16b9324a-5b8c-47b9-9b02-6efa868958e5`

### 💰 Token Economics (Solana)

| Token | Supply | Purpose | Standard |
|-------|--------|---------|----------|
| DREAM | 777,777,777 | Dream validation rewards | SPL Token 2022 |
| SMIND | 777,777,777 | Cognitive staking | SPL Token 2022 |
| LUCID | 333,333,333 | Oracle access | SPL Token 2022 |

### 🛡️ MEV Protection

The Solana implementation includes built-in MEV protection:

- **Backrun Detection**: Automatic detection of profitable backrun opportunities
- **SOL Rebates**: Users receive 1% of backrun profits (minimum 0.001 SOL)
- **Zero Risk**: No exposure to toxic MEV or front-running
- **Treasury Funded**: Rebates paid from program treasury

### 📁 Program Structure

```
programs/dream-mind-lucid/
├── src/
│   └── lib.rs          # Main Solana program
├── Cargo.toml          # Rust dependencies
└── ...

agents/
├── solana_dream_syndicate.py  # Solana deployment agent
├── iem_syndicate.py          # Legacy SKALE agent
└── ...

.github/workflows/
├── deploy-solana.yml    # Solana CI/CD
├── deploy-oneirosphere.yml  # Legacy SKALE
└── ...
```

### 🔄 Migration Path

The repository supports both networks during the transition:

1. **Phase 1**: Solana deployment with simulation mode
2. **Phase 2**: Real Solana deployment with limited functionality
3. **Phase 3**: Full Solana migration with enhanced features
4. **Phase 4**: SKALE deprecation (optional)

### 🧪 Testing

Run the test suite for both networks:

```bash
# Test Solana implementation
python agents/solana_dream_syndicate.py test-dream
python agents/solana_dream_syndicate.py test-mev

# Test legacy SKALE implementation
python agents/iem_syndicate.py test
```

### 🚀 GitHub Actions

Use the new Solana workflow:

1. Go to Actions tab
2. Select "Deploy Dream-Mind-Lucid to Solana" 
3. Choose action: `deploy`, `test-dream`, `test-mev`, or `monitor`
4. Run workflow

### 📊 Monitoring

Monitor both networks:

```bash
# Solana event monitoring
python agents/solana_dream_syndicate.py monitor

# Legacy SKALE monitoring  
python agents/iem_looter.py
```

### 🔐 Security

- Private keys are optional (simulation mode available)
- All transactions are logged to `iem_memory.json`
- Audit trails for both Solana and SKALE deployments
- MEV protection prevents value extraction

### 📞 Support

For migration assistance:
- Check `iem_memory.json` for deployment status
- Review GitHub Actions logs for detailed output
- Use simulation mode for testing without real funds

---

*The future of dream-mining is multi-chain! 🌌*