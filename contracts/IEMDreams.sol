// contracts/IEMDreams.sol
// Copilot: Enhance this to include basic DREAM token and dream recording
pragma solidity ^0.8.20;

contract IEMDreams {
    string public name = "IEM Dreams";
    uint256 public totalSupply = 777777777 * 10**18; // 777,777,777 DREAM tokens
    mapping(address => uint256) public balances;

    event DreamRecorded(address indexed dreamer, string dream);
    event TokensMinted(address indexed to, uint256 amount);

    constructor() {
        balances[msg.sender] = totalSupply; // Creator gets all tokens initially
    }

    // Record a dream and mint 10 DREAM tokens as reward
    function recordDream(string memory dream) public {
        require(balances[msg.sender] >= 10 * 10**18, "Not enough DREAM to record");
        balances[msg.sender] -= 10 * 10**18;
        emit DreamRecorded(msg.sender, dream);
        // Copilot: Add transfer logic for reward distribution later
    }

    // Check balance (for testing)
    function balanceOf(address account) public view returns (uint256) {
        return balances[account];
    }
}
