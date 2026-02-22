from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

PRIVATE_KEY = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
ACCOUNT = w3.eth.account.from_key(PRIVATE_KEY)

CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

# with open("backend/blockchain/contract_abi.json") as f:
with open("blockchain/contract_abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)


def send_root(root_hex):

    root_bytes = Web3.to_bytes(hexstr=root_hex)

    nonce = w3.eth.get_transaction_count(ACCOUNT.address)

    tx = contract.functions.updateMerkleRoot(root_bytes).build_transaction({
        "from": ACCOUNT.address,
        "nonce": nonce,
        "gas": 3000000,
        "gasPrice": w3.to_wei("1", "gwei")
    })

    signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)


    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print("Transaction Hash:", tx_hash.hex())
    print("Gas Used:", receipt.gasUsed)

    return receipt.gasUsed
