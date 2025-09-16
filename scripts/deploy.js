const { ethers } = require("hardhat");

async function main() {
    console.log("Starting Dream ecosystem deployment...");
    
    // Get the deployer account
    const [deployer] = await ethers.getSigners();
    console.log("Deploying contracts with account:", deployer.address);
    
    // Get contract factories
    const DreamToken = await ethers.getContractFactory("DreamToken");
    const SMindToken = await ethers.getContractFactory("SMindToken");
    const LucidToken = await ethers.getContractFactory("LucidToken");
    const DreamEconomicEngine = await ethers.getContractFactory("DreamEconomicEngine");
    const DreamStaking = await ethers.getContractFactory("DreamStaking");
    const DreamPerformanceDistributor = await ethers.getContractFactory("DreamPerformanceDistributor");
    
    console.log("Deploying tokens...");
    
    // Deploy tokens
    const dreamToken = await DreamToken.deploy(
        ethers.utils.parseEther(process.env.DREAM_TOTAL_SUPPLY.toString())
    );
    await dreamToken.deployed();
    console.log("DREAM Token deployed to:", dreamToken.address);
    
    const smindToken = await SMindToken.deploy(
        ethers.utils.parseEther(process.env.SMIND_TOTAL_SUPPLY.toString())
    );
    await smindToken.deployed();
    console.log("SMIND Token deployed to:", smindToken.address);
    
    const lucidToken = await LucidToken.deploy(
        ethers.utils.parseEther(process.env.LUCID_TOTAL_SUPPLY.toString())
    );
    await lucidToken.deployed();
    console.log("LUCID Token deployed to:", lucidToken.address);
    
    console.log("Deploying economic engine...");
    
    // Deploy economic engine with price feeds
    const economicEngine = await DreamEconomicEngine.deploy(
        process.env.CHAINLINK_COORDINATOR,
        dreamToken.address,
        smindToken.address,
        lucidToken.address
    );
    await economicEngine.deployed();
    console.log("Economic Engine deployed to:", economicEngine.address);
    
    console.log("Deploying staking contract...");
    
    // Deploy staking contract
    const staking = await DreamStaking.deploy(
        dreamToken.address,
        smindToken.address,
        lucidToken.address,
        economicEngine.address
    );
    await staking.deployed();
    console.log("Staking Contract deployed to:", staking.address);
    
    console.log("Deploying performance distributor...");
    
    // Deploy performance distributor
    const distributor = await DreamPerformanceDistributor.deploy(
        dreamToken.address,
        smindToken.address,
        lucidToken.address,
        economicEngine.address,
        staking.address
    );
    await distributor.deployed();
    console.log("Performance Distributor deployed to:", distributor.address);
    
    console.log("Configuring contracts...");
    
    // Configure economic engine parameters
    await economicEngine.updateEconomicParams({
        baseRewardRate: process.env.BASE_REWARD_RATE,
        burnRateMin: process.env.BURN_RATE_MIN,
        burnRateMax: process.env.BURN_RATE_MAX,
        stakingWeight: process.env.STAKING_WEIGHT,
        performanceWeight: process.env.PERFORMANCE_WEIGHT
    });
    
    // Configure staking parameters
    await staking.updateRewardRate(dreamToken.address, process.env.BASE_REWARD_RATE);
    await staking.updateRewardRate(smindToken.address, process.env.BASE_REWARD_RATE);
    await staking.updateRewardRate(lucidToken.address, process.env.BASE_REWARD_RATE);
    
    // Transfer ownership of tokens to distributor
    await dreamToken.transferOwnership(distributor.address);
    await smindToken.transferOwnership(distributor.address);
    await lucidToken.transferOwnership(distributor.address);
    
    console.log("Setting up initial token distribution...");
    
    // Transfer initial token supplies
    const treasury = process.env.TREASURY_ADDRESS;
    
    await dreamToken.transfer(treasury, ethers.utils.parseEther("100000000")); // Initial treasury allocation
    await smindToken.transfer(treasury, ethers.utils.parseEther("100000000"));
    await lucidToken.transfer(treasury, ethers.utils.parseEther("50000000"));
    
    await dreamToken.transfer(staking.address, ethers.utils.parseEther("200000000")); // Staking rewards
    await smindToken.transfer(staking.address, ethers.utils.parseEther("200000000"));
    await lucidToken.transfer(staking.address, ethers.utils.parseEther("100000000"));
    
    console.log("Deployment complete!");
    console.log({
        dreamToken: dreamToken.address,
        smindToken: smindToken.address,
        lucidToken: lucidToken.address,
        economicEngine: economicEngine.address,
        staking: staking.address,
        distributor: distributor.address
    });
    
    // Verify contracts on block explorer (if supported)
    if (process.env.VERIFY_CONTRACTS) {
        console.log("Verifying contracts...");
        try {
            await hre.run("verify:verify", {
                address: dreamToken.address,
                constructorArguments: [ethers.utils.parseEther(process.env.DREAM_TOTAL_SUPPLY.toString())]
            });
            
            await hre.run("verify:verify", {
                address: smindToken.address,
                constructorArguments: [ethers.utils.parseEther(process.env.SMIND_TOTAL_SUPPLY.toString())]
            });
            
            await hre.run("verify:verify", {
                address: lucidToken.address,
                constructorArguments: [ethers.utils.parseEther(process.env.LUCID_TOTAL_SUPPLY.toString())]
            });
            
            await hre.run("verify:verify", {
                address: economicEngine.address,
                constructorArguments: [
                    process.env.CHAINLINK_COORDINATOR,
                    dreamToken.address,
                    smindToken.address,
                    lucidToken.address
                ]
            });
            
            await hre.run("verify:verify", {
                address: staking.address,
                constructorArguments: [
                    dreamToken.address,
                    smindToken.address,
                    lucidToken.address,
                    economicEngine.address
                ]
            });
            
            await hre.run("verify:verify", {
                address: distributor.address,
                constructorArguments: [
                    dreamToken.address,
                    smindToken.address,
                    lucidToken.address,
                    economicEngine.address,
                    staking.address
                ]
            });
            
            console.log("Contract verification complete!");
        } catch (error) {
            console.error("Error verifying contracts:", error);
        }
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
