# Dream-Mind-Lucid → SKALE/EVM Integration (scaffold)

This folder contains a minimal EVM contract and a lightweight OneiroAgent simulator to start porting the Dream-Mind-Lucid consensus to EVM/Skale.

Files added:
- `evm/contracts/DreamRecords.sol` — Minimal contract that stores dream records and emits events.
- `oneiroagent/agent.py` — Simple Python agent that can submit dream records and listen for events.
- `oneiroagent/requirements.txt` — Python dependencies for the agent.

Quick start (local Ganache or an RPC endpoint):

1. Deploy `DreamRecords.sol` using your preferred tool (Hardhat/Foundry/Remix).
2. Set environment variables:

```powershell
$env:WEB3_RPC = "http://127.0.0.1:8545"
$env:CONTRACT_ADDRESS = "0x..."
# optional
$env:PRIVATE_KEY = "0x..."
```

3. Run the listener:

```powershell
python oneiroagent\agent.py
```

4. Submit a dream:

```powershell
python oneiroagent\agent.py submit
```

Next steps:
- Implement Lucid block assembly off-chain and submit finalized block headers to an EVM contract.
- Add threshold signature verification (BLS) via a precompile or on-chain verifier.
- Implement catchup and storage contracts for committed lucid blocks.
