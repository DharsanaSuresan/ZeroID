from merkle_tree import MerkleTree, sha256
from batch_revocation import BatchRevocationManager

credentials = [
    "Alice_degree",
    "Bob_degree",
    "Charlie_degree",
    "David_degree",
    "Eva_degree"
]

hashed = [sha256(c) for c in credentials]

tree = MerkleTree(hashed)

print("Original Root:", tree.get_root())

# Initialize batch manager
batch = BatchRevocationManager(tree)

# Queue multiple revocations
batch.queue_revocation(1)  # Bob
batch.queue_revocation(3)  # David

# Process batch revocation
new_root = batch.process_batch()

print("New Root After Batch Revocation:", new_root)
