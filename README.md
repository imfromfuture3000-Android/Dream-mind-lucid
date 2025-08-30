# 🚀 Dream-Mind-Lucid: The Dream Adventure!

Welcome to **Dream-Mind-Lucid**, a super cool project where your dreams become magic coins on the SKALE blockchain! It’s like a video game world where you can share dreams, earn rewards, and explore the future. We started this on August 30, 2025, and it’s going to grow huge by 2089!

## 🌟 What’s This About?
- **DREAM Tokens**: 777,777,777 coins for making and ruling the dream world.
- **SMIND Tokens**: 777,777,777 coins for saving (staking) and joining a smart group.
- **LUCID Tokens**: 333,333,333 coins to open secret doors to see the future!
- **SKALE Network**: A fast, free-to-play blockchain (no fees!) using `https://mainnet.skalenodes.com/v1/elated-tan-skat` and Chain ID `2046399126`.

In the future (2089), this will become **The Oneiro-Sphere**—a giant dream network where your mind talks to computers!

## 🎮 How It Works
1. **Record Dreams**: Save your dreams using our magic rules (smart contract).
2. **Earn Coins**: Get DREAM, SMIND, or LUCID coins for cool dreams.
3. **Explore**: Open Lucid Gates to see future adventures (coming soon!).

## 🛠️ What’s Inside the Repo?
- `contracts/IEMDreams.sol`: The rulebook to record dreams on SKALE.
- `agents/iem_syndicate.py`: A robot with 4 friends:
  - **Deployer**: Sends the rulebook to SKALE.
  - **Auditor**: Checks if it’s safe.
  - **Looter**: Watches for new dreams.
  - **Oracle**: Updates the game info.
- `agents/iem_looter.py`: A treasure-hunting robot that catches dreams!
- `.github/workflows/deploy-verify.yml`: Auto-magic that builds stuff on GitHub when you save.

## 🚧 How to Build It (For Big Kids or Grown-Ups)

### 📋 Prerequisites
- Install Git (git-scm.com) and Python (python.org)
- GitHub account with repository access

### 🔧 Local Development Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/imfromfuture3000-Android/Dream-mind-lucid.git
   cd Dream-mind-lucid
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (for local testing):
   ```bash
   export SKALE_RPC="https://mainnet.skalenodes.com/v1/elated-tan-skat"
   export DEPLOYER_KEY="your-wallet-secret-key"  # Keep this super secret!
   export SKALE_CHAIN_ID="2046399126"
   ```

### 🚀 GitHub Actions Automated Deployment

The repository now includes automated GitHub Actions workflows! Here's how to set them up:

1. **Set Up GitHub Secrets** (Repository Settings > Secrets > Actions):
   - `SKALE_RPC`: `https://mainnet.skalenodes.com/v1/elated-tan-skat`
   - `DEPLOYER_KEY`: Your wallet secret key (keep it super secret!)
   - `SKALE_CHAIN_ID`: `2046399126`

2. **Automatic Deployment**:
   - Push to `main` branch → Automatically deploys to SKALE
   - Create Pull Request → Runs tests and validation
   - Manual deployment available via "Actions" tab

3. **Manual Deployment**:
   - Go to "Actions" tab in GitHub
   - Select "🚀 Deploy & Verify Dream Contracts"
   - Click "Run workflow" → Enable "Deploy to SKALE Network"

### 🛠️ Local Development Commands
   - Go to the folder: `cd Desktop/dream-mind-lucid` (or where you saved it).
   - Deploy: `python agents/iem_syndicate.py deploy` (set `DEPLOYER_KEY` with `export DEPLOYER_KEY='your-secret-key'`).
   - Watch dreams: `python agents/iem_looter.py`.
4. **Test a Dream**:
   - Use Remix (remix.ethereum.org) to send a dream (e.g., “I flew with a dragon!”) to the contract address (from `iem_memory.json`).

## 🌌 The Oneiro-Sphere (Future Dream Land)
By 2089, this will be a quantum dream network! We’ll add:
- A new rulebook (`OneiroSphere.sol`) to connect minds and computers.
- Secret doors (Lucid Gates) with LUCID coins.
- More robots to make it grow!

## 🤝 Help Us Build!
- Share your ideas or fix bugs by clicking “Fork” and sending a “Pull Request”.
- Ask questions in the “Issues” tab.

## 🎉 Let’s Dream Big!
Started on August 30, 2025, by imfromfuture3000-Android and friends. With your help, we’ll build a dream world that lasts forever! 🚀

*Last updated: 04:54 PM PST, August 30, 2025*
