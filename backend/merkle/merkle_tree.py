# import hashlib

# import time

# class OperationMetrics:
#     def __init__(self):
#         self.hash_operations = 0
#         self.start_time = 0
#         self.end_time = 0

#     def start(self):
#         self.hash_operations = 0
#         self.start_time = time.time()

#     def stop(self):
#         self.end_time = time.time()

#     def duration_ms(self):
#         return (self.end_time - self.start_time) * 1000


# def sha256(data, metrics=None):
#     if metrics:
#         metrics.hash_operations += 1
#     return hashlib.sha256(data.encode()).hexdigest()


# class MerkleTree:

#     def __init__(self, leaves):
#         self.leaves = leaves
#         self.levels = []
#         self.metrics = OperationMetrics()
#         self.build_tree()
        

#     def build_tree(self):
#         current_level = self.leaves
#         self.levels = [current_level]

#         while len(current_level) > 1:
#             next_level = []

#             for i in range(0, len(current_level), 2):
#                 left = current_level[i]
#                 right = current_level[i + 1] if i + 1 < len(current_level) else left

#                 combined_hash = sha256(left + right, self.metrics)
#                 next_level.append(combined_hash)

#             current_level = next_level
#             self.levels.append(current_level)

#     def get_root(self):
#         return self.levels[-1][0]

#     def get_proof(self, index):
#         proof = []
#         current_index = index

#         for level in self.levels[:-1]:
#             sibling_index = current_index ^ 1

#             if sibling_index < len(level):
#                 proof.append(level[sibling_index])
#             else:
#                 proof.append(level[current_index])

#             current_index = current_index // 2

#         return proof

#     @staticmethod
#     def verify_proof(leaf, proof, root, index):
#         computed_hash = leaf

#         for sibling in proof:
#             if index % 2 == 0:
#                 computed_hash = sha256(computed_hash + sibling)
#             else:
#                 computed_hash = sha256(sibling + computed_hash)

#             index = index // 2

#         return computed_hash == root

#     # DELTA UPDATE (O(log n))
#     def update_leaf(self, index, new_leaf_hash):
#     self.levels[0][index] = new_leaf_hash
#     current_index = index

#     # propagate change to root
#     for level in range(len(self.levels) - 1):

#         parent_index = current_index // 2
#         left_index = parent_index * 2
#         right_index = left_index + 1

#         left = self.levels[level][left_index]
#         right = (
#             self.levels[level][right_index]
#             if right_index < len(self.levels[level])
#             else left
#         )

#         new_parent_hash = sha256(left + right, self.metrics)
#         self.levels[level + 1][parent_index] = new_parent_hash

#         current_index = parent_index

# `   def delta_revoke(self, index):
#         revoked_hash = sha256("REVOKED")
#         self.metrics.start()
#         self.update_leaf(index, revoked_hash)
#         self.metrics.stop()
#         return self.metrics

import hashlib
import time


# ---------------- METRICS ----------------
class OperationMetrics:
    def __init__(self):
        self.hash_operations = 0
        self.start_time = 0
        self.end_time = 0

    def start(self):
        self.hash_operations = 0
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def duration_ms(self):
        return (self.end_time - self.start_time) * 1000


# ---------------- HASH ----------------
def sha256(data, metrics=None):
    if metrics:
        metrics.hash_operations += 1
    return hashlib.sha256(data.encode()).hexdigest()


# ---------------- MERKLE TREE ----------------
class MerkleTree:

    def __init__(self, leaves):
        self.metrics = OperationMetrics()
        self.leaves = [sha256(x) for x in leaves]
        self.levels = []
        self.build_tree()

    # Build initial tree (NOT counted in experiments)
    def build_tree(self):
        self.levels = [self.leaves[:]]

        current = self.leaves[:]
        while len(current) > 1:
            next_level = []
            for i in range(0, len(current), 2):
                left = current[i]
                right = current[i + 1] if i + 1 < len(current) else left
                next_level.append(sha256(left + right))  # no metrics here
            self.levels.append(next_level)
            current = next_level

    def get_root(self):
        return self.levels[-1][0]

    # ---------- DELTA UPDATE ----------
    def update_leaf(self, index, new_hash):
        self.levels[0][index] = new_hash
        current_index = index

        for level in range(len(self.levels) - 1):
            parent_index = current_index // 2

            left_index = parent_index * 2
            right_index = left_index + 1

            left = self.levels[level][left_index]
            right = self.levels[level][right_index] if right_index < len(self.levels[level]) else left

            parent_hash = sha256(left + right, self.metrics)
            self.levels[level + 1][parent_index] = parent_hash

            current_index = parent_index

    # public function for delta revocation experiment
    def delta_revoke(self, index):
        revoked_hash = sha256("REVOKED")
        self.metrics.start()
        self.update_leaf(index, revoked_hash)
        self.metrics.stop()
        return self.metrics

        # ---------- PROOF GENERATION ----------
    def get_proof(self, index):
        proof = []
        current_index = index

        for level in range(len(self.levels) - 1):
            level_nodes = self.levels[level]

            sibling_index = current_index ^ 1  # toggle last bit

            if sibling_index < len(level_nodes):
                sibling_hash = level_nodes[sibling_index]
            else:
                sibling_hash = level_nodes[current_index]

            is_left = sibling_index < current_index
            proof.append((sibling_hash, is_left))

            current_index = current_index // 2

        return proof
    
    
def verify_proof(leaf_hash, proof, root):

    computed_hash = leaf_hash

    for sibling_hash, is_left in proof:
        if is_left:
            computed_hash = sha256(sibling_hash + computed_hash)
        else:
            computed_hash = sha256(computed_hash + sibling_hash)

    return computed_hash == root

