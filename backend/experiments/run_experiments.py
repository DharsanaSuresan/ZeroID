import csv
import os
from backend.config.settings import BASE_DIR
from backend.merkle.merkle_tree import MerkleTree
from backend.merkle.batch_revocation import BatchRevocation
from backend.experiments.dataset_generator import generate_users
from backend.blockchain.send_root import send_root 


DATASET_SIZES = [100, 500, 1000, 5000]
def run():

    BASE_DIR = os.path.dirname(__file__)
    file_path = os.path.join(BASE_DIR, "results.csv")

    with open(file_path, "w", newline="") as f:

        writer = csv.writer(f)
        writer.writerow([
            "users",
            "delta_hash_ops",
            "delta_time_ms",
            "batch_hash_ops",
            "batch_time_ms",
            "gas_used"
        ])

        for size in DATASET_SIZES:

            print("Running experiment for", size, "users")

            users = generate_users(size)

            # -------- DELTA TEST --------
            tree_delta = MerkleTree(users)
            delta_metrics = tree_delta.delta_revoke(size // 2)

            # -------- BATCH TEST --------
            tree_batch = MerkleTree(users)
            batch = BatchRevocation(tree_batch)

            for i in range(10):
                batch.add_to_batch((size // 2 + i) % size)

            _, batch_metrics = batch.process_batch()
            print("Merkle Root:",tree_batch.get_root())

            #-------BLOCKCHAIN COST--------
            gas_used =send_root("0x"+ tree_batch.get_root())

            writer.writerow([
                size,
                delta_metrics.hash_operations,
                delta_metrics.duration_ms(),
                batch_metrics.hash_operations,
                batch_metrics.duration_ms(),
                gas_used
            ])

    print("Experiments completed → results.csv created")


# print("Experiments completed → results.csv created")

if __name__ == "__main__":
    run()
