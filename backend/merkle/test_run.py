from backend.merkle.merkle_tree import MerkleTree
from backend.merkle.batch_revocation import BatchRevocation

# create fake users
data = [f"user{i}" for i in range(16)]

# build tree
tree = MerkleTree(data)

print("Initial Root:", tree.get_root())

# ---- Delta revoke ----
delta_metrics = tree.delta_revoke(3)
print("Delta revoke hash operations:", delta_metrics.hash_operations)
print("Delta revoke time (ms):", delta_metrics.duration_ms())

# ---- Batch revoke ----
batch = BatchRevocation(tree)
batch.add_to_batch(1)
batch.add_to_batch(5)
batch.add_to_batch(7)

root, batch_metrics = batch.process_batch()
print("Batch revoke hash operations:", batch_metrics.hash_operations)
print("Batch revoke time (ms):", batch_metrics.duration_ms())
