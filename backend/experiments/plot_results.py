import os
import pandas as pd
import matplotlib.pyplot as plt

# locate csv inside experiments folder
BASE_DIR = os.path.dirname(__file__)
file_path = os.path.join(BASE_DIR, "results.csv")

data = pd.read_csv(file_path)

# ---------------- Time Graph ----------------
plt.figure()
plt.plot(data["users"], data["delta_time_ms"], marker='o', label="Delta Revocation")
plt.plot(data["users"], data["batch_time_ms"], marker='o', label="Batch Revocation")
plt.xlabel("Number of Users")
plt.ylabel("Time (ms)")
plt.title("Revocation Time vs Dataset Size")
plt.legend()
plt.grid(True)

time_graph = os.path.join(BASE_DIR, "time_comparison.png")
plt.savefig(time_graph)
plt.close()

# ---------------- Hash Graph ----------------
plt.figure()
plt.plot(data["users"], data["delta_hash_ops"], marker='o', label="Delta Revocation")
plt.plot(data["users"], data["batch_hash_ops"], marker='o', label="Batch Revocation")
plt.xlabel("Number of Users")
plt.ylabel("Hash Computations")
plt.title("Hash Operations vs Dataset Size")
plt.legend()
plt.grid(True)

hash_graph = os.path.join(BASE_DIR, "hash_comparison.png")
plt.savefig(hash_graph)
plt.close()

print("Graphs generated!")
print("Saved:", time_graph)
print("Saved:", hash_graph)
