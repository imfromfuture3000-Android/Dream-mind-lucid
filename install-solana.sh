#!/bin/bash
# Solana Dream-Mind-Lucid Installation Script
# Installs all necessary dependencies for Solana deployment

set -e

echo "🚀 Installing Dream-Mind-Lucid Solana Dependencies"
echo "================================================="

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install solana anchorpy spl-token aiohttp base58 construct

# Install Rust (needed for building programs)
echo "🦀 Installing Rust..."
if ! command -v rustup &> /dev/null; then
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source ~/.cargo/env
else
    echo "✅ Rust already installed"
fi

# Install Solana CLI
echo "⚡ Installing Solana CLI..."
if ! command -v solana &> /dev/null; then
    sh -c "$(curl -sSfL https://release.solana.com/v1.17.0/install)"
    echo 'export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"' >> ~/.bashrc
    export PATH="$HOME/.local/share/solana/install/active_release/bin:$PATH"
else
    echo "✅ Solana CLI already installed"
fi

# Install Anchor (for building Solana programs)
echo "⚓ Installing Anchor..."
if ! command -v anchor &> /dev/null; then
    cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
    avm install latest
    avm use latest
else
    echo "✅ Anchor already installed"
fi

# Create Solana wallet if it doesn't exist
echo "🔑 Setting up Solana wallet..."
if [ ! -f ~/.config/solana/id.json ]; then
    mkdir -p ~/.config/solana
    solana-keygen new --outfile ~/.config/solana/id.json --no-bip39-passphrase
else
    echo "✅ Solana wallet already exists"
fi

# Set Solana config
echo "⚙️ Configuring Solana..."
solana config set --url mainnet-beta
solana config set --keypair ~/.config/solana/id.json

echo ""
echo "✅ Installation completed successfully!"
echo ""
echo "🌟 Next Steps:"
echo "1. Fund your wallet with SOL: solana airdrop 1 (testnet) or transfer from exchange"
echo "2. Load configuration: source solana-config.sh"
echo "3. Deploy: python agents/solana_dream_syndicate.py deploy"
echo "4. Test: python agents/solana_dream_syndicate.py test-dream"
echo ""
echo "💡 Your wallet address: $(solana address)"
echo "💰 Your balance: $(solana balance) SOL"
echo ""
echo "🛡️ MEV Protection and SOL rebates are now available!"