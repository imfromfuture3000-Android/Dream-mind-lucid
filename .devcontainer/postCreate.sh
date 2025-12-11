#!/bin/bash
set -euo pipefail

echo "🚀 Setting up SKALE Consensus development environment..."

# Setup GCC 11 as default
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-11 100
sudo update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-11 100

# Clone SKALE consensus if not exists
CONSENSUS_DIR="/workspace/skale-consensus"
if [ ! -d "$CONSENSUS_DIR" ]; then
    echo "📦 Cloning SKALE consensus..."
    git clone --recurse-submodules https://github.com/skalenetwork/skale-consensus.git "$CONSENSUS_DIR"
fi

# Build SKALE consensus deps
echo "🔨 Building SKALE consensus dependencies..."
cd "$CONSENSUS_DIR/deps"
./build.sh DEBUG=1

# Configure and build consensus
echo "🏗️ Building SKALE consensus..."
cd ..
cmake . -Bbuild -DCMAKE_BUILD_TYPE=Debug
cmake --build build -- -j$(nproc)

# Install Node.js and npm
echo "📦 Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install project dependencies
echo "📚 Installing project dependencies..."
cd /workspace/evm
npm install --silent || true

cd /workspace
if [ -f requirements.txt ]; then
    pip install -r requirements.txt --user || true
fi

echo "✅ Development environment ready!"
