from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc
import json
import time

# SKALE chains to try
SKALE_CHAINS = [
    {
        "name": "Europa Hub",
        "rpc": "https://mainnet.skalenodes.com/v1/elated-tan-skat",
        "chain_id": 2046399126
    },
    {
        "name": "Calypso",
        "rpc": "https://mainnet.skalenodes.com/v1/honorable-steel-rasalhague",
        "chain_id": 1564830818
    },
    {
        "name": "Nebula",
        "rpc": "https://mainnet.skalenodes.com/v1/green-giddy-denebola",
        "chain_id": 1482601649
    },
    {
        "name": "Titan",
        "rpc": "https://mainnet.skalenodes.com/v1/parallel-stormy-spica",
        "chain_id": 1350216234
    }
]

# Contract source
contract_source = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract IEMDreams {
    string public name;
    uint256 public totalSupply;
    mapping(address => uint256) public balances;

    event DreamRecorded(address indexed dreamer, string dream);

    constructor() {
        name = "IEM Dreams";
        totalSupply = 777777777 * 10**18;
        balances[msg.sender] = totalSupply;
    }

    function recordDream(string memory dream) public {
        emit DreamRecorded(msg.sender, dream);
    }

    function balanceOf(address account) public view returns (uint256) {
        return balances[account];
    }
}
"""

def deploy_to_chain(chain_info):
    print(f"\n🌟 Attempting deployment on {chain_info['name']}")
    print(f"RPC: {chain_info['rpc']}")
    print(f"Chain ID: {chain_info['chain_id']}")
    
    # Connect to chain
    w3 = Web3(Web3.HTTPProvider(chain_info['rpc']))
    if not w3.is_connected():
        print("❌ Failed to connect to network")
        return False
    
    print(f"✅ Connected to network")
    
    # Set up account
    private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
    account = Account.from_key(private_key)
    print(f"📝 Using account: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    print(f"💰 Account balance: {w3.from_wei(balance, 'ether')} SKALE")
    
    try:
        # Compile contract
        if deploy_to_chain.compiled_contract is None:
            print("🔨 Compiling contract...")
            compiled = compile_standard(
                {
                    "language": "Solidity",
                    "sources": {"IEMDreams.sol": {"content": contract_source}},
                    "settings": {
                        "outputSelection": {
                            "*": {"*": ["abi", "evm.bytecode", "evm.deployedBytecode"]}
                        }
                    }
                },
                solc_version="0.8.20"
            )
            deploy_to_chain.compiled_contract = compiled
        
        # Get bytecode and ABI
        contract_interface = deploy_to_chain.compiled_contract["contracts"]["IEMDreams.sol"]["IEMDreams"]
        bytecode = contract_interface["evm"]["bytecode"]["object"]
        abi = contract_interface["abi"]
        
        # Create contract
        Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
        
        # Get nonce
        nonce = w3.eth.get_transaction_count(account.address)
        
        # Build constructor transaction
        constructor_txn = Contract.constructor().build_transaction(
            {
                "chainId": chain_info["chain_id"],
                "gas": 20000000,  # Using higher gas limit as requested
                "gasPrice": w3.eth.gas_price,
                "nonce": nonce,
            }
        )
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(constructor_txn, private_key)
        print("✅ Transaction signed successfully")
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"📤 Transaction sent: {tx_hash.hex()}")
        
        # Wait for transaction receipt
        print("⏳ Waiting for confirmation...")
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        contract_address = tx_receipt.contractAddress
        print(f"Contract deployed at: {contract_address}")
        print(f"Transaction status: {tx_receipt.status}")
        print(f"Gas used: {tx_receipt.gasUsed}")
        
        # Verify contract code exists
        code = w3.eth.get_code(contract_address)
        code_exists = len(code) > 0
        print(f"Contract code exists: {code_exists}")
        print(f"Code size: {len(code)} bytes")
        
        if code_exists:
            # Save deployment info
            deployment_info = {
                "chain": chain_info["name"],
                "rpc": chain_info["rpc"],
                "chainId": chain_info["chain_id"],
                "contract": "IEMDreams",
                "address": contract_address,
                "deployer": account.address,
                "transactionHash": tx_hash.hex(),
                "abi": abi,
                "status": tx_receipt.status
            }
            
            filename = f"iem_memory_{chain_info['name'].lower().replace(' ', '_')}.json"
            with open(filename, "w") as f:
                json.dump(deployment_info, f, indent=2)
            print(f"📝 Deployment information saved to {filename}")
            
            return True
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

# Initialize compiler cache
deploy_to_chain.compiled_contract = None

# Install Solidity compiler
print("🔧 Installing Solidity compiler...")
install_solc("0.8.20")

# Try each chain
for chain in SKALE_CHAINS:
    success = deploy_to_chain(chain)
    if success:
        print(f"✨ Successfully deployed to {chain['name']}")
    else:
        print(f"❌ Failed to deploy to {chain['name']}")
    print("\n" + "="*50)
    time.sleep(2)  # Wait between attempts
