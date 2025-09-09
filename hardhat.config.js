require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

const PRIVATE_KEY = process.env.PRIVATE_KEY;
const SKALE_RPC = process.env.SKALE_RPC || "https://mainnet.skalenodes.com/v1/elated-tan-skat";
const SKALE_CHAIN_ID = parseInt(process.env.SKALE_CHAIN_ID) || 2046399126;

/** @type import('hardhat/config').HardhatUserConfig */
module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      }
    }
  },
  networks: {
    skale: {
      url: SKALE_RPC,
      chainId: SKALE_CHAIN_ID,
      accounts: PRIVATE_KEY ? [PRIVATE_KEY] : [],
      gas: 8000000,
      gasPrice: 0,  // SKALE has zero gas fees
      timeout: 120000  // 2 minutes
    }
  },
  gasReporter: {
    enabled: (process.env.REPORT_GAS) ? true : false
  }
};
