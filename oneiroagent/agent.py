"""
Simple OneiroAgent simulator for interacting with the DreamRecords contract.
This script demonstrates submitting a dream and listening for DreamSubmitted events.

Requirements (install into a virtualenv):
    pip install -r requirements.txt

Configure WEB3_RPC and CONTRACT_ADDRESS environment variables before running.
"""
import os
import sys
import time
from web3 import Web3
from eth_abi import encode_single

RPC = os.environ.get("WEB3_RPC", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = os.environ.get("CONTRACT_ADDRESS")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")  # optional: for sending transactions

if CONTRACT_ADDRESS is None:
    print("Set CONTRACT_ADDRESS env var to the deployed DreamRecords contract address.")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC))
if not w3.is_connected():
    print("Failed to connect to RPC:", RPC)
    sys.exit(1)

# ABI minimal for DreamRecords
ABI = [
    {
        "anonymous": False,
        "inputs": [
            {"indexed": True, "internalType": "address", "name": "dreamer", "type": "address"},
            {"indexed": True, "internalType": "uint256", "name": "dreamId", "type": "uint256"},
            {"indexed": False, "internalType": "bytes", "name": "dreamData", "type": "bytes"}
        ],
        "name": "DreamSubmitted",
        "type": "event"
    },
    {
        "inputs": [{"internalType": "bytes", "name": "dreamData", "type": "bytes"}],
        "name": "submitDream",
        "outputs": [{"internalType": "uint256", "name": "dreamId", "type": "uint256"}],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=ABI)


def submit_dream(data: bytes):
    acct = w3.eth.account.from_key(PRIVATE_KEY) if PRIVATE_KEY else None
    if acct is None:
        # Use first unlocked account if available (local node)
        try:
            sender = w3.eth.accounts[0]
            tx = contract.functions.submitDream(data).transact({"from": sender})
            receipt = w3.eth.wait_for_transaction_receipt(tx)
            print("Submitted dream in tx", receipt.transactionHash.hex())
            return receipt
        except Exception as e:
            print("Error submitting dream (no PRIVATE_KEY and no unlocked account):", e)
            raise
    else:
        nonce = w3.eth.get_transaction_count(acct.address)
        txn = contract.functions.submitDream(data).build_transaction({
            "chainId": w3.eth.chain_id,
            "gas": 300000,
            "gasPrice": w3.to_wei('1', 'gwei'),
            "nonce": nonce,
        })
        signed = acct.sign_transaction(txn)
        txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
        receipt = w3.eth.wait_for_transaction_receipt(txhash)
        print("Submitted dream in tx", receipt.transactionHash.hex())
        return receipt


def listen_events(poll_interval=2):
    print("Listening for DreamSubmitted events...")
    event_filter = contract.events.DreamSubmitted.create_filter(fromBlock='latest')
    try:
        while True:
            for ev in event_filter.get_new_entries():
                print("Event: dreamer=", ev['args']['dreamer'], "dreamId=", ev['args']['dreamId'])
            time.sleep(poll_interval)
    except KeyboardInterrupt:
        print("Stopping listener")


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'submit':
        payload = b"Example dream data from OneiroAgent"
        submit_dream(payload)
    else:
        listen_events()
