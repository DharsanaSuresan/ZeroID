from backend.merkle.merkle_tree import MerkleTree, verify_proof

users = ["A", "B", "C", "D"]
tree = MerkleTree(users)

index = 2
leaf_hash = tree.leaves[index]
proof = tree.get_proof(index)
root = tree.get_root()

print("Proof valid:", verify_proof(leaf_hash, proof, root))