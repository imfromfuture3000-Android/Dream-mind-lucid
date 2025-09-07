const hre = require('hardhat');

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log('Deploying contracts with account:', deployer.address);

  const DreamRecords = await hre.ethers.getContractFactory('DreamRecords');
  const dream = await DreamRecords.deploy();
  await dream.deployed();
  console.log('DreamRecords deployed to:', dream.address);

  const LucidBlocks = await hre.ethers.getContractFactory('LucidBlocks');
  const lucid = await LucidBlocks.deploy();
  await lucid.deployed();
  console.log('LucidBlocks deployed to:', lucid.address);

  const BLSVerifier = await hre.ethers.getContractFactory('BLSVerifier');
  const bls = await BLSVerifier.deploy();
  await bls.deployed();
  console.log('BLSVerifier deployed to:', bls.address);

  const ConsensusCoordinator = await hre.ethers.getContractFactory('ConsensusCoordinator');
  const coord = await ConsensusCoordinator.deploy(lucid.address, bls.address);
  await coord.deployed();
  console.log('ConsensusCoordinator deployed to:', coord.address);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
