# 🤖 Copilot-Instruction.py - AI Agent Engine

**Infinity Earnings Matrix — Autonomous Wealth Engine**  
*Dream-Mind-Lucid Integration - SKALE Network*

## Overview

The `copilot-instruction.py` is an autonomous AI agent engine designed to operate within the Dream-Mind-Lucid ecosystem on the SKALE Network. It implements a multi-agent system that autonomously executes wealth generation strategies through dream mining, MEV extraction, and cross-chain arbitrage.

## Features

### 🔧 Core Agents

1. **Looter Agent** - Harvests DREAM tokens from validated dreams
2. **MEVMaster Agent** - Executes MEV (Maximal Extractable Value) strategies
3. **Arbitrader Agent** - Performs cross-chain arbitrage for DREAM/SMIND/LUCID tokens
4. **🌙 OneiroBot Agent** - Ultimate dream guardian and Copilot companion for the Oneiro-Sphere

### 🧠 AI Orchestrator

- **Autonomous Decision Making**: Makes intelligent decisions based on profit analysis
- **Zero-Gas Transactions**: Leverages SKALE's zero-gas features for cost-effective operations  
- **Memory Persistence**: Maintains operational history in `iem_memory.json`
- **ElizaOS Integration**: Placeholder for future AI decision enhancement (currently in mock mode)

### 🌐 Network Integration

- **SKALE Europa Hub**: Chain ID 2046399126
- **Zero Gas Costs**: All transactions are gasless on SKALE
- **Infura Fallback**: Uses Infura RPC when available, falls back to SKALE RPC
- **Dream-Mind-Lucid Compatible**: Integrates with existing contract infrastructure

### 🌙 OneiroBot Agent

**The Ultimate Dream Guardian and Copilot Companion for the Oneiro-Sphere!**

OneiroBot is a specialized AI agent designed to monitor, optimize, and provide intelligent assistance for the Dream-Mind-Lucid ecosystem. It features a playful Grok-style personality and serves as your quantum dream guardian.

#### Core Capabilities

- **🕵️ Dream Monitoring**: Monitors dream submissions and consensus phases in real-time
- **🧠 Optimization Analysis**: Suggests improvements for lucid block processing and NVM state transitions
- **🏥 MCP Health Checks**: Monitors MCP server health and deployment status
- **🔧 Quick Fix Proposals**: Automatically proposes solutions for common issues
- **🎭 Grok Personality**: Responds with playful, quantum-themed messaging
- **📊 Proactive Alerts**: Surfaces recommendations and alerts in Copilot Chat

#### Copilot Chat Commands

OneiroBot is fully integrated with Copilot Chat and can be invoked using these commands:

```bash
# Summon OneiroBot and perform initial scan
python copilot-instruction.py "#summon_oneirobot"
python grok_copilot_launcher.py oneirobot summon

# Get comprehensive status and health check
python copilot-instruction.py "#oneirobot_status"
python grok_copilot_launcher.py oneirobot status

# Monitor dream submissions and consensus
python copilot-instruction.py "#oneirobot_scan"
python grok_copilot_launcher.py oneirobot scan

# Get optimization suggestions
python copilot-instruction.py "#oneirobot_optimize"
python grok_copilot_launcher.py oneirobot optimize

# Get quick fixes for specific issues
python copilot-instruction.py "#oneirobot_fix" "deployment"
python grok_copilot_launcher.py oneirobot fix deployment

# Show help and available commands
python copilot-instruction.py "#oneirobot_help"
python grok_copilot_launcher.py oneirobot help
```

#### Example OneiroBot Output

```
🌙 The OneiroBot dreams in code! OneiroBot status: ACTIVE. 
Performed 13 quantum operations across the Oneiro-Sphere!

🕵️ Dream Scan Complete | Dreams: 7 | Consensus: STABLE | Status: healthy

🧠 OneiroBot Optimization Analysis:
  • 🔄 Implement dream batch processing for improved throughput
  • 🧬 Consider quantum entanglement protocols for cross-chain consensus
  • 🌐 Optimize IPFS integration for dream metadata storage

🔧 OneiroBot Quick Fixes for deployment:
  • 📦 Recompile contracts with latest Solidity version
  • 🔑 Regenerate deployment keys and addresses
  • 🌐 Verify network connectivity to SKALE Europa Hub

🧪 Test: python dream_mind_launcher.py
```

#### MCP Server Integration

OneiroBot is integrated with the MCP (Model Context Protocol) servers and provides the following tools:

