from backend.merkle.merkle_tree import MerkleTree
from backend.blockchain.send_root import send_root
from backend.verification.verifier import verify_credential

users = ["A", "B", "C", "D"]
tree = MerkleTree(users)

# send initial root to blockchain
send_root("0x" + tree.get_root())

# verify user at index 2
print("Before revoke:", verify_credential(tree, 2))

# revoke user at index 2
tree.delta_revoke(2)

# update blockchain root
send_root("0x" + tree.get_root())

# verify again
print("After revoke:", verify_credential(tree, 2))