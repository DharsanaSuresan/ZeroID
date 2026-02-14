from merkle_tree import MerkleTree, sha256

credentials = [
    "Alice_degree",
    "Bob_degree",
    "Charlie_degree",
    "David_degree"
]

hashed = [sha256(c) for c in credentials]

tree = MerkleTree(hashed)

root = tree.get_root()
print("Merkle Root:", root)

index = 1
proof = tree.get_proof(index)

print("Proof:", proof)

valid = MerkleTree.verify_proof(
    hashed[index],
    proof,
    root,
    index
)

print("Proof Valid:", valid)

print("\nRevoking Bob (Delta Update)...")

revoked_hash = sha256("REVOKED")
tree.update_leaf(index, revoked_hash)

new_root = tree.get_root()
print("New Root:", new_root)
