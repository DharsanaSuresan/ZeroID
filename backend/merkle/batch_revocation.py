# from merkle_tree import MerkleTree, sha256


# class BatchRevocationManager:

#     def __init__(self, merkle_tree: MerkleTree):
#         self.tree = merkle_tree
#         self.revocation_queue = []

#     # -----------------------------------
#     # Add credential index to revoke later
#     # -----------------------------------
#     def queue_revocation(self, index):
#         self.revocation_queue.append(index)

#     # -----------------------------------
#     # Process ALL revocations together
#     # -----------------------------------
#     def process_batch(self):

#     if not self.revocation_queue:
#         return self.tree.get_root(), None

#     revoked_hash = sha256("REVOKED")
#     unique_indexes = sorted(set(self.revocation_queue))

#     self.tree.metrics.start()

#     for index in unique_indexes:
#         self.tree.update_leaf(index, revoked_hash)

#     self.tree.metrics.stop()

#     self.revocation_queue.clear()
#     return self.tree.get_root(), self.tree.metrics


#         # # Return NEW Merkle Root (single blockchain update)
#         # return self.tree.get_root()


from .merkle_tree import MerkleTree, sha256


class BatchRevocation:

    def __init__(self, tree):
        self.tree = tree
        self.revocation_queue = []

    def add_to_batch(self, index):
        self.revocation_queue.append(index)

    def process_batch(self):

        if not self.revocation_queue:
            return self.tree.get_root(), None

        revoked_hash = sha256("REVOKED")
        unique_indexes = sorted(set(self.revocation_queue))

        # start measurement once
        self.tree.metrics.start()

        for index in unique_indexes:
            self.tree.update_leaf(index, revoked_hash)

        self.tree.metrics.stop()

        self.revocation_queue.clear()
        return self.tree.get_root(), self.tree.metrics
