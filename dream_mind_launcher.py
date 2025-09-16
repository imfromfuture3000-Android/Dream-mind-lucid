#!/usr/bin/env python3
"""
Dream-Mind-Lucid Launcher
------------------------
All-in-one script to auto-install dependencies, set up MCP server, and deploy
contracts (IEMDreams and OneiroSphere) via Copilot integration with Infura and Biconomy.
Last Updated: September 01, 2025, 02:46 AM PST
"""

import os
import subprocess
import time
import json
from web3 import Web3
try:
    from biconomy.client import Biconomy
    BICONOMY_AVAILABLE = True
except ImportError:
    BICONOMY_AVAILABLE = False
    print("⚠️ Biconomy SDK not available - using standard Web3 transactions")

try:
    from mcp.server import Server as McpServer
    MCP_AVAILABLE = True
except ImportError:
    try:
        from modelcontextprotocol.server import McpServer, McpServerTool, McpServerToolType
        MCP_AVAILABLE = True
    except ImportError:
        MCP_AVAILABLE = False
        print("⚠️ MCP server not available - MCP functionality will be disabled")
import ipfshttpclient
from solcx import install_solc

# Environment Configuration
INFURA_PROJECT_ID = os.getenv("INFURA_PROJECT_ID", "YOUR_INFURA_API_KEY")
BICONOMY_API_KEY = os.getenv("BICONOMY_API_KEY", "YOUR_BICONOMY_API_KEY")
SKALE_CHAIN_ID = int(os.getenv("SKALE_CHAIN_ID", "2046399126"))
PRIVATE_KEY = os.getenv("DEPLOYER_KEY", "")
FORWARDER_ADDRESS = os.getenv("FORWARDER_ADDRESS", "0xYOUR_BICONOMY_FORWARDER")
MEMORY_FILE = "iem_memory.json"

# Use Infura RPC if available, otherwise fallback to SKALE RPC
SKALE_RPC = "https://mainnet.skalenodes.com/v1/elated-tan-skat"
if INFURA_PROJECT_ID and INFURA_PROJECT_ID != "YOUR_INFURA_API_KEY":
    RPC_URL = f"https://skale-mainnet.infura.io/v3/{INFURA_PROJECT_ID}"
else:
    RPC_URL = SKALE_RPC

w3 = Web3(Web3.HTTPProvider(RPC_URL))
if BICONOMY_AVAILABLE:
    biconomy = Biconomy(w3, api_key=BICONOMY_API_KEY, chain_id=SKALE_CHAIN_ID)
else:
    biconomy = None
ipfs_client = ipfshttpclient.connect()

# MCP Server Setup
if MCP_AVAILABLE:
    server = McpServer("dream_mind_server", "Manages Dream-Mind-Lucid deployment and dreams")
else:
    server = None

def install_dependencies():
    """Auto-install required dependencies."""
    try:
        subprocess.run(["pip", "install", "web3", "py-solc-x", "mcp", "ipfshttpclient", "PyExifTool"], check=True)
        install_solc("0.8.20")
        print("✅ Dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        exit(1)

def load_memory():
    if os.path.exists(MEMORY_FILE):
        return json.load(open(MEMORY_FILE))
    return {"lastDeployed": {}, "loot": []}

def save_memory(mem):
    with open(MEMORY_FILE, "w") as f:
        json.dump(mem, f, indent=2)

def compile_contract(contract_name):
    with open(f"contracts/{contract_name}.sol") as f:
        source = f.read()
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {f"{contract_name}.sol": {"content": source}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
    }, solc_version="0.8.20")
    return compiled["contracts"][f"{contract_name}.sol"][contract_name]

