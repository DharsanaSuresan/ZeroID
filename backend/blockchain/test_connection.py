# # from web3 import Web3
# # import json

# # w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))

# # print("Connected:", w3.is_connected())

# # CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"

# # with open("blockchain\contract_abi.json") as f:
# #     abi = json.load(f)

# # contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=abi)
# # root = contract.functions.merkleRoot().call()

# # # root = contract.functions.getRoot().call()
# # print("Current Root on Chain:", root)

# from web3 import Web3
# import json
# import os
# from pathlib import Path
# from dotenv import load_dotenv

# # Load .env from project root
# # load_dotenv(r"C:\Users\admin\Desktop\Major Project\.env")
# load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# RPC_URL          = os.getenv("SEPOLIA_RPC_URL")
# CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# # Load ABI — try both filenames
# _base = Path(__file__).resolve().parent
# for name in ["contract_abi.json", "ZeroIDMerkle.json"]:
#     _p = _base / name
#     if _p.exists():
#         with open(_p) as f:
#             raw = json.load(f)
#         abi = raw.get("abi", raw) if isinstance(raw, dict) else raw
#         break

# w3 = Web3(Web3.HTTPProvider(RPC_URL))
# print("Connected:", w3.is_connected())

# contract = w3.eth.contract(
#     address=Web3.to_checksum_address(CONTRACT_ADDRESS),
#     abi=abi
# )

# root = contract.functions.merkleRoot().call()
# admin = contract.functions.admin().call()
# print("Current Root  :", root.hex())
# print("Admin Address :", admin)


"""
test_connection.py
Quick test to verify Sepolia connection and contract are working.
Run from backend/: python -m blockchain.test_connection
"""
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
from blockchain.blockchain_service import w3, get_contract, get_merkle_root, CONTRACT_ADDRESS

print("Connected     :", w3.is_connected())
print("Contract Addr :", CONTRACT_ADDRESS)

try:
    root  = get_merkle_root()
    admin = get_contract().functions.admin().call()
    print("Merkle Root   :", root)
    print("Admin Address :", admin)
except Exception as e:
    print("Error         :", e)