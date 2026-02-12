from merkle_tree import MerkleTree, sha256


class BatchRevocationManager:

    def __init__(self, merkle_tree: MerkleTree):
        self.tree = merkle_tree
        self.revocation_queue = []

    # -----------------------------------
    # Add credential index to revoke later
    # -----------------------------------
    def queue_revocation(self, index):
        self.revocation_queue.append(index)

    # -----------------------------------
    # Process ALL revocations together
    # -----------------------------------
    def process_batch(self):

        if not self.revocation_queue:
            print("No revocations to process.")
            return self.tree.get_root()

        print(f"Processing {len(self.revocation_queue)} revocations in batch...")

        revoked_hash = sha256("REVOKED")

        # Sort indexes for stable processing
        unique_indexes = sorted(set(self.revocation_queue))

        for index in unique_indexes:
            self.tree.update_leaf(index, revoked_hash)

        # Clear queue after processing
        self.revocation_queue.clear()

        # Return NEW Merkle Root (single blockchain update)
        return self.tree.get_root()