@McpServerToolType
class DreamTools:
    @McpServerTool(description="Deploy a Dream-Mind-Lucid contract to SKALE")
    def deploy_contract(self, contract_name: str) -> str:
        """Deploy the specified contract (IEMDreams or OneiroSphere)."""
        if contract_name not in ["IEMDreams", "OneiroSphere"]:
            return "Invalid contract name. Use IEMDreams or OneiroSphere."
        
        compiled = compile_contract(contract_name)
        bytecode = compiled["evm"]["bytecode"]["object"]
        abi = compiled["abi"]

        acct = w3.eth.account.from_key(PRIVATE_KEY)
        contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        tx = contract.constructor(FORWARDER_ADDRESS).build_transaction({
            "from": acct.address,
            "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 5_000_000,
            "gasPrice": 0,
            "chainId": SKALE_CHAIN_ID
        })
        signed_tx = acct.sign_transaction(tx)
        if biconomy and BICONOMY_AVAILABLE:
            tx_hash = biconomy.send_transaction(signed_tx.raw_transaction)
        else:
            # Use regular Web3 transaction (SKALE has zero gas anyway)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        memory = load_memory()
        memory["lastDeployed"][contract_name] = {
            "address": receipt.contractAddress,
            "abi": abi,
            "timestamp": time.time()
        }
        save_memory(memory)
        return f"✅ Deployed {contract_name} at {receipt.contractAddress}"

    @McpServerTool(description="Record a dream and store it via IPFS")
    def record_dream(self, dream: str) -> str:
        """Record a dream and return its IPFS hash."""
        memory = load_memory()
        if not memory.get("lastDeployed", {}).get("IEMDreams", {}).get("address"):
            return "❌ IEMDreams not deployed. Deploy it first."
        
        contract = w3.eth.contract(address=memory["lastDeployed"]["IEMDreams"]["address"], abi=memory["lastDeployed"]["IEMDreams"]["abi"])
        acct = w3.eth.account.from_key(PRIVATE_KEY)
        tx = contract.functions.recordDream(dream).build_transaction({
            "from": acct.address,
            "nonce": w3.eth.get_transaction_count(acct.address),
            "gas": 200_000,
            "gasPrice": 0,
            "chainId": SKALE_CHAIN_ID
        })
        signed_tx = acct.sign_transaction(tx)
        if biconomy and BICONOMY_AVAILABLE:
            tx_hash = biconomy.send_transaction(signed_tx.raw_transaction)
        else:
            # Use regular Web3 transaction (SKALE has zero gas anyway)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        w3.eth.wait_for_transaction_receipt(tx_hash)

        ipfs_hash = ipfs_client.add_str(dream)["Hash"]
        memory["loot"].append({"dreamer": acct.address, "dream": dream, "ipfsHash": ipfs_hash, "timestamp": time.time()})
        save_memory(memory)
        return f"✅ Dream recorded. IPFS Hash: {ipfs_hash}"

    @McpServerTool(description="Summon OneiroBot for dream monitoring and assistance")
    def summon_oneirobot(self) -> str:
        """Summon OneiroBot and perform initial health checks."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
            copilot_instruction = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(copilot_instruction)
            
            result = copilot_instruction.handle_copilot_command("summon_oneirobot")
            return f"🌙 OneiroBot summoned! Status: {result.get('status', {}).get('status', 'UNKNOWN')}"
        except Exception as e:
            return f"❌ Failed to summon OneiroBot: {e}"

    @McpServerTool(description="Get OneiroBot status and health check")
    def oneirobot_status(self) -> str:
        """Get comprehensive OneiroBot status and health information."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
            copilot_instruction = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(copilot_instruction)
            
            result = copilot_instruction.handle_copilot_command("oneirobot_status")
            status = result.get('status', {})
            health = result.get('health', {})
            
            return f"🤖 OneiroBot Status: {status.get('status', 'UNKNOWN')} | Activities: {status.get('total_activities', 0)} | MCP Health: {health.get('connectivity', 'UNKNOWN')}"
        except Exception as e:
            return f"❌ Failed to get OneiroBot status: {e}"

    @McpServerTool(description="Monitor dream submissions and consensus phases")
    def oneirobot_scan(self) -> str:
        """Monitor dream submissions and consensus state."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
            copilot_instruction = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(copilot_instruction)
            
            result = copilot_instruction.handle_copilot_command("oneirobot_scan")
            scan_result = result.get('result', {})
            
            return f"🕵️ Dream Scan Complete | Dreams: {scan_result.get('dreams_detected', 0)} | Consensus: {scan_result.get('consensus_state', 'UNKNOWN')} | Status: {scan_result.get('status', 'UNKNOWN')}"
        except Exception as e:
            return f"❌ Dream scan failed: {e}"

    @McpServerTool(description="Get optimization suggestions from OneiroBot")
    def oneirobot_optimize(self) -> str:
        """Get OneiroBot's optimization suggestions for the Oneiro-Sphere."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
            copilot_instruction = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(copilot_instruction)
            
            result = copilot_instruction.handle_copilot_command("oneirobot_optimize")
            suggestions = result.get('suggestions', [])
            
            formatted_suggestions = "\n".join([f"  • {suggestion}" for suggestion in suggestions[:5]])  # Limit to 5 suggestions
            return f"🧠 OneiroBot Optimization Analysis:\n{formatted_suggestions}"
        except Exception as e:
            return f"❌ Optimization analysis failed: {e}"

    @McpServerTool(description="Get quick fixes from OneiroBot for specific issues")
    def oneirobot_fix(self, issue_type: str = "general") -> str:
        """Get OneiroBot's quick fix suggestions for specific issue types."""
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location("copilot_instruction", "copilot-instruction.py")
            copilot_instruction = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(copilot_instruction)
            
            result = copilot_instruction.handle_copilot_command("oneirobot_fix", [issue_type])
            fixes = result.get('fixes', [])
            test_command = result.get('test_command', '')
            
            formatted_fixes = "\n".join([f"  • {fix}" for fix in fixes[:3]])  # Limit to 3 fixes
            return f"🔧 OneiroBot Quick Fixes for {issue_type}:\n{formatted_fixes}\n\n🧪 Test: {test_command}"
        except Exception as e:
            return f"❌ Quick fix generation failed: {e}"

def setup_mcp():
    """Set up MCP server and integrate with Copilot."""
    server.add_tool_class(DreamTools)
    server.run(port=5000, host="localhost")
    with open(".vscode/mcp.json", "w") as f:
        json.dump({
            "servers": {
                "dream_mind_server": {"type": "http", "url": "http://localhost:5000/sse"}
            }
        }, f)
    print("✅ MCP server running and config created!")

def run_all_commands():
    """Execute all deployment commands via MCP."""
    print("🚀 Starting full deployment...")
    install_dependencies()
    setup_mcp()
    time.sleep(2)  # Allow server to start
    # Simulate Copilot commands (replace with actual Copilot Chat input)
    tools = DreamTools()
    print(tools.deploy_contract("IEMDreams"))
    print(tools.deploy_contract("OneiroSphere"))
    print(tools.record_dream("I dreamed of a rocket!"))

if __name__ == "__main__":
    try:
        run_all_commands()
    except Exception as e:
        print(f"❌ Error: {e}")
