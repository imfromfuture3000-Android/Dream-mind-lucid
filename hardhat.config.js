require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const PRIVATE_KEY = process.env.PRIVATE_KEY || process.env.DEPLOYER_KEY;
const SKALE_RPC = process.env.SKALE_RPC || "https://mainnet.skalenodes.com/v1/elated-tan-skat";
const SKALE_CHAIN_ID = parseInt(process.env.SKALE_CHAIN_ID) || 2046399126;
const INFURA_GAS_API = process.env.INFURA_GAS_API || "https://gas.api.infura.io/v3/96e56809f7fc4662b56852c0f3f63c1a";

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      },
      viaIR: true  // Enable via-IR for better optimization
    }
  },
  networks: {
    hardhat: {
      chainId: 31337
    },
    skale: {
      url: SKALE_RPC,
      chainId: SKALE_CHAIN_ID,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      gas: 8000000,
      gasPrice: 0,  // SKALE has zero gas fees
      timeout: 120000,  // 2 minutes
      // Infura Gas API integration for gas estimation
      gasMultiplier: 1.2
    },
    // Add localhost for testing
    localhost: {
      url: "http://127.0.0.1:8545",
      chainId: 31337
    }
  },
  gasReporter: {
    enabled: (process.env.REPORT_GAS) ? true : false,
    currency: "USD",
    gasPrice: 0,  // Zero gas for SKALE
    coinmarketcap: process.env.COINMARKETCAP_API_KEY
  },
  etherscan: {
    // SKALE Europa Hub explorer
    apiKey: {
      skale: "no-api-key-needed"
    },
    customChains: [
      {
        network: "skale",
        chainId: SKALE_CHAIN_ID,
        urls: {
          apiURL: "https://elated-tan-skat.explorer.mainnet.skalenodes.com/api",
          browserURL: "https://elated-tan-skat.explorer.mainnet.skalenodes.com"
        }
      }
    ]
  },
  // Enhanced settings for Mint Gene deployment
  paths: {
    sources: "./contracts",
    tests: "./test",
    cache: "./cache",
    artifacts: "./artifacts"
  },
  mocha: {
    timeout: 60000  // 60 seconds for mainnet tests
  }
};
