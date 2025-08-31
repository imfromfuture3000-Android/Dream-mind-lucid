// SPDX-License-Identifier: MIT
// contracts/OneiroSphere.sol - Quantum Dream Network Interface
pragma solidity ^0.8.20;

interface IERC20 {
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
}

contract OneiroSphere {
    // Token contracts
    IERC20 public immutable smindToken; // SMIND for staking governance
    IERC20 public immutable lucidToken; // LUCID for oracle access
    
    // Contract metadata
    string public name = "OneiroSphere";
    string public version = "1.0.0";
    address public immutable owner;
    
    // Quantum dream network
    struct QuantumDream {
        string ipfsHash;
        address dreamer;
        uint256 timestamp;
        uint256 coherenceScore;
        uint256 noveltyScore;
        uint256 emotionScore;
        bool validated;
        uint256 lucidGateAccess;
    }
    
    struct MindNode {
        address operator;
        uint256 smindStaked;
        uint256 validationCount;
        uint256 accuracy;
        bool active;
        uint256 rewards;
    }
    
    struct LucidGate {
        string name;
        uint256 accessCost; // LUCID tokens required
        bool active;
        mapping(address => bool) hasAccess;
        mapping(address => uint256) lastAccess;
    }
    
    // Storage
    mapping(bytes32 => QuantumDream) public dreams;
    mapping(address => MindNode) public mindNodes;
    mapping(uint256 => LucidGate) public lucidGates;
    mapping(address => string[]) public userDreamHashes;
    mapping(address => uint256) public oracleCredits;
    
    uint256 public dreamCount;
    uint256 public activeNodes;
    uint256 public totalSmindStaked;
    uint256 public gateCount;
    
    // Constants
    uint256 constant MIN_SMIND_STAKE = 1000 * 10**18; // 1000 SMIND minimum
    uint256 constant MIN_LUCID_ACCESS = 10 * 10**18;  // 10 LUCID minimum
    uint256 constant VALIDATION_REWARD = 5 * 10**18;  // 5 SMIND per validation
    uint256 constant COHERENCE_THRESHOLD = 70;
    uint256 constant NOVELTY_THRESHOLD = 60;
    uint256 constant EMOTION_THRESHOLD = 50;
    
    // Events
    event DreamInterfaced(address indexed dreamer, string ipfsHash, bytes32 indexed dreamId);
    event DreamValidated(bytes32 indexed dreamId, address indexed validator, bool approved);
    event MindNodeRegistered(address indexed operator, uint256 smindStaked);
    event MindNodeDeactivated(address indexed operator);
    event LucidGateCreated(uint256 indexed gateId, string name, uint256 accessCost);
    event LucidGateAccessed(uint256 indexed gateId, address indexed user, uint256 timestamp);
    event OraclePrediction(address indexed user, string query, string response, uint256 cost);
    event RewardsDistributed(address indexed recipient, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    modifier onlyActiveMindNode() {
        require(mindNodes[msg.sender].active, "Not active MindNode");
        _;
    }

    constructor(address _owner, address _smindToken, address _lucidToken) {
        owner = _owner;
        smindToken = IERC20(_smindToken);
        lucidToken = IERC20(_lucidToken);
        
        // Create initial Lucid Gates
        _createLucidGate("Reality Gate Alpha", 100 * 10**18);
        _createLucidGate("Temporal Nexus", 250 * 10**18);
        _createLucidGate("Consciousness Bridge", 500 * 10**18);
    }

    // Quantum Dream Interface Functions
    function interfaceDream(string memory ipfsHash, uint256 coherence, uint256 novelty, uint256 emotion) public {
        require(bytes(ipfsHash).length > 0, "IPFS hash required");
        require(coherence <= 100 && novelty <= 100 && emotion <= 100, "Scores must be 0-100");
        
        bytes32 dreamId = keccak256(abi.encodePacked(ipfsHash, msg.sender, block.timestamp));
        require(dreams[dreamId].timestamp == 0, "Dream already exists");
        
        dreams[dreamId] = QuantumDream({
            ipfsHash: ipfsHash,
            dreamer: msg.sender,
            timestamp: block.timestamp,
            coherenceScore: coherence,
            noveltyScore: novelty,
            emotionScore: emotion,
            validated: false,
            lucidGateAccess: 0
        });
        
        userDreamHashes[msg.sender].push(ipfsHash);
        dreamCount++;
        
        emit DreamInterfaced(msg.sender, ipfsHash, dreamId);
    }

    // MindNode Registration and Management
    function registerMindNode(uint256 smindAmount) public {
        require(smindAmount >= MIN_SMIND_STAKE, "Insufficient SMIND stake");
        require(!mindNodes[msg.sender].active, "Already registered");
        require(smindToken.transferFrom(msg.sender, address(this), smindAmount), "SMIND transfer failed");
        
        mindNodes[msg.sender] = MindNode({
            operator: msg.sender,
            smindStaked: smindAmount,
            validationCount: 0,
            accuracy: 100, // Start with perfect accuracy
            active: true,
            rewards: 0
        });
        
        totalSmindStaked += smindAmount;
        activeNodes++;
        
        emit MindNodeRegistered(msg.sender, smindAmount);
    }

    function validateDream(bytes32 dreamId, bool approve) public onlyActiveMindNode {
        require(dreams[dreamId].timestamp > 0, "Dream does not exist");
        require(!dreams[dreamId].validated, "Dream already validated");
        
        QuantumDream storage dream = dreams[dreamId];
        
        if (approve) {
            // Check if dream meets quality thresholds
            bool qualityCheck = dream.coherenceScore >= COHERENCE_THRESHOLD &&
                               dream.noveltyScore >= NOVELTY_THRESHOLD &&
                               dream.emotionScore >= EMOTION_THRESHOLD;
                               
            if (qualityCheck) {
                dream.validated = true;
                dream.lucidGateAccess = _calculateGateAccess(dream);
                
                // Reward the validator
                mindNodes[msg.sender].rewards += VALIDATION_REWARD;
                mindNodes[msg.sender].validationCount++;
            }
        }
        
        emit DreamValidated(dreamId, msg.sender, approve);
    }

    function _calculateGateAccess(QuantumDream memory dream) internal pure returns (uint256) {
        uint256 totalScore = dream.coherenceScore + dream.noveltyScore + dream.emotionScore;
        
        if (totalScore >= 270) return 3; // Access to all gates
        if (totalScore >= 220) return 2; // Access to Reality Gate Alpha and Temporal Nexus
        if (totalScore >= 180) return 1; // Access to Reality Gate Alpha only
        return 0; // No gate access
    }

    // Lucid Gate Management
    function _createLucidGate(string memory gateName, uint256 accessCost) internal {
        LucidGate storage gate = lucidGates[gateCount];
        gate.name = gateName;
        gate.accessCost = accessCost;
        gate.active = true;
        
        gateCount++;
        emit LucidGateCreated(gateCount - 1, gateName, accessCost);
    }

    function accessLucidGate(uint256 gateId) public {
        require(gateId < gateCount, "Gate does not exist");
        require(lucidGates[gateId].active, "Gate inactive");
        
        LucidGate storage gate = lucidGates[gateId];
        require(lucidToken.transferFrom(msg.sender, address(this), gate.accessCost), "LUCID payment failed");
        
        gate.hasAccess[msg.sender] = true;
        gate.lastAccess[msg.sender] = block.timestamp;
        oracleCredits[msg.sender] += gate.accessCost / 10; // 10% of cost as oracle credits
        
        emit LucidGateAccessed(gateId, msg.sender, block.timestamp);
    }

    function hasGateAccess(uint256 gateId, address user) public view returns (bool) {
        return lucidGates[gateId].hasAccess[user];
    }

    // Oracle Prediction System
    function requestOraclePrediction(string memory query, uint256 lucidCost) public {
        require(oracleCredits[msg.sender] >= lucidCost, "Insufficient oracle credits");
        require(bytes(query).length > 0, "Query cannot be empty");
        
        oracleCredits[msg.sender] -= lucidCost;
        
        // In a real implementation, this would interface with an AI oracle
        string memory response = "Quantum prediction processing...";
        
        emit OraclePrediction(msg.sender, query, response, lucidCost);
    }

    // Yield and Rewards
    function claimMindNodeRewards() public {
        require(mindNodes[msg.sender].active, "Not active MindNode");
        uint256 rewards = mindNodes[msg.sender].rewards;
        require(rewards > 0, "No rewards to claim");
        
        mindNodes[msg.sender].rewards = 0;
        require(smindToken.transfer(msg.sender, rewards), "Reward transfer failed");
        
        emit RewardsDistributed(msg.sender, rewards);
    }

    function deactivateMindNode() public {
        require(mindNodes[msg.sender].active, "Not active");
        
        uint256 stakedAmount = mindNodes[msg.sender].smindStaked;
        uint256 rewards = mindNodes[msg.sender].rewards;
        
        mindNodes[msg.sender].active = false;
        totalSmindStaked -= stakedAmount;
        activeNodes--;
        
        if (stakedAmount > 0) {
            require(smindToken.transfer(msg.sender, stakedAmount), "Stake return failed");
        }
        if (rewards > 0) {
            require(smindToken.transfer(msg.sender, rewards), "Reward transfer failed");
        }
        
        emit MindNodeDeactivated(msg.sender);
    }

    // View Functions
    function getDream(bytes32 dreamId) public view returns (
        string memory ipfsHash,
        address dreamer,
        uint256 timestamp,
        uint256 coherenceScore,
        uint256 noveltyScore,
        uint256 emotionScore,
        bool validated,
        uint256 lucidGateAccess
    ) {
        QuantumDream storage dream = dreams[dreamId];
        return (
            dream.ipfsHash,
            dream.dreamer,
            dream.timestamp,
            dream.coherenceScore,
            dream.noveltyScore,
            dream.emotionScore,
            dream.validated,
            dream.lucidGateAccess
        );
    }

    function getUserDreams(address user) public view returns (string[] memory) {
        return userDreamHashes[user];
    }

    function getMindNodeInfo(address operator) public view returns (
        uint256 smindStaked,
        uint256 validationCount,
        uint256 accuracy,
        bool active,
        uint256 rewards
    ) {
        MindNode storage node = mindNodes[operator];
        return (node.smindStaked, node.validationCount, node.accuracy, node.active, node.rewards);
    }

    function getLucidGateInfo(uint256 gateId) public view returns (
        string memory gateName,
        uint256 accessCost,
        bool active
    ) {
        require(gateId < gateCount, "Gate does not exist");
        LucidGate storage gate = lucidGates[gateId];
        return (gate.name, gate.accessCost, gate.active);
    }

    function getNetworkStats() public view returns (
        uint256 totalDreams,
        uint256 activeMindNodes,
        uint256 totalStaked,
        uint256 totalGates
    ) {
        return (dreamCount, activeNodes, totalSmindStaked, gateCount);
    }

    // Admin Functions
    function setGateStatus(uint256 gateId, bool active) public onlyOwner {
        require(gateId < gateCount, "Gate does not exist");
        lucidGates[gateId].active = active;
    }

    function createLucidGate(string memory gateName, uint256 accessCost) public onlyOwner {
        _createLucidGate(gateName, accessCost);
    }

    function emergencyWithdraw() public onlyOwner {
        uint256 smindBalance = smindToken.balanceOf(address(this));
        uint256 lucidBalance = lucidToken.balanceOf(address(this));
        
        if (smindBalance > 0) {
            smindToken.transfer(owner, smindBalance);
        }
        if (lucidBalance > 0) {
            lucidToken.transfer(owner, lucidBalance);
        }
    }
}