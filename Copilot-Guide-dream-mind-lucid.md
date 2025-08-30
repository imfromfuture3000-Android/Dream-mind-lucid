/*
# Copilot Guide for dream-mind-lucid
*Date: August 30, 2025, 05:15 PM PST*

---

## Project Overview

- **Mission:** Build a dream ecosystem on the SKALE blockchain for `dream-mind-lucid`.
- **Tokens:**
  - DREAM: `777,777,777`
  - SMIND: `777,777,777`
  - LUCID: `333,333,333`
- **Vision:** By 2089, launch The Oneiro-Sphere (quantum dream network).

---

## SKALE Info

- **RPC Endpoint:** `https://mainnet.skalenodes.com/v1/elated-tan-skat`
- **Chain ID:** `2046399126` (Europa Hub)
- **Gas:** Zero-gas transactions (SKALE exclusive).

---

## Repo Structure

- `contracts/IEMDreams.sol`: Records dreams via `DreamRecorded` event. **Enhance:** Add DREAM token logic.
- `agents/iem_syndicate.py`: Multi-agent script (Deployer, Auditor, Looter, Oracle). Uses `web3.py` and `solcx` (Solidity 0.8.20).
- `agents/iem_looter.py`: Listens for `DreamRecorded` events, logs to `iem_memory.json`.
- `.github/workflows/deploy-verify.yml`: Automates deployment with GitHub Actions.

---

## Future Plans

- `contracts/OneiroSphere.sol`: Quantum dream network, `interfaceDream` function.
- IPFS integration for dream storage (`pip install ipfshttpclient`).
- Lucid Gates: Access control with LUCID token.
- Quantum dream attestation.

---

## Code Examples

### IEMDreams.sol

```solidity
pragma solidity ^0.8.20;
contract IEMDreams {
    event DreamRecorded(address indexed dreamer, string dream);
    function recordDream(string memory dream) public {
        emit DreamRecorded(msg.sender, dream);
    }
}
```

### iem_syndicate.py (deploy function)

```python
def deploy_contract():
    from solcx import compile_standard, install_solc
    install_solc("0.8.20")
    # ... (compile and deploy logic)
```

### OneiroSphere.sol (future)

```solidity
pragma solidity ^0.8.20;
contract OneiroSphere {
    mapping(address => string[]) public dreams;
    event DreamInterfaced(address indexed dreamer, string ipfsHash);
    function interfaceDream(string memory ipfsHash) public {
        dreams[msg.sender].push(ipfsHash);
        emit DreamInterfaced(msg.sender, ipfsHash);
    }
}
```

---

## Instructions

- **Test deploy:**  
  `python agents/iem_syndicate.py deploy`  
  _Set environment:_ `export DEPLOYER_KEY='your-key'`
- **Run looter:**  
  `python agents/iem_looter.py`
- **Send dreams:**  
  Use Remix (`remix.ethereum.org`)
- **GitHub secrets:**  
  - `SKALE_RPC`
  - `DEPLOYER_KEY`
  - `SKALE_CHAIN_ID`

---

## Copilot Hints

- Suggest ERC-20 token functions for DREAM, SMIND, LUCID.
- Integrate IPFS:  
  `ipfs_client = ipfshttpclient.connect()`
- Add `oneirosphere` agent to `iem_syndicate.py` for The Oneiro-Sphere.
*/