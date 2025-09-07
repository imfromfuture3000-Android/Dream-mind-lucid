#pragma once

#include <string>
#include <vector>
#include <unordered_map>
#include <functional>

namespace dream {

struct AgentInfo {
    std::string address;
    std::string role;
    std::vector<std::string> permissions;
};

struct TokenInfo {
    std::string address;
    uint64_t totalSupply;
    uint8_t decimals;
};

class AgentRegistry {
public:
    explicit AgentRegistry(const std::string& configPath);

    // Agent management
    bool registerAgent(const std::string& name, const AgentInfo& info);
    bool hasPermission(const std::string& agentAddress, const std::string& permission) const;
    std::string getAgentAddress(const std::string& name) const;
    std::vector<std::string> getAgentPermissions(const std::string& name) const;
    
    // Token management
    std::string getTokenAddress(const std::string& symbol) const;
    TokenInfo getTokenInfo(const std::string& symbol) const;
    
    // Validation
    bool validateAddress(const std::string& address) const;
    bool isRegisteredAgent(const std::string& address) const;
    
    // Events
    using AgentEventHandler = std::function<void(const std::string& agent, const std::string& action)>;
    void setAgentEventHandler(AgentEventHandler handler);

private:
    std::string configPath_;
    std::unordered_map<std::string, AgentInfo> agents_;
    std::unordered_map<std::string, TokenInfo> tokens_;
    AgentEventHandler eventHandler_;
    
    void loadConfig();
    void notifyAgentEvent(const std::string& agent, const std::string& action);
};

} // namespace dream
