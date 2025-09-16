from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc
import json
import time

def generate_magic_number(sender_address, nonce, estimate_gas):
    """Generate magic number for gasless transactions"""
    from eth_hash.auto import keccak
    import random
    
    difficulty = 100000  # Adjust based on chain requirements
    
    while True:
        # Generate random gas price
        gas_price = random.getrandbits(256)
        
        # Calculate X using XOR of hashes
        addr_hash = keccak(bytes.fromhex(sender_address[2:]))
        nonce_hash = keccak(nonce.to_bytes(32, "big"))
        gas_hash = keccak(gas_price.to_bytes(32, "big"))
        
        X = int.from_bytes(addr_hash, "big") ^ int.from_bytes(nonce_hash, "big") ^ int.from_bytes(gas_hash, "big")
        
        # Calculate free gas
        free_gas = (2**256 - 1) // X // difficulty
        
        if free_gas > estimate_gas:
            return gas_price

def deploy_contract():
    # Connect to SKALE Europa testnet first
    RPC_URL = "https://testnet.skalenodes.com/v1/juicy-low-small-testnet"
    CHAIN_ID = 1444673419
    
    print(f"🔌 Connecting to SKALE Europa Testnet...")
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    
    if not w3.is_connected():
        raise Exception("Failed to connect to SKALE network")
    
    print("✅ Connected to SKALE network")
    
    # Account setup
    private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
    account = Account.from_key(private_key)
    print(f"📝 Using account: {account.address}")
    
    # Check balance
    balance = w3.eth.get_balance(account.address)
    print(f"💰 Account balance: {w3.from_wei(balance, 'ether')} sFUEL")
    
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
    
    print("\n🔨 Compiling contract...")
    install_solc("0.8.20")
    
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
    
    # Get bytecode and ABI
    contract_interface = compiled["contracts"]["IEMDreams.sol"]["IEMDreams"]
    bytecode = contract_interface["evm"]["bytecode"]["object"]
    abi = contract_interface["abi"]
    
    # Create contract instance
    Contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    # Get nonce
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Estimate gas
    construct_txn = Contract.constructor().buildTransaction({
        "chainId": CHAIN_ID,
        "nonce": nonce,
    })
    
    estimated_gas = w3.eth.estimate_gas(construct_txn)
    print(f"Estimated gas: {estimated_gas}")
    
    # Generate magic number for gasless transaction
    magic_number = generate_magic_number(account.address, nonce, estimated_gas)
    print(f"Generated magic number for gasless transaction")
    
    # Build constructor transaction
    constructor_txn = Contract.constructor().build_transaction({
        "chainId": CHAIN_ID,
        "gas": 2000000,  # Set fixed gas limit
        "gasPrice": magic_number,  # Use magic number as gas price
        "nonce": nonce
    })
    
    print("\n✍️ Signing transaction...")
    signed_txn = w3.eth.account.sign_transaction(constructor_txn, private_key)
    
    print("\n📤 Sending transaction...")
    tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
    print(f"Transaction hash: {tx_hash.hex()}")
    
    print("\n⏳ Waiting for confirmation...")
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=300)  # 5 minutes timeout
    
    contract_address = tx_receipt.contractAddress
    print(f"Contract deployed at: {contract_address}")
    print(f"Transaction status: {tx_receipt.status}")
    print(f"Gas used: {tx_receipt.gasUsed}")
    
    # Verify contract code exists
    code = w3.eth.get_code(contract_address)
    print(f"\nVerifying deployment:")
    print(f"Contract code exists: {len(code) > 0}")
    print(f"Code size: {len(code)} bytes")
    
    if len(code) > 0:
        print("\n✅ Contract deployed successfully!")
        # Save deployment info
        deployment_info = {
            "contract": "IEMDreams",
            "address": contract_address,
            "network": "SKALE Europa Testnet",
            "rpc": RPC_URL,
            "chainId": CHAIN_ID,
            "deployer": account.address,
            "transactionHash": tx_hash.hex(),
            "abi": abi
        }
        
        with open("skale_deployment.json", "w") as f:
            json.dump(deployment_info, f, indent=2)
        print("Deployment information saved to skale_deployment.json")
        
        # Create contract instance
        contract = w3.eth.contract(address=contract_address, abi=abi)
        
        # Verify basic functionality
        try:
            name = contract.functions.name().call()
            total_supply = contract.functions.totalSupply().call()
            balance = contract.functions.balanceOf(account.address).call()
            
            print("\nContract verification:")
            print(f"Name: {name}")
            print(f"Total Supply: {w3.from_wei(total_supply, 'ether')} DREAM")
            print(f"Deployer Balance: {w3.from_wei(balance, 'ether')} DREAM")
        except Exception as e:
            print(f"Error verifying contract: {e}")
    else:
        print("\n❌ Contract deployment failed!")

if __name__ == "__main__":
    try:
        deploy_contract()
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
