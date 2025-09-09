// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts-upgradeable/access/AccessControlUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/PausableUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";
import "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/CountersUpgradeable.sol";
import "./interfaces/IDreamGovernance.sol";
import "./interfaces/ILucidAccess.sol";
import "./interfaces/IDreamToken.sol";

/**
 * @title OneiroSphere - The Quantum Dream Network (Next Generation)
 * @dev Upgradeable quantum dream interfacing system with enhanced security and governance
 * @notice Core smart contract for The Oneiro-Sphere ecosystem with LUCID token access control
 * 
 * Key Features:
 * - IPFS-based dream storage with quantum validation
 * - LUCID token-based access control and tiering
 * - Meta-transaction support for gasless operations
 * - DAO governance integration with timelock mechanisms
 * - Dream analytics and cognitive pattern recognition
 * - Upgradeable architecture for future quantum enhancements
 * - SKALE network optimization (zero-gas transactions)
 * - Advanced security patterns and emergency controls
 */
contract OneiroSphere is
    Initializable,
    AccessControlUpgradeable,
    PausableUpgradeable,
    ReentrancyGuardUpgradeable,
    UUPSUpgradeable
{
    using CountersUpgradeable for CountersUpgradeable.Counter;

    // ============ Constants ============
    
    /// @notice Maximum dream size in bytes (prevents spam and ensures IPFS efficiency)
    uint256 public constant MAX_DREAM_SIZE = 10 * 1024 * 1024; // 10MB
    
    /// @notice Maximum dreams per user per day (default limit)
    uint256 public constant DEFAULT_DAILY_DREAM_LIMIT = 10;
    
    /// @notice Minimum IPFS hash length
    uint256 public constant MIN_IPFS_HASH_LENGTH = 32;
    
    /// @notice Maximum IPFS hash length
    uint256 public constant MAX_IPFS_HASH_LENGTH = 64;

    // ============ Roles ============
    
    /// @notice Role for quantum validators
    bytes32 public constant QUANTUM_VALIDATOR_ROLE = keccak256("QUANTUM_VALIDATOR_ROLE");
    
    /// @notice Role for governance operations
    bytes32 public constant GOVERNANCE_ROLE = keccak256("GOVERNANCE_ROLE");
    
    /// @notice Role for emergency operations
    bytes32 public constant EMERGENCY_ROLE = keccak256("EMERGENCY_ROLE");
    
    /// @notice Role for analytics and pattern recognition
    bytes32 public constant ANALYTICS_ROLE = keccak256("ANALYTICS_ROLE");
    
    /// @notice Role for trusted forwarders (meta-transactions)
    bytes32 public constant TRUSTED_FORWARDER_ROLE = keccak256("TRUSTED_FORWARDER_ROLE");

    // ============ Structs ============
    
    /**
     * @notice Structure representing a quantum dream
     * @param dreamId Unique dream identifier
     * @param dreamer Address of the dreamer
     * @param ipfsHash IPFS hash of the dream content
     * @param timestamp Block timestamp when dream was recorded
     * @param blockNumber Block number when dream was recorded
     * @param dreamSize Size of the dream data in bytes
     * @param quantumSignature Quantum validation signature
     * @param accessTier Access tier of the dreamer at time of recording
     * @param validated Whether the dream has been quantum validated
     * @param cognitivePattern Identified cognitive pattern (ML/AI classification)
     * @param metadata Additional metadata hash
     */
    struct QuantumDream {
        uint256 dreamId;
        address dreamer;
        string ipfsHash;
        uint256 timestamp;
        uint256 blockNumber;
        uint256 dreamSize;
        bytes32 quantumSignature;
        uint256 accessTier;
        bool validated;
        uint256 cognitivePattern;
        bytes32 metadata;
    }

    /**
     * @notice Structure for dream analytics
     * @param totalDreams Total number of dreams in the system
     * @param validatedDreams Number of quantum-validated dreams
     * @param totalDreamers Number of unique dreamers
     * @param averageDreamSize Average size of dreams
     * @param cognitivePatterns Array of identified cognitive patterns
     * @param lastUpdateBlock Last block when analytics were updated
     */
    struct DreamAnalytics {
        uint256 totalDreams;
        uint256 validatedDreams;
        uint256 totalDreamers;
        uint256 averageDreamSize;
        uint256[] cognitivePatterns;
        uint256 lastUpdateBlock;
    }

    // ============ State Variables ============
    
    /// @notice Counter for unique dream IDs
    CountersUpgradeable.Counter private _dreamIdCounter;
    
    /// @notice Address of the LUCID access control contract
    ILucidAccess public lucidAccessContract;
    
    /// @notice Address of the governance contract
    IDreamGovernance public governanceContract;
    
    /// @notice Address of the DREAM token contract
    IDreamToken public dreamTokenContract;
    
    /// @notice Current trusted forwarder for meta-transactions
    address public trustedForwarder;
    
    /// @notice Global dream analytics
    DreamAnalytics public dreamAnalytics;

    // ============ Mappings ============
    
    /// @notice Mapping of dream ID to QuantumDream
    mapping(uint256 => QuantumDream) public dreams;
    
    /// @notice Mapping of dreamer to their dream IDs
    mapping(address => uint256[]) public dreamerToDreams;
    
    /// @notice Mapping of IPFS hash to dream ID (prevents duplicates)
    mapping(string => uint256) public ipfsHashToDreamId;
    
    /// @notice Mapping of dreamer to daily dream count (resets daily)
    mapping(address => mapping(uint256 => uint256)) public dailyDreamCount; // dreamer => day => count
    
    /// @notice Mapping of cognitive pattern to dream IDs
    mapping(uint256 => uint256[]) public cognitivePatternToDreams;
    
    /// @notice Mapping of dreamer to total storage used
    mapping(address => uint256) public dreamerStorageUsed;
    
    /// @notice Mapping of quantum validators to their validation count
    mapping(address => uint256) public validatorStats;

    // ============ Events ============
    
    /**
     * @notice Emitted when a dream is interfaced with the quantum network
     * @param dreamId The unique dream ID
     * @param dreamer The address that recorded the dream
     * @param ipfsHash The IPFS hash of the dream content
     * @param dreamSize The size of the dream data
     * @param accessTier The access tier of the dreamer
     */
    event DreamInterfaced(
        uint256 indexed dreamId,
        address indexed dreamer,
        string ipfsHash,
        uint256 dreamSize,
        uint256 accessTier
    );

    /**
     * @notice Emitted when a dream is quantum validated
     * @param dreamId The dream ID that was validated
     * @param validator The address that performed the validation
     * @param quantumSignature The quantum signature
     * @param cognitivePattern The identified cognitive pattern
     */
    event QuantumDreamValidated(
        uint256 indexed dreamId,
        address indexed validator,
        bytes32 quantumSignature,
        uint256 cognitivePattern
    );

    /**
     * @notice Emitted when system parameters are updated
     * @param parameterName The name of the updated parameter
     * @param oldValue The old value
     * @param newValue The new value
     * @param updatedBy The address that made the update
     */
    event SystemParameterUpdated(
        string parameterName,
        uint256 oldValue,
        uint256 newValue,
        address indexed updatedBy
    );

    /**
     * @notice Emitted when dream analytics are updated
     * @param totalDreams Total dreams in the system
     * @param validatedDreams Number of validated dreams
     * @param totalDreamers Number of unique dreamers
     * @param updateBlock Block number of the update
     */
    event DreamAnalyticsUpdated(
        uint256 totalDreams,
        uint256 validatedDreams,
        uint256 totalDreamers,
        uint256 updateBlock
    );

    /**
     * @notice Emitted when a cognitive pattern is identified
     * @param dreamId The dream ID where pattern was found
     * @param pattern The pattern identifier
     * @param confidence The confidence level (0-100)
     * @param analyzer The address that identified the pattern
     */
    event CognitivePatternIdentified(
        uint256 indexed dreamId,
        uint256 indexed pattern,
        uint256 confidence,
        address indexed analyzer
    );

    // ============ Modifiers ============
    
    /// @notice Restricts access based on LUCID token requirements
    modifier requiresLucidAccess(bytes32 feature, uint256 dreamSize) {
        if (address(lucidAccessContract) != address(0)) {
            (bool canAccess, string memory reason) = lucidAccessContract.canRecordDream(_msgSender(), dreamSize);
            require(canAccess, string(abi.encodePacked("OneiroSphere: ", reason)));
            require(lucidAccessContract.hasAccess(_msgSender(), feature), "OneiroSphere: Insufficient LUCID access");
        }
        _;
    }

    /// @notice Validates IPFS hash format
    modifier validIpfsHash(string memory ipfsHash) {
        bytes memory hashBytes = bytes(ipfsHash);
        require(hashBytes.length >= MIN_IPFS_HASH_LENGTH, "OneiroSphere: IPFS hash too short");
        require(hashBytes.length <= MAX_IPFS_HASH_LENGTH, "OneiroSphere: IPFS hash too long");
        require(ipfsHashToDreamId[ipfsHash] == 0, "OneiroSphere: Dream already exists");
        _;
    }

    // ============ Initialization ============
    
    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    /**
     * @notice Initializes the OneiroSphere contract
     * @param initialOwner The initial owner and admin
     * @param trustedForwarderAddr The address of the trusted forwarder for meta-transactions
     * @param lucidAccessAddr The address of the LUCID access control contract
     * @param governanceAddr The address of the governance contract
     * @param dreamTokenAddr The address of the DREAM token contract
     */
    function initialize(
        address initialOwner,
        address trustedForwarderAddr,
        address lucidAccessAddr,
        address governanceAddr,
        address dreamTokenAddr
    ) public initializer {
        __AccessControl_init();
        __Pausable_init();
        __ReentrancyGuard_init();
        __UUPSUpgradeable_init();

        // Grant roles to initial owner
        _grantRole(DEFAULT_ADMIN_ROLE, initialOwner);
        _grantRole(GOVERNANCE_ROLE, initialOwner);
        _grantRole(EMERGENCY_ROLE, initialOwner);
        _grantRole(QUANTUM_VALIDATOR_ROLE, initialOwner);
        _grantRole(ANALYTICS_ROLE, initialOwner);

        // Set contract addresses
        trustedForwarder = trustedForwarderAddr;
        if (trustedForwarderAddr != address(0)) {
            _grantRole(TRUSTED_FORWARDER_ROLE, trustedForwarderAddr);
        }

        if (lucidAccessAddr != address(0)) {
            lucidAccessContract = ILucidAccess(lucidAccessAddr);
        }

        if (governanceAddr != address(0)) {
            governanceContract = IDreamGovernance(governanceAddr);
        }

        if (dreamTokenAddr != address(0)) {
            dreamTokenContract = IDreamToken(dreamTokenAddr);
        }

        // Initialize analytics
        dreamAnalytics.lastUpdateBlock = block.number;
    }

    // ============ Core Dream Functions ============
    
    /**
     * @notice Interface a dream with the quantum network
     * @param ipfsHash The IPFS hash of the dream content
     * @param dreamSize The size of the dream data in bytes
     * @param metadata Optional metadata hash for additional information
     * @return dreamId The unique ID of the interfaced dream
     */
    function interfaceDream(
        string memory ipfsHash,
        uint256 dreamSize,
        bytes32 metadata
    )
        public
        whenNotPaused
        nonReentrant
        validIpfsHash(ipfsHash)
        requiresLucidAccess(ILucidAccess(address(0)).FEATURE_DREAM_RECORDING(), dreamSize)
        returns (uint256 dreamId)
    {
        require(dreamSize <= MAX_DREAM_SIZE, "OneiroSphere: Dream size exceeds maximum");
        require(dreamSize > 0, "OneiroSphere: Dream size cannot be zero");

        // Check daily limits if LUCID access is configured
        if (address(lucidAccessContract) != address(0)) {
            lucidAccessContract.recordDreamAccess(_msgSender(), dreamSize);
        }

        // Generate unique dream ID
        _dreamIdCounter.increment();
        dreamId = _dreamIdCounter.current();

        // Get current access tier
        uint256 accessTier = 0;
        if (address(lucidAccessContract) != address(0)) {
            accessTier = lucidAccessContract.getUserTier(_msgSender());
        }

        // Create the dream record
        dreams[dreamId] = QuantumDream({
            dreamId: dreamId,
            dreamer: _msgSender(),
            ipfsHash: ipfsHash,
            timestamp: block.timestamp,
            blockNumber: block.number,
            dreamSize: dreamSize,
            quantumSignature: bytes32(0), // Will be set during validation
            accessTier: accessTier,
            validated: false,
            cognitivePattern: 0, // Will be set during analysis
            metadata: metadata
        });

        // Update mappings
        dreamerToDreams[_msgSender()].push(dreamId);
        ipfsHashToDreamId[ipfsHash] = dreamId;
        dreamerStorageUsed[_msgSender()] += dreamSize;

        // Update daily count
        uint256 today = block.timestamp / 1 days;
        dailyDreamCount[_msgSender()][today]++;

        // Update analytics
        _updateDreamAnalytics();

        // Reward dreamer through DREAM token contract if connected
        if (address(dreamTokenContract) != address(0)) {
            try dreamTokenContract.recordDreamReward(_msgSender(), keccak256(abi.encodePacked(ipfsHash))) {
                // Dream reward successful
            } catch {
                // Continue even if reward fails
            }
        }

        emit DreamInterfaced(dreamId, _msgSender(), ipfsHash, dreamSize, accessTier);

        return dreamId;
    }

    /**
     * @notice Interface a dream with just IPFS hash (backward compatibility)
     * @param ipfsHash The IPFS hash of the dream content
     * @return dreamId The unique ID of the interfaced dream
     */
    function interfaceDream(string memory ipfsHash)
        external
        returns (uint256 dreamId)
    {
        return interfaceDream(ipfsHash, 1024, bytes32(0)); // Default size and empty metadata
    }

    /**
     * @notice Validates a dream with quantum signature
     * @param dreamId The ID of the dream to validate
     * @param quantumSignature The quantum validation signature
     * @param cognitivePattern The identified cognitive pattern
     */
    function validateQuantumDream(
        uint256 dreamId,
        bytes32 quantumSignature,
        uint256 cognitivePattern
    )
        external
        onlyRole(QUANTUM_VALIDATOR_ROLE)
        whenNotPaused
    {
        require(dreamId > 0 && dreamId <= _dreamIdCounter.current(), "OneiroSphere: Invalid dream ID");
        require(quantumSignature != bytes32(0), "OneiroSphere: Invalid quantum signature");

        QuantumDream storage dream = dreams[dreamId];
        require(!dream.validated, "OneiroSphere: Dream already validated");

        // Update dream validation
        dream.quantumSignature = quantumSignature;
        dream.cognitivePattern = cognitivePattern;
        dream.validated = true;

        // Update cognitive pattern mapping
        if (cognitivePattern > 0) {
            cognitivePatternToDreams[cognitivePattern].push(dreamId);
        }

        // Update validator stats
        validatorStats[msg.sender]++;

        // Update analytics
        dreamAnalytics.validatedDreams++;

        emit QuantumDreamValidated(dreamId, msg.sender, quantumSignature, cognitivePattern);
    }

    // ============ View Functions ============
    
    /**
     * @notice Gets a specific dream by ID
     * @param dreamId The ID of the dream
     * @return The QuantumDream struct
     */
    function getDream(uint256 dreamId) external view returns (QuantumDream memory) {
        require(dreamId > 0 && dreamId <= _dreamIdCounter.current(), "OneiroSphere: Invalid dream ID");
        return dreams[dreamId];
    }

    /**
     * @notice Gets all dreams for a specific dreamer
     * @param dreamer The address of the dreamer
     * @return Array of dream IDs
     */
    function getDreamerDreams(address dreamer) external view returns (uint256[] memory) {
        return dreamerToDreams[dreamer];
    }

    /**
     * @notice Gets dreams for a specific cognitive pattern
     * @param pattern The cognitive pattern identifier
     * @return Array of dream IDs
     */
    function getDreamsByPattern(uint256 pattern) external view returns (uint256[] memory) {
        return cognitivePatternToDreams[pattern];
    }

    /**
     * @notice Gets the total number of dreams for a dreamer
     * @param dreamer The address of the dreamer
     * @return The total dream count
     */
    function getDreamCount(address dreamer) external view returns (uint256) {
        return dreamerToDreams[dreamer].length;
    }

    /**
     * @notice Gets the latest dream for a dreamer
     * @param dreamer The address of the dreamer
     * @return The QuantumDream struct of the latest dream
     */
    function getLatestDream(address dreamer) external view returns (QuantumDream memory) {
        uint256[] memory dreamerDreams = dreamerToDreams[dreamer];
        require(dreamerDreams.length > 0, "OneiroSphere: No dreams found for this dreamer");
        return dreams[dreamerDreams[dreamerDreams.length - 1]];
    }

    /**
     * @notice Gets dreams recorded in a specific time range
     * @param startTime The start timestamp
     * @param endTime The end timestamp
     * @param offset The offset for pagination
     * @param limit The maximum number of dreams to return
     * @return dreamIds Array of dream IDs in the time range
     */
    function getDreamsByTimeRange(
        uint256 startTime,
        uint256 endTime,
        uint256 offset,
        uint256 limit
    ) external view returns (uint256[] memory dreamIds) {
        require(startTime <= endTime, "OneiroSphere: Invalid time range");
        require(limit > 0 && limit <= 100, "OneiroSphere: Invalid limit");

        uint256[] memory tempIds = new uint256[](limit);
        uint256 count = 0;
        uint256 skipped = 0;

        for (uint256 i = 1; i <= _dreamIdCounter.current() && count < limit; i++) {
            QuantumDream memory dream = dreams[i];
            if (dream.timestamp >= startTime && dream.timestamp <= endTime) {
                if (skipped >= offset) {
                    tempIds[count] = i;
                    count++;
                } else {
                    skipped++;
                }
            }
        }

        // Resize array to actual count
        dreamIds = new uint256[](count);
        for (uint256 j = 0; j < count; j++) {
            dreamIds[j] = tempIds[j];
        }
    }

    /**
     * @notice Gets current dream analytics
     * @return The DreamAnalytics struct
     */
    function getDreamAnalytics() external view returns (DreamAnalytics memory) {
        return dreamAnalytics;
    }

    /**
     * @notice Gets daily dream count for a user
     * @param dreamer The address of the dreamer
     * @param day The day (timestamp / 1 days)
     * @return The number of dreams recorded that day
     */
    function getDailyDreamCount(address dreamer, uint256 day) external view returns (uint256) {
        return dailyDreamCount[dreamer][day];
    }

    /**
     * @notice Gets total storage used by a dreamer
     * @param dreamer The address of the dreamer
     * @return The total storage used in bytes
     */
    function getDreamerStorageUsed(address dreamer) external view returns (uint256) {
        return dreamerStorageUsed[dreamer];
    }

    // ============ Analytics Functions ============
    
    /**
     * @notice Identifies cognitive patterns in a dream (AI/ML integration point)
     * @param dreamId The ID of the dream to analyze
     * @param pattern The identified pattern
     * @param confidence The confidence level (0-100)
     */
    function identifyCognitivePattern(
        uint256 dreamId,
        uint256 pattern,
        uint256 confidence
    )
        external
        onlyRole(ANALYTICS_ROLE)
    {
        require(dreamId > 0 && dreamId <= _dreamIdCounter.current(), "OneiroSphere: Invalid dream ID");
        require(confidence <= 100, "OneiroSphere: Invalid confidence level");

        QuantumDream storage dream = dreams[dreamId];
        dream.cognitivePattern = pattern;

        if (pattern > 0) {
            cognitivePatternToDreams[pattern].push(dreamId);
        }

        emit CognitivePatternIdentified(dreamId, pattern, confidence, msg.sender);
    }

    // ============ Administrative Functions ============
    
    /**
     * @notice Updates the trusted forwarder for meta-transactions
     * @param newForwarder The new trusted forwarder address
     */
    function updateTrustedForwarder(address newForwarder)
        external
        onlyRole(GOVERNANCE_ROLE)
    {
        if (trustedForwarder != address(0)) {
            _revokeRole(TRUSTED_FORWARDER_ROLE, trustedForwarder);
        }
        
        trustedForwarder = newForwarder;
        
        if (newForwarder != address(0)) {
            _grantRole(TRUSTED_FORWARDER_ROLE, newForwarder);
        }
    }

    /**
     * @notice Updates contract addresses
     * @param lucidAccessAddr New LUCID access contract address
     * @param governanceAddr New governance contract address
     * @param dreamTokenAddr New DREAM token contract address
     */
    function updateContractAddresses(
        address lucidAccessAddr,
        address governanceAddr,
        address dreamTokenAddr
    )
        external
        onlyRole(GOVERNANCE_ROLE)
    {
        if (lucidAccessAddr != address(0)) {
            lucidAccessContract = ILucidAccess(lucidAccessAddr);
        }
        if (governanceAddr != address(0)) {
            governanceContract = IDreamGovernance(governanceAddr);
        }
        if (dreamTokenAddr != address(0)) {
            dreamTokenContract = IDreamToken(dreamTokenAddr);
        }
    }

    // ============ Emergency Functions ============
    
    /**
     * @notice Pauses the contract (emergency only)
     */
    function pause() external onlyRole(EMERGENCY_ROLE) {
        _pause();
    }

    /**
     * @notice Unpauses the contract (emergency only)
     */
    function unpause() external onlyRole(EMERGENCY_ROLE) {
        _unpause();
    }

    /**
     * @notice Emergency dream removal (extreme cases only)
     * @param dreamId The ID of the dream to remove
     * @param reason The reason for removal
     */
    function emergencyRemoveDream(uint256 dreamId, string memory reason)
        external
        onlyRole(EMERGENCY_ROLE)
    {
        require(dreamId > 0 && dreamId <= _dreamIdCounter.current(), "OneiroSphere: Invalid dream ID");
        
        QuantumDream storage dream = dreams[dreamId];
        require(dream.dreamer != address(0), "OneiroSphere: Dream already removed");

        // Clear the dream data
        delete ipfsHashToDreamId[dream.ipfsHash];
        delete dreams[dreamId];

        // Note: We don't remove from dreamerToDreams to maintain array integrity
        // Instead, the dream ID will point to an empty struct
    }

    // ============ Internal Functions ============
    
    /**
     * @notice Updates global dream analytics
     */
    function _updateDreamAnalytics() internal {
        dreamAnalytics.totalDreams = _dreamIdCounter.current();
        dreamAnalytics.lastUpdateBlock = block.number;

        // Update total dreamers count (expensive operation, done periodically)
        if (dreamAnalytics.lastUpdateBlock % 100 == 0) {
            // This could be optimized with a separate counter in production
            dreamAnalytics.totalDreamers = _calculateUniqueDreamers();
        }

        emit DreamAnalyticsUpdated(
            dreamAnalytics.totalDreams,
            dreamAnalytics.validatedDreams,
            dreamAnalytics.totalDreamers,
            block.number
        );
    }

    /**
     * @notice Calculates the number of unique dreamers (expensive operation)
     * @return The number of unique dreamers
     */
    function _calculateUniqueDreamers() internal view returns (uint256) {
        // This is a simplified implementation
        // In production, this should use a more efficient approach
        return dreamAnalytics.totalDreamers + 1; // Placeholder
    }

    /**
     * @notice Authorizes contract upgrades
     * @param newImplementation The new implementation address
     */
    function _authorizeUpgrade(address newImplementation)
        internal
        override
        onlyRole(GOVERNANCE_ROLE)
    {}

    // ============ Meta-transaction Support ============
    
    /**
     * @notice Checks if the forwarder is trusted
     * @param forwarder The forwarder address to check
     * @return True if the forwarder is trusted
     */
    function isTrustedForwarder(address forwarder) public view returns (bool) {
        return hasRole(TRUSTED_FORWARDER_ROLE, forwarder);
    }

    /**
     * @notice Gets the message sender (supports meta-transactions)
     * @return sender The actual sender address
     */
    function _msgSender() internal view override returns (address sender) {
        if (isTrustedForwarder(msg.sender)) {
            // The assembly code is more gas efficient
            assembly {
                sender := shr(96, calldataload(sub(calldatasize(), 20)))
            }
        } else {
            sender = msg.sender;
        }
    }

    /**
     * @notice Gets the message data (supports meta-transactions)
     * @return The actual message data
     */
    function _msgData() internal view override returns (bytes calldata) {
        if (isTrustedForwarder(msg.sender)) {
            return msg.data[:msg.data.length - 20];
        } else {
            return msg.data;
        }
    }

    // ============ Receive ETH ============
    
    receive() external payable {
        // Allow contract to receive ETH for gas optimization on SKALE
    }
}