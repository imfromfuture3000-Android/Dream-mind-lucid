#include "DreamConsensus.h"
#include <libconsensus/BLSUtils.h>
#include <stdexcept>

namespace dream {

DreamConsensus::DreamConsensus(const std::string& configPath)
    : configPath_(configPath)
    , currentHeight_(0)
    , nodeCount_(0)
    , requiredSignatures_(0) {
}

DreamConsensus::~DreamConsensus() {
    if (engine_) {
        engine_->exitGracefully();
    }
}

void DreamConsensus::initialize(uint64_t nodeCount, uint64_t requiredSignatures) {
    nodeCount_ = nodeCount;
    requiredSignatures_ = requiredSignatures;

    // Initialize BLS cryptography
    initializeBLS();

    // Create and configure consensus engine
    engine_ = std::make_unique<consensus::ConsensusEngine>();
    
    // Configure consensus parameters
    consensus::ConsensusExtFace::consensusConfig config;
    config.nodeCount = nodeCount_;
    config.requiredSigners = requiredSignatures_;
    
    // Set up network info (ports, IPs, etc) from config file
    engine_->parseTestConfigFile(configPath_);
    
    // Create consensus agent
    agent_ = engine_->createAgent(config);
    
    // Register callbacks
    agent_->onBlockProposed([this](const std::string& blockHash) {
        onBlockProposed(blockHash);
    });

    agent_->onBlockFinalized([this](uint64_t blockNumber, const std::string& blockHash) {
        onBlockFinalized(blockNumber, blockHash);
    });

    // Start consensus engine
    engine_->start();
}

void DreamConsensus::proposeDreamBlock(const std::string& dreamerId, const std::string& dreamData) {
    if (!engine_ || !agent_) {
        throw std::runtime_error("Consensus engine not initialized");
    }

    // Create dream block data
    std::string blockData = dreamerId + ":" + dreamData;
    
    // Propose block to consensus
    agent_->proposeBlock(blockData);
}

std::string DreamConsensus::getLatestDreamBlock() const {
    return latestBlockHash_;
}

bool DreamConsensus::isConsensusRunning() const {
    return engine_ && engine_->isWorking();
}

uint64_t DreamConsensus::getBlockHeight() const {
    return currentHeight_;
}

void DreamConsensus::initializeBLS() {
    // Initialize BLS crypto library
    consensus::initBLSCrypto();
    
    // Load keys from config or generate new ones
    // TODO: Implement key management
}

void DreamConsensus::onBlockProposed(const std::string& blockHash) {
    // Handle newly proposed block
    // TODO: Implement block verification
}

void DreamConsensus::onBlockFinalized(uint64_t blockNumber, const std::string& blockHash) {
    currentHeight_ = blockNumber;
    latestBlockHash_ = blockHash;
    
    // TODO: Trigger dream state updates in smart contracts
}

} // namespace dream
