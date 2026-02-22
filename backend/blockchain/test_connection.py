from web3 import Web3
import json

w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

print("Connected:", w3.is_connected())

CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

with open("backend/blockchain/contract_abi.json") as f:
    abi = json.load(f)

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
root = contract.functions.merkleRoot().call()

# root = contract.functions.getRoot().call()
print("Current Root on Chain:", root)
