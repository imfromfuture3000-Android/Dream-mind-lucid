const { ethers } = require("hardhat");
const fs = require('fs');

async function main() {
  console.log("🔵 Deploying Dream-Mind-Lucid contracts to SKALE...");
  
  const [deployer] = await ethers.getSigners();
  console.log("🔑 Deploying with account:", deployer.address);
  
  // Get deployer balance
  const balance = await deployer.provider.getBalance(deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(balance), "ETH");
  
  const deploymentResults = {
    timestamp: new Date().toISOString(),
    deployer: deployer.address,
    network: hre.network.name,
    contracts: {}
  };
  
  try {
    // Deploy DreamBridge
    console.log("\n🌉 Deploying DreamBridge...");
    const DreamBridge = await ethers.getContractFactory("DreamBridge");
    const dreamBridge = await DreamBridge.deploy(
      "Wrapped DREAM",
      "wDREAM", 
      deployer.address
    );
    
    await dreamBridge.waitForDeployment();
    const dreamBridgeAddress = await dreamBridge.getAddress();
    
    console.log("✅ DreamBridge deployed to:", dreamBridgeAddress);
    
    deploymentResults.contracts.DreamBridge = {
      address: dreamBridgeAddress,
      name: "Wrapped DREAM",
      symbol: "wDREAM",
      type: "ERC20 Bridge"
    };
    
    // Deploy OneiroSphereV2
    console.log("\n🌌 Deploying OneiroSphereV2...");
    const OneiroSphereV2 = await ethers.getContractFactory("OneiroSphereV2");
    const oneiroSphere = await OneiroSphereV2.deploy(
      deployer.address,
      dreamBridgeAddress
    );
    
    await oneiroSphere.waitForDeployment();
    const oneiroSphereAddress = await oneiroSphere.getAddress();
    
    console.log("✅ OneiroSphereV2 deployed to:", oneiroSphereAddress);
    
    deploymentResults.contracts.OneiroSphereV2 = {
      address: oneiroSphereAddress,
      name: "OneiroSphere V2",
      type: "Dream Interface",
      bridgeToken: dreamBridgeAddress
    };
    
    // Setup bridge authorization
    console.log("\n🔗 Configuring bridge...");
    const authTx = await dreamBridge.authorizeRelayer(oneiroSphereAddress);
    await authTx.wait();
    console.log("✅ OneiroSphere authorized as bridge relayer");
    
    // Set reward rate
    console.log("\n⚙️ Configuring yield parameters...");
    const rewardRate = ethers.parseEther("1"); // 1 DREAM per second
    const rewardTx = await oneiroSphere.setRewardRate(rewardRate);
    await rewardTx.wait();
    console.log("✅ Reward rate set to 1 DREAM/second");
    
    // Emergency mint some tokens for initial liquidity
    console.log("\n💧 Minting initial liquidity...");
    const liquidityAmount = ethers.parseEther("10000"); // 10,000 DREAM
    const mintTx = await dreamBridge.emergencyMint(deployer.address, liquidityAmount);
    await mintTx.wait();
    console.log("✅ Initial liquidity minted:", ethers.formatEther(liquidityAmount), "DREAM");
    
    deploymentResults.initialLiquidity = ethers.formatEther(liquidityAmount);
    deploymentResults.status = "success";
    
    // Save deployment results
    fs.writeFileSync(
      'skale_deployment_results.json',
      JSON.stringify(deploymentResults, null, 2)
    );
    
    console.log("\n🎉 SKALE deployment completed successfully!");
    console.log("📁 Results saved to: skale_deployment_results.json");
    
    // Output for script consumption
    console.log(`\nDreamBridge deployed to: ${dreamBridgeAddress}`);
    console.log(`OneiroSphereV2 deployed to: ${oneiroSphereAddress}`);
    
  } catch (error) {
    console.error("❌ Deployment failed:", error);
    
    deploymentResults.status = "failed";
    deploymentResults.error = error.message;
    
    fs.writeFileSync(
      'skale_deployment_results.json',
      JSON.stringify(deploymentResults, null, 2)
    );
    
    process.exit(1);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });