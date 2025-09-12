# GitHub Secrets Setup

This script helps you easily configure GitHub repository secrets for the Dream-Mind-Lucid blockchain ecosystem.

## Prerequisites

- [GitHub CLI](https://cli.github.com/) installed and authenticated
- Access to the repository (admin permissions required for setting secrets)

## Usage

### Basic usage with .env file
```bash
./scripts/setup_github_secrets.sh
```

### Specify different repository
```bash
./scripts/setup_github_secrets.sh owner/repo-name
```

### Use custom .env file
```bash
./scripts/setup_github_secrets.sh owner/repo-name path/to/custom.env
```

### Interactive mode (no .env file)
If no .env file is found, the script will prompt for each secret interactively.

## Supported Secrets

The script configures the following secrets used by Dream-Mind-Lucid workflows:

### Core Blockchain
- `INFURA_PROJECT_ID` - Infura API project ID
- `ALCHEMY_API_KEY` - Alchemy API key
- `ANKR_API_KEY` - Ankr API key
- `DEPLOYER_KEY` - Private key for contract deployment
- `SOLANA_DEPLOYER_KEY` - Solana wallet private key
- `WALLET_MNEMONIC` - Wallet mnemonic phrase
- `ETHERSCAN_API_KEY` - Etherscan API key for verification

### Network Configuration
- `SKALE_RPC` - SKALE network RPC URL
- `SKALE_CHAIN_ID` - SKALE chain ID
- `SOLANA_RPC_URL` - Solana RPC endpoint

### Gasless Transactions
- `BICONOMY_API_KEY` - Biconomy relayer API key
- `BICONOMY_FORWARDER_ADDRESS` - Biconomy forwarder contract
- `GELATO_API_KEY` - Gelato relayer API key
- `FORWARDER_ADDRESS` - Generic forwarder address

### Storage & IPFS
- `IPFS_PROJECT_ID` - IPFS project ID
- `IPFS_PROJECT_SECRET` - IPFS project secret

### Frontend Hosting
- `VERCEL_TOKEN` - Vercel deployment token
- `VERCEL_ORG_ID` - Vercel organization ID
- `VERCEL_PROJECT_ID` - Vercel project ID
- `NETLIFY_AUTH_TOKEN` - Netlify authentication token
- `NETLIFY_SITE_ID` - Netlify site ID
- `FLEEK_API_KEY` - Fleek API key

### AI & Context APIs
- `MODEL_CONTEXT_API_KEY` - Model context API key
- `MCP_API_KEY` - MCP API key

## Security Notes

- Sensitive values (containing KEY, SECRET, MNEMONIC, DEPLOYER, TOKEN) are hidden during input
- The script uses GitHub CLI's secure secret storage
- Never commit actual secret values to the repository

## Example .env file

```bash
# Core secrets
DEPLOYER_KEY="0x1234..."
INFURA_PROJECT_ID="your-infura-project-id"
BICONOMY_API_KEY="your-biconomy-key"

# Network configuration
SKALE_RPC="https://mainnet.skalenodes.com/v1/elated-tan-skat"
SKALE_CHAIN_ID="2046399126"
```