# OneiroSphere Deployment Guide

## Prerequisites

1. **Environment Setup**:
   - Python 3.11+
   - Git
   - SKALE-compatible wallet with test SKL tokens from https://sfuel.skale.space/europa

2. **Required Environment Variables** (set in `.env` or GitHub Secrets):
   ```bash
   SKALE_RPC=https://mainnet.skalenodes.com/v1/elated-tan-skat
   SKALE_CHAIN_ID=2046399126
   INFURA_PROJECT_ID=your-infura-api-key
   BICONOMY_API_KEY=your-biconomy-api-key
   FORWARDER_ADDRESS=0xyour-biconomy-forwarder
   DEPLOYER_KEY=your-wallet-private-key
   ```

## Installation

1. **Clone Repository**:
   ```bash
   git clone https://github.com/imfromfuture3000-Android/Dream-mind-lucid.git
   cd Dream-mind-lucid
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment**:
   - Copy `.env.example` to `.env` and fill in your values
   - Or set environment variables directly

## Deployment Commands

### Deploy OneiroSphere Contract
```bash
python agents/iem_syndicate.py deploy OneiroSphere
```

### Deploy IEMDreams Contract
```bash
python agents/iem_syndicate.py deploy IEMDreams
```

### Audit Deployed Contract
```bash
python agents/iem_syndicate.py audit <contract_address>
```

### Record Test Dream
```bash
python agents/iem_syndicate.py test <contract_address> "My lucid dream experience"
```

### Monitor Events
```bash
python agents/iem_looter.py <contract_address> 300  # Monitor for 5 minutes
```

### Check Deployment Status
```bash
python agents/iem_syndicate.py status
```

## GitHub Actions Deployment

The repository includes automated deployment via GitHub Actions:

1. **Set GitHub Secrets**:
   - `SKALE_RPC`
   - `SKALE_CHAIN_ID`
   - `DEPLOYER_KEY`
   - `INFURA_PROJECT_ID`
   - `BICONOMY_API_KEY`
   - `FORWARDER_ADDRESS`

2. **Manual Deployment**:
   - Go to Actions tab in GitHub
   - Select "Deploy and Verify Dream-Mind-Lucid"
   - Click "Run workflow"
   - Choose contract to deploy

## Contract Verification

After deployment, verify on SKALE Explorer:
- **SKALE Explorer**: https://elated-tan-skat.explorer.mainnet.skalenodes.com/address/YOUR_CONTRACT_ADDRESS

## Contract Interactions

### OneiroSphere Functions:
- `interfaceDream(string ipfsHash)` - Interface a dream with IPFS
- `createQuantumEntanglement(address dreamer2, string sharedHash)` - Create quantum entanglement
- `scoreLucidity(string ipfsHash, uint256 score)` - Score dream lucidity
- `getDreams(address dreamer)` - Get all dreams for a dreamer
- `balanceOf(address account)` - Check LUCID token balance

### Using Remix IDE:
1. Go to https://remix.ethereum.org
2. Connect to SKALE Network:
   - Network: Custom RPC
   - RPC URL: `https://mainnet.skalenodes.com/v1/elated-tan-skat`
   - Chain ID: `2046399126`
3. Import contract ABI and address from `iem_memory.json`
4. Interact with contract functions

## Troubleshooting

### Common Issues:

1. **Connection Errors**: 
   - Check RPC URLs are correct
   - Verify network connectivity
   - Try Infura RPC as fallback

2. **Gas Errors**:
   - SKALE has zero gas fees
   - Ensure `gasPrice: 0` in transactions

3. **Private Key Issues**:
   - Ensure DEPLOYER_KEY is set correctly
   - Private key should not include '0x' prefix

4. **Compilation Errors**:
   - Solidity 0.8.20 is required
   - Check contract syntax

### Getting Help:
- Check deployment logs in `iem_memory.json`
- Review GitHub Actions logs for automated deployments
- Verify contract on SKALE Explorer

## Security Notes

- Never commit private keys to version control
- Use environment variables or GitHub Secrets for sensitive data
- Audit contracts before mainnet deployment
- Test thoroughly on testnet first

## Next Steps

After successful deployment:
1. Record test dreams to verify functionality
2. Monitor events with IEM Looter
3. Set up IPFS integration for dream storage
4. Configure Biconomy for gasless transactions
5. Deploy Lucid Gates for oracle access