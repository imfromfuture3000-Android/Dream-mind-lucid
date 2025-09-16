# SKALE Consensus Integration

This directory contains the C++ implementation for integrating Dream-Mind-Lucid with SKALE consensus.

## Building

1. Install dependencies:

```bash
sudo apt update
sudo apt install -y cmake g++-11 libssl-dev libprocps-dev
```

1. Build the consensus module:

```bash
mkdir build && cd build
cmake ..
make -j$(nproc)
```

## Integration Details

The consensus integration provides:

- BLS signature verification for dream blocks
- SKALE chain consensus participation
- Dream state synchronization across nodes
- Automatic block finalization and state updates

## Configuration

Create a config.json file with:

```json
{
  "nodeCount": 16,
  "requiredSignatures": 11,
  "nodes": [
    {
      "nodeID": 1,
      "ip": "127.0.0.1",
      "port": 1231,
      "publicKey": "..."
    }
    // ... more nodes ...
  ]
}
```

## Usage

```cpp
#include "DreamConsensus.h"

// Initialize consensus
dream::DreamConsensus consensus("config.json");
consensus.initialize(16, 11);

// Propose new dream blocks
consensus.proposeDreamBlock("dreamer_id", "dream_data");

// Check consensus status
uint64_t height = consensus.getBlockHeight();
std::string latestBlock = consensus.getLatestDreamBlock();
```

## Testing

Run tests with:

```bash
cd build
./dream_consensus_test
```
