from web3 import Web3
from eth_account import Account

# Connect to SKALE
w3 = Web3(Web3.HTTPProvider("https://mainnet.skalenodes.com/v1/elated-tan-skat"))
print(f"Connected to SKALE: {w3.is_connected()}")

# Set up account
private_key = "1c734d612698d2f21bc54a6ed073f7cfa6920d02f346a7f15c7f0c5310cc0108"
account = Account.from_key(private_key)
print(f"Account address: {account.address}")

# Check balance
balance = w3.eth.get_balance(account.address)
print(f"Balance: {w3.from_wei(balance, 'ether')} SKALE")
