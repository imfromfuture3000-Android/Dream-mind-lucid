# Dream-Mind-Lucid: Decentralized Dream-Mining Investment Platform

## 🚀 Now Available on Solana with MEV Protection!

Dream-Mind-Lucid has been enhanced with **Solana blockchain support**, featuring SPL Token 2022 standards, automatic SOL rebates, and built-in MEV protection while maintaining full backward compatibility with SKALE.

## Overview
Dream-Mind-Lucid is a multi-chain blockchain platform designed for dream-mining, cognitive staking, and lucidity-based access controls. Originally launched on SKALE Network (August 30, 2025), it now supports **Solana mainnet** with enhanced features including automatic SOL rebates via post-trade backruns and zero-risk MEV protection. The platform enables users to record and validate dreams, earn tokens through staking and governance, and access predictive oracles for strategic investment decisions.

## 🌟 New Solana Features

- **🛡️ MEV Protection**: Automatic SOL rebates from profitable backruns (1% of profits, minimum 0.001 SOL)
- **⚡ SPL Token 2022**: Enhanced token standards for DREAM, SMIND, and LUCID tokens  
- **🌐 Helius RPC**: High-performance Solana access with WebSocket support
- **💰 Treasury Integration**: Unified treasury at `4eJZVbbsiLAG6EkWvgEYEWKEpdhJPFBYMeJ6DBX98w6a`
- **🔄 Multi-Chain**: Supports both Solana and SKALE networks

## Tokenomics and Investment Opportunities
The platform features a triple-token model optimized for investment growth and community governance, now available on both **Solana** (SPL Token 2022) and **SKALE** networks:

- **DREAM Token**: Utility for dream mining and community governance (total supply: 777,777,777). Investors can participate in yield generation through dream validation, with potential for appreciation as the ecosystem expands. **Enhanced on Solana with MEV protection**.
- **SMIND Token**: Focused on cognitive staking and neural committee participation (total supply: 777,777,777). Staking provides passive returns, positioning SMIND as a stable investment for long-term holders in the neural economy.
- **LUCID Token**: Access key to Lucid Zones and AI oracles (total supply: 333,333,333). Enables entry into future-prediction arenas, offering high-reward opportunities for speculative investors.

### 🛡️ MEV Protection (Solana)
Unique to our Solana implementation:
- **Automatic SOL Rebates**: Receive 1% of backrun profits from your transactions
- **Zero MEV Risk**: Built-in protection against front-running and sandwich attacks  
- **Treasury Funded**: All rebates paid from program treasury (`4eJZVbbsiLAG6EkWvgEYEWKEpdhJPFBYMeJ6DBX98w6a`)
- **Minimum Guarantee**: 0.001 SOL minimum rebate per qualifying transaction

All tokens operate on **Solana mainnet** (enhanced features) and **SKALE Europa** (Chain ID: 2046399126, zero gas fees), providing multiple pathways for participation and maximizing ROI for deployers and participants.

## Key Features
- **Dream Mining with AI Validation**: Submit dreams for novelty, emotion, and coherence scoring, earning tokens as rewards. This creates a data-driven investment model where validated dreams contribute to network value.
- **Zero-Gas Transactions**: Powered by SKALE, ensuring cost-effective deployment and operations for investors and developers.
- **Cognitive Staking**: Stake SMIND tokens for governance rights and yields, fostering a self-sustaining investment ecosystem.
- **Lucid Gates**: Access predictive arenas for future insights, enabling informed investment strategies in parallel reality threads.
- **The Oneiro-Sphere (Future Roadmap)**: A quantum dream network interfacing human consciousness with AI, evolving tokens into mediums for thought-exchange in a post-scarcity framework. This positions the platform as a long-term investment in emerging neural technologies.

## Repository Structure
- `contracts/IEMDreams.sol`: Core smart contract for dream recording and event emission.
- `agents/iem_syndicate.py`: Multi-agent Python script for deployment, auditing, event listening, and state synchronization.
- `agents/iem_looter.py`: Specialized script for real-time event monitoring and data persistence.
- `.github/workflows/deploy-verify.yml`: GitHub Actions workflow for automated deployment and verification.
- `iem_memory.json`: Persistent storage for deployment artifacts and audited data.

## Deployment and Development Guidelines
To deploy and manage the platform as an investment creator:

### 🚀 Solana Deployment (Recommended)

1. **Quick Setup**:
   ```bash
   # Install all dependencies (Rust, Solana CLI, Anchor, Python packages)
   ./install-solana.sh
   
   # Configure environment
   source solana-config.sh
   ```

2. **Deploy to Solana**:
   ```bash
   # Deploy full ecosystem (simulation mode by default)
   python agents/solana_dream_syndicate.py deploy
   
   # Test dream recording
   python agents/solana_dream_syndicate.py test-dream
   
   # Test MEV protection
   python agents/solana_dream_syndicate.py test-mev
   ```

3. **Real Deployment** (with actual SOL):
   ```bash
   export DEPLOYER_KEY="your-base58-private-key"
   export SYNDICATE_SIMULATE="0"
   python agents/solana_dream_syndicate.py deploy
   ```

### 🌌 Legacy SKALE Deployment

1. **Prerequisites**:
   - Install Git and Python 3.11+.
   - Install dependencies: `pip install -r requirements.txt`.
   - Configure a SKALE-compatible wallet (e.g., MetaMask) with test SKL from https://sfuel.skale.space/europa.

2. **Configuration**:
   - Set environment variables or GitHub Secrets:
     - `SKALE_RPC`: `https://mainnet.skalenodes.com/v1/elated-tan-skat`
     - `DEPLOYER_KEY`: Your private key for deployment (securely stored).
     - `SKALE_CHAIN_ID`: `2046399126`.

3. **Deployment**:
   - Deploy the contract: `python agents/iem_syndicate.py deploy OneiroSphere`.
   - Audit the deployment: `python agents/iem_syndicate.py audit`.
   - Monitor events: `python agents/iem_looter.py`.

4. **Testing and Interaction**:
   - **Solana**: Use the built-in test commands or interact via Solana CLI/web3.js
   - **SKALE**: Use Remix (https://remix.ethereum.org) to interact with deployed contracts
   - Submit dreams and verify event emission on both networks
   - For investment simulation, stake tokens to test yield generation

5. **Security and Auditing**:
   - **Solana**: Automatic program verification and MEV protection built-in
   - **SKALE**: The Auditor agent computes SHA-256 hashes for contract integrity
   - All deployments logged to `iem_memory.json` with transaction details
   - Future enhancements include zero-knowledge proofs for enhanced privacy

6. **Roadmap**:
   - Short-Term: Full Solana program optimization and cross-chain bridges
   - Medium-Term: Enhanced MEV protection and yield farming integration  
   - Long-Term: The Oneiro-Sphere quantum dream network spanning multiple chains

## Investment Considerations
Dream-Mind-Lucid offers a unique entry into the neural economy, with potential for high returns through token appreciation and staking yields. As a deployer tool, it enables creators to launch customized investment vehicles on SKALE, with low barriers to entry and high scalability. Investors are advised to conduct due diligence, considering blockchain risks such as volatility and smart contract vulnerabilities. For professional deployment services or partnerships, open an issue on GitHub.

## Contribution and Contact
Contributions are welcome via fork and pull request. For investment inquiries or collaborations, submit an issue or contact the maintainer at the repository's discussion forum.

*Last Updated: August 30, 2025*
