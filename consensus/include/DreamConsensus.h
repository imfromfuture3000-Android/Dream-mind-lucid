#pragma once

#include <libconsensus/ConsensusEngine.h>
#include <libconsensus/BlockConsensusAgent.h>
#include <string>
#include <memory>

namespace dream {

class DreamConsensus {
public:
    DreamConsensus(const std::string& configPath);
    ~DreamConsensus();

    // Initialize consensus engine with SKALE chain parameters
    void initialize(uint64_t nodeCount, uint64_t requiredSignatures);

    // Add a new dream block to consensus
    void proposeDreamBlock(const std::string& dreamerId, const std::string& dreamData);

    // Get latest finalized dream block
    std::string getLatestDreamBlock() const;

    // Consensus status check
    bool isConsensusRunning() const;
    uint64_t getBlockHeight() const;

private:
    std::unique_ptr<consensus::ConsensusEngine> engine_;
    std::shared_ptr<consensus::BlockConsensusAgent> agent_;

    // Internal state
    uint64_t currentHeight_;
    std::string latestBlockHash_;

    // Configuration
    std::string configPath_;
    uint64_t nodeCount_;
    uint64_t requiredSignatures_;

    // Initialize BLS signatures for consensus
    void initializeBLS();

    // Internal consensus callbacks
    void onBlockProposed(const std::string& blockHash);
    void onBlockFinalized(uint64_t blockNumber, const std::string& blockHash);
};

} // namespace dream
