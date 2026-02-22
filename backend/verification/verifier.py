from backend.merkle.merkle_tree import verify_proof
from backend.blockchain.test_connection import w3, contract


def verify_credential(tree, index):

    # 1. Get leaf hash
    leaf_hash = tree.leaves[index]

    # 2. Generate proof
    proof = tree.get_proof(index)

    # 3. Fetch blockchain root
    blockchain_root_bytes = contract.functions.merkleRoot().call()
    blockchain_root = blockchain_root_bytes.hex()

    # remove 0x if present
    if blockchain_root.startswith("0x"):
        blockchain_root = blockchain_root[2:]

    # 4. Verify
    is_valid = verify_proof(leaf_hash, proof, blockchain_root)

    return is_valid