from web3 import Web3
from eth_account import Account
import json

# SKALE chains to check
SKALE_CHAINS = [
    {
        "name": "Europa Hub",
        "rpc": "https://mainnet.skalenodes.com/v1/elated-tan-skat",
        "contract": "0xF874AeC485733971a7dAEE9167E388f218aa93D5"
    },
    {
        "name": "Calypso",
        "rpc": "https://mainnet.skalenodes.com/v1/honorable-steel-rasalhague",
        "contract": "0x46815B01d46C3A4217Ca8CF95A06dA64196755bC"
    },
    {
        "name": "Nebula",
        "rpc": "https://mainnet.skalenodes.com/v1/green-giddy-denebola",
        "contract": "0x46815B01d46C3A4217Ca8CF95A06dA64196755bC"
    },
    {
        "name": "Titan",
        "rpc": "https://mainnet.skalenodes.com/v1/parallel-stormy-spica",
        "contract": "0x46815B01d46C3A4217Ca8CF95A06dA64196755bC"
    }
]

for chain in SKALE_CHAINS:
    print(f"\n🔍 Checking {chain['name']}")
    print(f"RPC: {chain['rpc']}")
    print(f"Contract: {chain['contract']}")
    
    # Connect to chain
    w3 = Web3(Web3.HTTPProvider(chain['rpc']))
    if not w3.is_connected():
        print("❌ Failed to connect to network")
        continue
    
    # Get contract code
    code = w3.eth.get_code(chain['contract'])
    print(f"Code exists: {len(code) > 0}")
    print(f"Code size: {len(code)} bytes")
    
    if len(code) > 0:
        print("✅ Contract verified!")
    else:
        print("❌ No contract code found at this address")
    
    print("="*50)
