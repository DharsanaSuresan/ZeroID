"""
blockchain_service.py
Centralized Web3 connection for the entire Django backend.
Import `get_contract()` wherever you need blockchain access.
"""

from web3 import Web3
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Find .env by walking up from this file
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

RPC_URL          = os.getenv("SEPOLIA_RPC_URL")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Load ABI
_abi_path = Path(__file__).parent / "contract_abi.json"
with open(_abi_path) as f:
    _raw = json.load(f)
_ABI = _raw.get("abi", _raw) if isinstance(_raw, dict) else _raw

# Single shared Web3 instance
w3 = Web3(Web3.HTTPProvider(RPC_URL))


def get_contract():
    """Return the ZeroIDMerkle contract instance."""
    return w3.eth.contract(
        address=Web3.to_checksum_address(CONTRACT_ADDRESS),
        abi=_ABI
    )


def get_merkle_root() -> str:
    """
    Fetch current Merkle root from Sepolia.
    Returns hex string without 0x prefix.
    Raises ConnectionError if not connected.
    """
    if not w3.is_connected():
        raise ConnectionError("Cannot connect to Sepolia RPC. Check SEPOLIA_RPC_URL in .env")
    root_bytes = get_contract().functions.merkleRoot().call()
    return root_bytes.hex()


def is_connected() -> bool:
    return w3.is_connected()