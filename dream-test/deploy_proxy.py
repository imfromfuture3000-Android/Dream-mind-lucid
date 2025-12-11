from web3 import Web3
from eth_account import Account
from solcx import compile_standard, install_solc
import json

# Connect to Europa Mainnet (has highest sFUEL balance)
RPC_URL = "https://mainnet.skalenodes.com/v1/elated-tan-skat"
CHAIN_ID = 2046399126

print("🔌 Connecting to SKALE Europa...")
w3 = Web3(Web3.HTTPProvider(RPC_URL))
assert w3.is_connected(), "Failed to connect to network"
print("✅ Connected successfully")

# Account setup
private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
account = Account.from_key(private_key)
print(f"📝 Using account: {account.address}")

# Check balance
balance = w3.eth.get_balance(account.address)
print(f"💰 Balance: {w3.from_wei(balance, 'ether')} sFUEL")

# Contract source with proxy pattern and access control
contract_source = """
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract IEMDreamsProxy {
    address public owner;
    address public implementation;
    mapping(address => bool) public admins;
    mapping(address => uint256) public dreamCount;
    
    event DreamRecorded(address indexed dreamer, string dream, uint256 count);
    event AdminAdded(address indexed admin);
    event AdminRemoved(address indexed admin);
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    modifier onlyAdmin() {
        require(admins[msg.sender] || msg.sender == owner, "Only admin or owner");
        _;
    }
    
    constructor() {
        owner = msg.sender;
        admins[msg.sender] = true;
    }
    
    function setImplementation(address _implementation) public onlyOwner {
        implementation = _implementation;
    }
    
    function addAdmin(address admin) public onlyOwner {
        admins[admin] = true;
        emit AdminAdded(admin);
    }
    
    function removeAdmin(address admin) public onlyOwner {
        require(admin != owner, "Cannot remove owner");
        admins[admin] = false;
        emit AdminRemoved(admin);
    }
    
    function recordDream(string memory dream) public {
        dreamCount[msg.sender]++;
        emit DreamRecorded(msg.sender, dream, dreamCount[msg.sender]);
        
        // If implementation exists, forward the call
        if (implementation != address(0)) {
            (bool success,) = implementation.call(
                abi.encodeWithSignature("recordDream(string)", dream)
            );
            require(success, "Forward call failed");
        }
    }
    
    function getDreamCount(address dreamer) public view returns (uint256) {
        return dreamCount[dreamer];
    }
    
    function isAdmin(address account) public view returns (bool) {
        return admins[account];
    }
    
    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }
}
"""

print("\n🔨 Compiling contract...")
install_solc("0.8.20")

compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"IEMDreamsProxy.sol": {"content": contract_source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode"]}
            }
        }
    },
    solc_version="0.8.20"
)

# Get bytecode and ABI
contract_interface = compiled["contracts"]["IEMDreamsProxy.sol"]["IEMDreamsProxy"]
bytecode = contract_interface["evm"]["bytecode"]["object"]
abi = contract_interface["abi"]

# Create contract
Contract = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get nonce
nonce = w3.eth.get_transaction_count(account.address)

print("\n⚡ Preparing transaction...")
# Build constructor transaction
constructor_txn = Contract.constructor().build_transaction({
    "chainId": CHAIN_ID,
    "gas": 1000000,
    "gasPrice": w3.eth.gas_price,
    "nonce": nonce,
})

print("✍️ Signing transaction...")
signed_txn = w3.eth.account.sign_transaction(constructor_txn, private_key)

print("📤 Sending transaction...")
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"Transaction hash: {tx_hash.hex()}")

print("\n⏳ Waiting for confirmation...")
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
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
        "contract": "IEMDreamsProxy",
        "address": contract_address,
        "network": "SKALE Europa Mainnet",
        "rpc": RPC_URL,
        "chainId": CHAIN_ID,
        "owner": account.address,
        "transactionHash": tx_hash.hex(),
        "abi": abi,
        "features": {
            "accessControl": True,
            "proxyCapability": True,
            "dreamCounting": True
        }
    }
    
    with open("skale_proxy_deployment.json", "w") as f:
        json.dump(deployment_info, f, indent=2)
    print("📝 Deployment information saved to skale_proxy_deployment.json")
    
    # Create contract instance
    contract = w3.eth.contract(address=contract_address, abi=abi)
    
    # Verify ownership and admin status
    owner = contract.functions.owner().call()
    is_admin = contract.functions.isAdmin(account.address).call()
    
    print("\nContract verification:")
    print(f"Owner: {owner}")
    print(f"Deployer is admin: {is_admin}")
    
    print("\n📋 Contract Usage Instructions:")
    print("1. Set implementation address:")
    print(f"   - Call setImplementation(address) to link to existing contract")
    print("2. Admin Management:")
    print("   - addAdmin(address) to add new admins")
    print("   - removeAdmin(address) to remove admins")
    print("3. Record Dreams:")
    print("   - recordDream(string) to record dreams")
    print("   - getDreamCount(address) to check dream count")
    print("4. Ownership:")
    print("   - transferOwnership(address) to transfer contract ownership")
else:
    print("\n❌ Contract deployment failed!")
