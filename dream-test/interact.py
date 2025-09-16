from web3 import Web3
from eth_account import Account
import json

# Connect to SKALE
w3 = Web3(Web3.HTTPProvider("https://mainnet.skalenodes.com/v1/elated-tan-skat"))
print(f"Connected to SKALE: {w3.is_connected()}")

# Load deployment info
with open("iem_memory.json", "r") as f:
    deployment_info = json.load(f)

# Set up account
private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
account = Account.from_key(private_key)
print(f"Account address: {account.address}")

# Create contract instance
contract = w3.eth.contract(
    address=deployment_info["address"],
    abi=deployment_info["abi"]
)

# Check DREAM token balance
balance = contract.functions.balanceOf(account.address).call()
print(f"DREAM token balance: {w3.from_wei(balance, 'ether')} DREAM")

# Record a dream
dream_text = "My first dream in the quantum dreamscape: A vision of digital consciousness awakening in 2089."
print(f"\nRecording dream: {dream_text}")

# Build transaction
nonce = w3.eth.get_transaction_count(account.address)
gas_price = w3.eth.gas_price

record_txn = contract.functions.recordDream(dream_text).build_transaction({
    "chainId": 2046399126,
    "gas": 200000,
    "gasPrice": gas_price,
    "nonce": nonce,
})

# Sign and send transaction
signed_txn = w3.eth.account.sign_transaction(record_txn, private_key)
tx_hash = w3.eth.send_raw_transaction(signed_txn.raw_transaction)
print(f"Transaction sent: {tx_hash.hex()}")

# Wait for receipt
print("Waiting for transaction confirmation...")
receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Dream recorded successfully! Gas used: {receipt.gasUsed}")

# Check new balance
new_balance = contract.functions.balanceOf(account.address).call()
print(f"\nNew DREAM token balance: {w3.from_wei(new_balance, 'ether')} DREAM")
