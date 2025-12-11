#include "AgentRegistry.h"
#include <fstream>
#include <nlohmann/json.hpp>
#include <regex>

using json = nlohmann::json;

namespace dream {

AgentRegistry::AgentRegistry(const std::string& configPath)
    : configPath_(configPath) {
    loadConfig();
}

void AgentRegistry::loadConfig() {
    std::ifstream file(configPath_);
    if (!file.is_open()) {
        throw std::runtime_error("Could not open config file: " + configPath_);
    }

    json config;
    file >> config;

    // Load agents
    for (const auto& [name, agent] : config["agents"].items()) {
        AgentInfo info;
        info.address = agent["address"];
        info.role = agent["role"];
        info.permissions = agent["permissions"].get<std::vector<std::string>>();
        agents_[name] = info;
    }

    // Load tokens
    for (const auto& [symbol, token] : config["tokens"].items()) {
        TokenInfo info;
        info.address = token["address"];
        info.totalSupply = std::stoull(token["totalSupply"].get<std::string>());
        info.decimals = token["decimals"];
        tokens_[symbol] = info;
    }
}

bool AgentRegistry::registerAgent(const std::string& name, const AgentInfo& info) {
    if (agents_.find(name) != agents_.end()) {
        return false;
    }

    if (!validateAddress(info.address)) {
        return false;
    }

    agents_[name] = info;
    notifyAgentEvent(name, "registered");
    return true;
}

bool AgentRegistry::hasPermission(
    const std::string& agentAddress,
    const std::string& permission
) const {
    for (const auto& [name, info] : agents_) {
        if (info.address == agentAddress) {
            return std::find(
                info.permissions.begin(),
                info.permissions.end(),
                permission
            ) != info.permissions.end();
        }
    }
    return false;
}

std::string AgentRegistry::getAgentAddress(const std::string& name) const {
    auto it = agents_.find(name);
    if (it != agents_.end()) {
        return it->second.address;
    }
    return "";
}

std::vector<std::string> AgentRegistry::getAgentPermissions(
    const std::string& name
) const {
    auto it = agents_.find(name);
    if (it != agents_.end()) {
        return it->second.permissions;
    }
    return {};
}

std::string AgentRegistry::getTokenAddress(const std::string& symbol) const {
    auto it = tokens_.find(symbol);
    if (it != tokens_.end()) {
        return it->second.address;
    }
    return "";
}

TokenInfo AgentRegistry::getTokenInfo(const std::string& symbol) const {
    auto it = tokens_.find(symbol);
    if (it != tokens_.end()) {
        return it->second;
    }
    return TokenInfo{};
}

bool AgentRegistry::validateAddress(const std::string& address) const {
    // Basic Ethereum address validation (0x followed by 40 hex chars)
    static const std::regex addr_regex("^0x[0-9a-fA-F]{40}$");
    return std::regex_match(address, addr_regex);
}

bool AgentRegistry::isRegisteredAgent(const std::string& address) const {
    for (const auto& [name, info] : agents_) {
        if (info.address == address) {
            return true;
        }
    }
    return false;
}

void AgentRegistry::setAgentEventHandler(AgentEventHandler handler) {
    eventHandler_ = handler;
}

void AgentRegistry::notifyAgentEvent(
    const std::string& agent,
    const std::string& action
) {
    if (eventHandler_) {
        eventHandler_(agent, action);
    }
}

} // namespace dream
