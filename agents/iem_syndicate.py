#!/usr/bin/env python3
"""
IEM-Ω Syndicate — SKALE Crew
Deployer | Auditor | Looter | Oracle
------------------------------------
Copilot: Enhance with IPFS integration and Oneiro-Sphere agent
"""

import os, json, hashlib, argparse, time
from web3 import Web3
import ipfshttpclient  # Copilot: Install with `pip install ipfshttpclient`

# ====== CONFIG ======
RPC = os.getenv("SKALE_RPC", "https://mainnet.skalenodes.com/v1/elated-tan-skat")
PRIVATE_KEY = os.getenv("DEPLOYER_KEY", "")
CHAIN_ID = int(os.getenv("SKALE_CHAIN_ID", "2046399126"))  # Europa Hub

w3 = Web3(Web3.HTTPProvider(RPC))

MEMORY_FILE = "iem_memory.json"
CONTRACT_FILE = "contracts/IEMDreams.sol"
ARTIFACT_FILE = "artifacts/contracts/IEMDreams.sol/IEMDreams.json"

# ====== UTILS ======
def load_memory():
    if os.path.exists(MEMORY_FILE):
        return json.load(open(MEMORY_FILE))
    return {"lastDeployed": {}}

def save_memory(mem):
    json.dump(mem, open(MEMORY_FILE, "w"), indent=2)
# ====== DEPLOYER ======
def deploy_contract():
    from solcx import compile_standard, install_solc
    install_solc("0.8.20")

    source = open(CONTRACT_FILE).read()
    compiled = compile_standard({
        "language": "Solidity",
        "sources": {CONTRACT_FILE: {"content": source}},
        "settings": {"outputSelection": {"*": {"*": ["abi", "evm.bytecode"]}}}
    }, solc_version="0.8.20")

    abi = compiled["contracts"][CONTRACT_FILE]["IEMDreams"]["abi"]
    bytecode = compiled["contracts"][CONTRACT_FILE]["IEMDreams"]["evm"]["bytecode"]["object"]

    acct = w3.eth.account.from_key(PRIVATE_KEY)
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx = contract.constructor().build_transaction({
        "from": acct.address,
        "nonce": w3.eth.get_transaction_count(acct.address),
        "gas": 5_000_000,
        "gasPrice": 0,  # SKALE zero gas
        "chainId": CHAIN_ID
    })

    signed = acct.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    mem = load_memory()
    mem["lastDeployed"] = {"address": receipt.contractAddress, "abi": abi}
    save_memory(mem)

    print("🚀 Deployed at:", receipt.contractAddress)

# ====== AUDITOR ======
def audit_contract():
    source = open(CONTRACT_FILE).read()
    hash = hashlib.sha256(source.encode()).hexdigest()
    print("🔎 Source Hash:", hash)

    mem = load_memory()
    mem["lastDeployed"]["auditHash"] = hash
    save_memory(mem)

# ====== LOOTER ======
def listen_events():
    mem = load_memory()
    abi = mem["lastDeployed"]["abi"]
    addr = mem["lastDeployed"]["address"]

    contract = w3.eth.contract(address=addr, abi=abi)
    event_filter = contract.events.DreamRecorded.create_filter(fromBlock="latest")

    print("👂 Listening to Dreams on:", addr)
    while True:
        for e in event_filter.get_new_entries():
            print("💭 Dream spotted:", e.args.dream, "from", e.args.dreamer)
        time.sleep(2)

# ====== ORACLE ======
def update_state():
    mem = load_memory()
    addr = mem["lastDeployed"]["address"]
    code = w3.eth.get_code(addr).hex()
    mem["lastDeployed"]["onchainCode"] = code[:64] + "..."
    save_memory(mem)
    print("📡 Oracle synced on-chain state")

# ====== ONEIROSPHERE (FUTURE) ======
def interface_dream():  # Copilot: Implement when OneiroSphere.sol is ready
    pass  # Placeholder for IPFS upload and contract call

# ====== MAIN ======
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="IEM Syndicate Crew")
    parser.add_argument("agent", choices=["deploy", "audit", "loot", "oracle", "oneirosphere"], help="Which agent to run")
    args = parser.parse_args()

    if args.agent == "deploy":
        deploy_contract()
    elif args.agent == "audit":
        audit_contract()
    elif args.agent == "loot":
        listen_events()
    elif args.agent == "oracle":
        update_state()
    elif args.agent == "oneirosphere":
        interface_dream()
