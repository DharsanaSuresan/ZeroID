# from web3 import Web3
# import json
# import os
# from pathlib import Path
# from dotenv import load_dotenv

# # Load .env from project root
# # load_dotenv(r"C:\Users\admin\Desktop\Major Project\.env")
# load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# RPC_URL          = os.getenv("SEPOLIA_RPC_URL")
# PRIVATE_KEY      = os.getenv("SEPOLIA_PRIVATE_KEY")
# CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# # Load ABI — try both filenames
# _base = Path(__file__).resolve().parent
# for name in ["contract_abi.json", "ZeroIDMerkle.json"]:
#     _p = _base / name
#     if _p.exists():
#         with open(_p) as f:
#             raw = json.load(f)
#         ABI = raw.get("abi", raw) if isinstance(raw, dict) else raw
#         break

# w3       = Web3(Web3.HTTPProvider(RPC_URL))
# ACCOUNT  = w3.eth.account.from_key(PRIVATE_KEY)
# contract = w3.eth.contract(
#     address=Web3.to_checksum_address(CONTRACT_ADDRESS),
#     abi=ABI
# )

# def send_root(root_hex: str) -> tuple:
#     root_bytes = bytes.fromhex(root_hex.replace("0x", ""))
#     nonce = w3.eth.get_transaction_count(ACCOUNT.address, "pending")
#     tx = contract.functions.updateMerkleRoot(root_bytes).build_transaction({
#         "from":     ACCOUNT.address,
#         "nonce":    nonce,
#         "gas":      200_000,
#         "gasPrice": w3.eth.gas_price,
#     })
#     signed   = ACCOUNT.sign_transaction(tx)
#     tx_hash  = w3.eth.send_raw_transaction(signed.raw_transaction)
#     receipt  = w3.eth.wait_for_transaction_receipt(tx_hash)
#     print(f"✅ Root updated | tx: {tx_hash.hex()} | gas: {receipt.gasUsed}")
#     return tx_hash.hex(), receipt.gasUsed


from web3 import Web3
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Find .env by walking up from this file's location
# _here = Path(__file__).resolve()
# for _parent in _here.parents:
#     if (_parent / ".env").exists():
#         load_dotenv(_parent / ".env")
#         break
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

# ✅ Correct env variable names matching .env
RPC_URL          = os.getenv("SEPOLIA_RPC_URL")
PRIVATE_KEY      = os.getenv("SEPOLIA_PRIVATE_KEY")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Load ABI
_abi_path = Path(__file__).parent / "contract_abi.json"
with open(_abi_path) as f:
    raw = json.load(f)
contract_abi = raw.get("abi", raw) if isinstance(raw, dict) else raw

w3       = Web3(Web3.HTTPProvider(RPC_URL))
contract = w3.eth.contract(
    address=Web3.to_checksum_address(CONTRACT_ADDRESS),
    abi=contract_abi
)

def send_root(new_root_hex: str) -> dict:
    """
    Push new Merkle root to Sepolia contract.
    Returns dict with tx_hash and gas_used.
    """
    account = w3.eth.account.from_key(PRIVATE_KEY)
    nonce   = w3.eth.get_transaction_count(account.address, "pending")

    tx = contract.functions.updateMerkleRoot(
        Web3.to_bytes(hexstr=new_root_hex)
    ).build_transaction({
        "from":     account.address,
        "nonce":    nonce,
        "gas":      300_000,
        "gasPrice": w3.eth.gas_price,
    })

    signed  = account.sign_transaction(tx)
    tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    print(f"✅ Root updated | tx: {tx_hash.hex()} | gas: {receipt.gasUsed}")

    return {
        "tx_hash":       tx_hash.hex(),
        "gas_used":      receipt.gasUsed,
        "block_number":  receipt.blockNumber,
        "network":       "sepolia",
        "contract_address": CONTRACT_ADDRESS,
    }