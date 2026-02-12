import hashlib

def sha256(data):
    return hashlib.sha256(data.encode()).hexdigest()


class MerkleTree:

    def __init__(self, leaves):
        self.leaves = leaves
        self.levels = []
        self.build_tree()

    def build_tree(self):
        current_level = self.leaves
        self.levels = [current_level]

        while len(current_level) > 1:
            next_level = []

            for i in range(0, len(current_level), 2):
                left = current_level[i]
                right = current_level[i + 1] if i + 1 < len(current_level) else left

                combined_hash = sha256(left + right)
                next_level.append(combined_hash)

            current_level = next_level
            self.levels.append(current_level)

    def get_root(self):
        return self.levels[-1][0]

    def get_proof(self, index):
        proof = []
        current_index = index

        for level in self.levels[:-1]:
            sibling_index = current_index ^ 1

            if sibling_index < len(level):
                proof.append(level[sibling_index])
            else:
                proof.append(level[current_index])

            current_index = current_index // 2

        return proof

    @staticmethod
    def verify_proof(leaf, proof, root, index):
        computed_hash = leaf

        for sibling in proof:
            if index % 2 == 0:
                computed_hash = sha256(computed_hash + sibling)
            else:
                computed_hash = sha256(sibling + computed_hash)

            index = index // 2

        return computed_hash == root

    # DELTA UPDATE (O(log n))
    def update_leaf(self, index, new_leaf_hash):

        self.levels[0][index] = new_leaf_hash
        current_index = index

        for level in range(len(self.levels) - 1):
            parent_index = current_index // 2

            left_index = parent_index * 2
            right_index = left_index + 1

            left = self.levels[level][left_index]
            right = (
                self.levels[level][right_index]
                if right_index < len(self.levels[level])
                else left
            )

            new_parent_hash = sha256(left + right)

            self.levels[level + 1][parent_index] = new_parent_hash

            current_index = parent_index
