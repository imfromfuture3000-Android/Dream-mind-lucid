"""
Submit a simple lucid block header to the ConsensusCoordinator contract.
Configure WEB3_RPC, COORDINATOR_ADDRESS, and PRIVATE_KEY env vars.
"""
import os
import sys
from web3 import Web3

RPC = os.environ.get("WEB3_RPC", "http://127.0.0.1:8545")
COORDINATOR = os.environ.get("COORDINATOR_ADDRESS")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")

if COORDINATOR is None:
    print("Set COORDINATOR_ADDRESS env var to ConsensusCoordinator contract address")
    sys.exit(1)

w3 = Web3(Web3.HTTPProvider(RPC))
if not w3.is_connected():
    print("RPC not reachable", RPC)
    sys.exit(1)

ABI = [
    {
        "inputs": [
            {"internalType": "uint64", "name": "dreamSequenceId", "type": "uint64"},
            {"internalType": "uint32", "name": "dreamRecordCount", "type": "uint32"},
            {"internalType": "bytes32", "name": "previousLucidHash", "type": "bytes32"},
            {"internalType": "bytes32", "name": "lucidHash", "type": "bytes32"},
            {"internalType": "address", "name": "envisioner", "type": "address"},
            {"internalType": "bytes", "name": "lucidityProof", "type": "bytes"}
        ],
        "name": "finalize",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

coord = w3.eth.contract(address=Web3.to_checksum_address(COORDINATOR), abi=ABI)


def finalize_header(seq: int, prev: bytes, lucid: bytes, envisioner: str, proof: bytes):
    acct = w3.eth.account.from_key(PRIVATE_KEY)
    nonce = w3.eth.get_transaction_count(acct.address)
    txn = coord.functions.finalize(seq, 0, prev, lucid, Web3.to_checksum_address(envisioner), proof).build_transaction({
        "chainId": w3.eth.chain_id,
        "gas": 400000,
        "gasPrice": w3.to_wei('1', 'gwei'),
        "nonce": nonce,
    })
    signed = acct.sign_transaction(txn)
    txhash = w3.eth.send_raw_transaction(signed.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(txhash)
    print("Finalized in tx", receipt.transactionHash.hex())
    return receipt


if __name__ == '__main__':
    # Demo values; replace before use
    seq = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    prev = bytes(32)
    lucid = Web3.keccak(text=f"lucid-{seq}")
    envisioner = w3.eth.accounts[0]
    proof = b""  # placeholder
    finalize_header(seq, prev, lucid, envisioner, proof)