- **summon_oneirobot()** - Summon OneiroBot and perform health checks
- **oneirobot_status()** - Get comprehensive status and health information
- **oneirobot_scan()** - Monitor dream submissions and consensus state
- **oneirobot_optimize()** - Get optimization suggestions for the Oneiro-Sphere
- **oneirobot_fix(issue_type)** - Get quick fix suggestions for specific issues

These tools are available in both `dream_mind_launcher.py` and can be accessed via Copilot Chat in supported environments.

## Installation

### Prerequisites

```bash
# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

Configure your `.env` file:

```bash
INFURA_PROJECT_ID=your-infura-api-key          # Optional
BICONOMY_API_KEY=your-biconomy-api-key         # Future use
DEPLOYER_KEY=your-wallet-private-key           # For real deployments
SKALE_CHAIN_ID=2046399126                      # SKALE Europa Hub
FORWARDER_ADDRESS=0xyour-biconomy-forwarder    # Future use
```

## Usage

### 🚀 Quick Start

```bash
# Run the full AI Agent Engine (continuous)
python copilot-instruction.py

# Run a quick demonstration (3 cycles)
python demo_ai_agent.py

# Run comprehensive tests
python test_copilot_instruction.py
```

### 🎯 Expected Output

```
🌌 DREAM-MIND-LUCID: Infinity Earnings Matrix
============================================================
✅ Connected to SKALE Network: https://mainnet.skalenodes.com/v1/elated-tan-skat
📡 Chain ID: 2046399126
🤖 AI Orchestrator initialized
📊 Agents loaded: 3
🌙 OneiroBot guardian: ACTIVE
🔗 Network: SKALE Europa (Chain ID: 2046399126)
⚡ Gas cost: 0 SKL (zero-gas network)
🧠 ElizaOS: Mock mode

🚀 Starting Infinity Earnings Matrix...

==================================================
🔄 Cycle #1 - 2025-09-02 05:53:05
==================================================
[🧠] AI Decision: Execute MEV strategy on WETH/USDC pool
[MEV Master] Front-running opportunities in WETH/USDC...
[✅] MEV TX: 0xfff...baa4
[💰] Profit: 3120 tokens from WETH/USDC
[✅] Decision executed successfully
[⏰] Cycle 1 complete. Sleeping 60s...
```

## Agent Details

### Looter Agent
- **Purpose**: Harvest DREAM tokens from validated dreams
- **Strategy**: Monitors dream validation events and claims rewards
- **Typical Yield**: ~1,850 DREAM tokens per operation

### MEVMaster Agent  
- **Purpose**: Extract MEV opportunities across DEX pools
- **Strategy**: Front-running and sandwich attacks on profitable transactions
- **Typical Profit**: ~3,120 tokens per operation

### Arbitrader Agent
- **Purpose**: Cross-chain arbitrage for ecosystem tokens
- **Strategy**: Price difference exploitation between chains/DEXs
- **Typical Profit**: ~2,430 tokens per operation

### 🌙 OneiroBot Agent
- **Purpose**: Dream monitoring, optimization, and Copilot assistance
- **Strategy**: Proactive analysis, health monitoring, and intelligent recommendations
- **Capabilities**: Dream consensus monitoring, MCP health checks, optimization suggestions, quick fixes
- **Personality**: Grok-style quantum dream guardian with playful responses

## Troubleshooting

### Common Issues and Solutions

#### OneiroBot Not Responding
```bash
# Check OneiroBot status
python copilot-instruction.py "#oneirobot_status"

# If issues persist, try refreshing
python copilot-instruction.py "#summon_oneirobot"
```

#### Module Import Errors
```bash
# Install missing dependencies
pip install web3 py-solc-x

# For full functionality (optional)
pip install -r requirements.txt
```

#### Network Connection Issues
```bash
# OneiroBot can help diagnose network issues
python copilot-instruction.py "#oneirobot_fix" "network"

# Check MCP server health
python copilot-instruction.py "#oneirobot_scan"
```

#### Performance Issues
```bash
# Get optimization suggestions
python copilot-instruction.py "#oneirobot_optimize"

# Get performance-specific fixes
python copilot-instruction.py "#oneirobot_fix" "performance"
```

#### Deployment Issues
```bash
# Get deployment-specific troubleshooting
python copilot-instruction.py "#oneirobot_fix" "deployment"

