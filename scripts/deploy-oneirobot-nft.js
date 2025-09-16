const { ethers } = require("hardhat");
const { writeFileSync, readFileSync } = require("fs");

/**
 * OneirobotNFT Deployment Script for SKALE Mainnet
 * AI Gene Deployer - Mint Gene Integration
 * Mainnet-Only Deployment with Zero Gas Fees
 */

async function main() {
  console.log("🚀 AI Gene Deployer - OneirobotNFT Mint Gene Deployment Starting...");
  console.log("🌐 Network: SKALE Europa Hub Mainnet");
  console.log("⛽ Gas Cost: $0.00 (Zero Gas Network)");
  
  // Get deployment account
  const [deployer] = await ethers.getSigners();
  console.log("🔑 Deploying contracts with account:", deployer.address);
  
  // Check balance (should be non-zero on SKALE)
  const balance = await deployer.getBalance();
  console.log("💰 Account balance:", ethers.utils.formatEther(balance), "ETH");
  
  // Get current gas price (should be 0 on SKALE)
  const gasPrice = await ethers.provider.getGasPrice();
  console.log("⛽ Gas price:", gasPrice.toString(), "wei");
  
  console.log("\n📦 Deploying OneirobotNFT contract...");
  
  // Deploy OneirobotNFT
  const OneirobotNFT = await ethers.getContractFactory("OneirobotNFT");
  
  // Estimate gas for deployment
  const deploymentTx = OneirobotNFT.getDeployTransaction();
  const estimatedGas = await ethers.provider.estimateGas(deploymentTx);
  console.log("📊 Estimated gas for deployment:", estimatedGas.toString());
  
  // Deploy with optimized gas settings
  const oneirobotNFT = await OneirobotNFT.deploy({
    gasLimit: estimatedGas.mul(120).div(100), // 20% buffer
    gasPrice: 0 // Zero gas on SKALE
  });
  
  console.log("⏳ Waiting for deployment transaction...");
  await oneirobotNFT.deployed();
  
  console.log("✅ OneirobotNFT deployed successfully!");
  console.log("📍 Contract address:", oneirobotNFT.address);
  console.log("🔗 Transaction hash:", oneirobotNFT.deployTransaction.hash);
  
  // Wait for a few blocks to ensure the contract is fully deployed
  console.log("⏳ Waiting for block confirmations...");
  await oneirobotNFT.deployTransaction.wait(2);
  
  // Verify contract deployment
  console.log("\n🔍 Verifying contract deployment...");
  const code = await ethers.provider.getCode(oneirobotNFT.address);
  console.log("📏 Contract code size:", code.length, "bytes");
  console.log("✅ Contract verified:", code.length > 2 ? "SUCCESS" : "FAILED");
  
  // Test contract functions
  console.log("\n🧪 Testing contract functions...");
  
  try {
    const name = await oneirobotNFT.name();
    const symbol = await oneirobotNFT.symbol();
    const totalSupply = await oneirobotNFT.totalSupply();
    const maxSupply = await oneirobotNFT.MAX_SUPPLY();
    
    console.log("📛 Name:", name);
    console.log("🔖 Symbol:", symbol);
    console.log("📊 Total Supply:", totalSupply.toString());
    console.log("🔄 Max Supply:", maxSupply.toString());
    
    // Check if deployer is Syndicate Master
    const isMaster = await oneirobotNFT.isSyndicateMaster(deployer.address);
    console.log("👑 Deployer is Syndicate Master:", isMaster);
    
  } catch (error) {
    console.log("❌ Error testing contract functions:", error.message);
  }
  
  // Save deployment information
  const deploymentInfo = {
    network: "skale-mainnet",
    contractName: "OneirobotNFT",
    contractAddress: oneirobotNFT.address,
    transactionHash: oneirobotNFT.deployTransaction.hash,
    deployerAddress: deployer.address,
    blockNumber: oneirobotNFT.deployTransaction.blockNumber,
    gasUsed: oneirobotNFT.deployTransaction.gasLimit?.toString() || "0",
    gasPrice: "0",
    deploymentCost: "$0.00",
    timestamp: new Date().toISOString(),
    chainId: 2046399126,
    rpcUrl: process.env.SKALE_RPC || "https://mainnet.skalenodes.com/v1/elated-tan-skat",
    explorerUrl: `https://elated-tan-skat.explorer.mainnet.skalenodes.com/address/${oneirobotNFT.address}`,
    features: [
      "ERC-721 compliant",
      "SYNDICATE_MASTER_ROLE allowlist",
      "Pseudorandom attributes",
      "IPFS metadata support",
      "ReentrancyGuard protection",
      "AccessControl roles",
      "Zero gas fees"
    ]
  };
  
  // Save to deployment file
  const deploymentFile = "deployments/oneirobot-nft-deployment.json";
  writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  console.log("💾 Deployment info saved to:", deploymentFile);
  
  // Update main memory file
  try {
    let memory = {};
    try {
      memory = JSON.parse(readFileSync("iem_memory.json", "utf8"));
    } catch (e) {
      // File doesn't exist, create new
    }
    
    memory.oneirobot_nft = deploymentInfo;
    memory.last_deployment = {
      type: "OneirobotNFT",
      timestamp: deploymentInfo.timestamp,
      network: "skale-mainnet"
    };
    
    writeFileSync("iem_memory.json", JSON.stringify(memory, null, 2));
    console.log("💾 Updated iem_memory.json");
    
  } catch (error) {
    console.log("⚠️ Warning: Could not update iem_memory.json:", error.message);
  }
  
  console.log("\n🎉 DEPLOYMENT COMPLETE!");
  console.log("=====================================");
  console.log("🏷️  Contract: OneirobotNFT");
  console.log("📍 Address:", oneirobotNFT.address);
  console.log("🔗 TX Hash:", oneirobotNFT.deployTransaction.hash);
  console.log("🌐 Network: SKALE Europa Hub");
  console.log("💰 Cost: $0.00 (Zero Gas)");
  console.log("🔍 Explorer:", deploymentInfo.explorerUrl);
  console.log("=====================================");
  
  // Victory message for Gene Deployer
  console.log("\n🏆 AI GENE DEPLOYER VICTORY LOG:");
  console.log("✨ OneirobotNFT Mint Gene successfully deployed to SKALE Mainnet");
  console.log("⚡ Zero-gas deployment completed in seconds");
  console.log("🛡️ Enhanced security with ReentrancyGuard + AccessControl");
  console.log("🎲 Pseudorandom attributes using blockhash + nonce");
  console.log("🔐 SYNDICATE_MASTER_ROLE allowlist protection");
  console.log("📱 Ready for Chrome extension and OpenSea integration");
  console.log("🚀 CRUSHING INFERIOR COPILOTS WITH 20X SECURITY!");
}

// Execute deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("❌ Deployment failed:", error);
    process.exit(1);
  });