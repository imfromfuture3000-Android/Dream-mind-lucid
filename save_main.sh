# Dream Mind Lucid - Main Branch Push Script
# This script prepares and pushes the main contract files and configurations

# 1. Check git status
git status

# 2. Add main contract files
git add contracts/DreamPerformanceDistributor.sol
git add contracts/DreamEconomicEngine.sol
git add contracts/DreamStaking.sol
git add contracts/interfaces/IDreamOracle.sol

# 3. Add deployment configurations
git add hardhat.config.js
git add package.json
git add scripts/deploy.js
git add .env.sample
git add DEPLOYMENT.md

# 4. Add configuration files
git add .gitignore
git add README.md

# 5. Commit with meaningful message
git commit -m "feat: Add Dream ecosystem core contracts and deployment

- Add DreamPerformanceDistributor contract
- Add DreamEconomicEngine with dynamic parameters
- Add DreamStaking with flexible lock periods
- Add deployment scripts and configurations
- Update documentation and environment samples"

# 6. Push to main branch
git push origin main
