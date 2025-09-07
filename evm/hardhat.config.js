require('@nomiclabs/hardhat-ethers');
require('dotenv').config();

module.exports = {
  solidity: {
    version: '0.8.20',
    settings: {
      optimizer: { enabled: true, runs: 200 }
    }
  },
  networks: {
    local: {
      url: process.env.SKALE_RPC || "http://127.0.0.1:8545",
      chainId: parseInt(process.env.SKALE_CHAIN_ID || "54173"),
      accounts: process.env.DEPLOYER_KEY ? [process.env.DEPLOYER_KEY] : undefined
    }
  },
  paths: {
    sources: './evm/contracts',
    tests: './evm/test',
    cache: './evm/cache',
    artifacts: './evm/artifacts'
  }
};
