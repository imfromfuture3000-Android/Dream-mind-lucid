from web3 import Web3

# Connect to SKALE
w3 = Web3(Web3.HTTPProvider('https://mainnet.skalenodes.com/v1/elated-tan-skat'))
print(f'Connected to SKALE: {w3.is_connected()}')

# Check balance
address = '0x4B1a58A3057d03888510d93B52ABad9Fee9b351d'
balance = w3.eth.get_balance(address)
print(f'Balance: {w3.from_wei(balance, "ether")} SKALE')
