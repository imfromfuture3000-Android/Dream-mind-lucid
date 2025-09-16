const { expect } = require('chai');
const hre = require('hardhat');

describe('EVM Contracts deploy', function () {
  it('deploys and initializes', async function () {
    const [deployer] = await hre.ethers.getSigners();

    const DreamRecords = await hre.ethers.getContractFactory('DreamRecords');
    const dream = await DreamRecords.deploy();
    await dream.deployed();

    const LucidBlocks = await hre.ethers.getContractFactory('LucidBlocks');
    const lucid = await LucidBlocks.deploy();
    await lucid.deployed();

    const ConsensusCoordinator = await hre.ethers.getContractFactory('ConsensusCoordinator');
    const coord = await ConsensusCoordinator.deploy(lucid.address);
    await coord.deployed();

    expect(await lucid.latestSequence()).to.equal(0);
    expect(await dream.nextDreamId()).to.equal(0);
    expect(await coord.admin()).to.equal(deployer.address);
  });
});