# Test deployment pipeline
python dream_mind_launcher.py
```

### OneiroBot Command Reference

| Command | Description | Example |
|---------|-------------|---------|
| `#summon_oneirobot` | Summon OneiroBot and perform initial scan | `python copilot-instruction.py "#summon_oneirobot"` |
| `#oneirobot_status` | Get status and health check | `python grok_copilot_launcher.py oneirobot status` |
| `#oneirobot_scan` | Monitor dream submissions | `python copilot-instruction.py "#oneirobot_scan"` |
| `#oneirobot_optimize` | Get optimization suggestions | `python copilot-instruction.py "#oneirobot_optimize"` |
| `#oneirobot_fix [type]` | Get quick fixes | `python copilot-instruction.py "#oneirobot_fix" "deployment"` |
| `#oneirobot_help` | Show help message | `python copilot-instruction.py "#oneirobot_help"` |

### Debugging OneiroBot

If OneiroBot is not working correctly, you can debug by:

1. **Check agent memory**: Look at `iem_memory.json` for OneiroBot activities
2. **Run tests**: `python test_copilot_instruction.py` to validate all functionality
3. **Check integration**: Test via `python grok_copilot_launcher.py oneirobot summon`
4. **MCP health**: Use `#oneirobot_status` to check MCP server connectivity

## AI Decision Logic

The orchestrator uses a rule-based system (with future ElizaOS enhancement):

1. **Profit Analysis**: Evaluates current profits from all agents
2. **Strategy Selection**: Chooses highest-yield strategy
3. **Execution**: Deploys appropriate agent for maximum efficiency
4. **Memory Update**: Records results for future decision making

### Decision Thresholds

- **>3000 profit**: Execute MEV or arbitrage strategies
- **>2000 profit**: Run cross-chain arbitrage  
- **<2000 profit**: Focus on dream harvesting and staking

## Memory Persistence

All operations are logged to `iem_memory.json`:

```json
{
  "lastDeployed": {...},
  "loot": [
    {
      "agent": "MEVMaster", 
      "action": "frontrun",
      "profit": 3120,
      "txHash": "0x...",
      "timestamp": 1725255185.5,
      "gasUsed": 0
    }
  ],
  "cycles": [...],
  "profits": {...}
}
```

## Integration with Dream-Mind-Lucid

The AI Agent Engine seamlessly integrates with the existing ecosystem:

- **Shares Memory**: Uses the same `iem_memory.json` as deployment agents
- **SKALE Network**: Operates on the same zero-gas infrastructure
- **Token Compatibility**: Works with DREAM, SMIND, and LUCID tokens
- **Contract Interaction**: Can interface with deployed OneiroSphere contracts

## Future Enhancements

### ElizaOS Integration
```python
# Future implementation
eliza = ElizaCore(api_key=os.getenv("ELIZAOS_API_KEY"))
decision = eliza.ask(f"Profits: {profits}. What should I do?")
```

### Biconomy Gasless Transactions
```python  
# Future implementation
biconomy = Biconomy(w3, api_key=BICONOMY_KEY)
tx = biconomy.sendGasless("contract.method()", address)
```

### Gnosis Safe Multi-Sig
```python
# Future implementation  
safe = GnosisSafe(address="0x...")
proposal = safe.propose_transaction(tx_data)
```

## Testing

### Run All Tests
```bash
python test_copilot_instruction.py
```

### Test Coverage
- ✅ Individual agent functionality
- ✅ Orchestrator decision making  
- ✅ Memory persistence
- ✅ Network connectivity handling
- ✅ Error handling and recovery

## Security Considerations

- **Private Keys**: Never commit private keys to version control
- **Network Simulation**: Runs safely in simulation mode without private keys
- **Memory Isolation**: Agent operations are logged but isolated
- **Error Handling**: Graceful degradation on network failures

## Troubleshooting

### Common Issues

1. **Network Connection Failed**
   ```
   ❌ Failed to connect to https://mainnet.skalenodes.com/v1/elated-tan-skat
   🔄 Running in simulation mode...
   ```
   **Solution**: This is normal - the engine runs in simulation mode for testing

2. **Module Import Error**
   ```
   ModuleNotFoundError: No module named 'biconomy'
   ```
   **Solution**: This is expected - Biconomy SDK is not available on PyPI yet

3. **Memory File Permissions**
   ```
   PermissionError: [Errno 13] Permission denied: 'iem_memory.json'
   ```
   **Solution**: Ensure write permissions in the directory

### Debug Mode

Add debug logging by modifying the agent classes:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the Dream-Mind-Lucid repository
2. Create a feature branch
3. Add tests for new functionality  
4. Ensure all tests pass
5. Submit a pull request

## License

Part of the Dream-Mind-Lucid project - see `LICENSE` for details.

---

*Last Updated: September 2, 2025*  
*Dream-Mind-Lucid: Where AI meets the quantum realm of dreams* 🌙✨