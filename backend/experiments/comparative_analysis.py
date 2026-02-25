"""
comparative_analysis.py  (Contribution 4)
==========================================
Empirical and theoretical comparison of ZeroID against:
  - CRL (Certificate Revocation Lists)
  - RSA Accumulator
  - Bilinear-Map Accumulator
  - Standard Merkle Tree (no batching / no delta)

Metrics compared:
  - Proof size (bytes)
  - Update complexity (hash ops / crypto ops)
  - On-chain storage (bytes)
  - Gas cost model (relative units)
  - Revocation privacy (yes/no)
  - Batch support (yes/no)

Outputs:
  - comparison_table.csv   : full data table
  - comparison_chart.png   : grouped bar chart of key metrics
  - complexity_chart.png   : O-notation complexity plot
"""

import os
import csv
import math
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# ── Theoretical models ────────────────────────────────────────────────────────
# All values are computed as functions of n (credential set size)
# and k (number of revocations in a batch).

def crl_proof_size(n, k=1):
    """CRL: send the entire list — O(n) bytes (32 bytes per revoked ID)."""
    return n * 32

def crl_update_ops(n, k=1):
    """CRL update: append k entries, no crypto ops."""
    return k

def crl_onchain_bytes(n, k=1):
    """CRL stored on-chain — not realistic but theoretical: O(n*32)."""
    return n * 32

def crl_gas(n, k=1):
    """Gas to store n*32 bytes on-chain (SSTORE ≈ 20k gas per 32 bytes)."""
    return (n * 32 / 32) * 20_000


def rsa_proof_size(n, k=1, bits=2048):
    """RSA accumulator witness: one element = bits/8 bytes."""
    return bits // 8

def rsa_update_ops(n, k=1):
    """RSA update: O(k) modular exponentiations (expensive)."""
    return k * 1000   # ~1000 hash-equivalent ops per modexp

def rsa_onchain_bytes(n, k=1, bits=2048):
    """Store accumulator value: bits/8 bytes."""
    return bits // 8

def rsa_gas(n, k=1):
    """One SSTORE for accumulator value (256-bit = 1 slot)."""
    return 20_000


def bilinear_proof_size(n, k=1, g1_bytes=48):
    """BLS12-381 G1 point = 48 bytes. Proof = one G1 element."""
    return g1_bytes

def bilinear_update_ops(n, k=1):
    """Pairing operations per update — expensive."""
    return k * 3000

def bilinear_onchain_bytes(n, k=1, g1_bytes=48):
    """Store accumulator: one G1 point."""
    return g1_bytes

def bilinear_gas(n, k=1):
    """EIP-2537 BLS precompile: ~45k gas per pairing."""
    return 45_000


def std_merkle_proof_size(n, k=1):
    """Standard Merkle: ceil(log2(n)) * 32 bytes per proof."""
    nodes = math.ceil(math.log2(n)) if n > 1 else 1
    return nodes * 32

def std_merkle_update_ops(n, k=1):
    """Standard Merkle: full rebuild for each of k revocations = k * n ops."""
    return k * n

def std_merkle_onchain_bytes(n, k=1):
    """Store just the root: 32 bytes."""
    return 32

def std_merkle_gas(n, k=1):
    """One SSTORE per revocation = k * 20k gas."""
    return k * 20_000


def zeroid_proof_size(n, k=1):
    """ZeroID: same Merkle proof = ceil(log2(n)) * 32 bytes."""
    nodes = math.ceil(math.log2(n)) if n > 1 else 1
    return nodes * 32

def zeroid_update_ops(n, k=1):
    """ZeroID delta: O(log n) per credential, batched = k * log2(n) ops."""
    return k * math.ceil(math.log2(n)) if n > 1 else k

def zeroid_onchain_bytes(n, k=1):
    """ZeroID: always just the root = 32 bytes regardless of k."""
    return 32

def zeroid_gas(n, k=1):
    """ZeroID: ONE transaction for any batch size = ~30,729 gas."""
    return 30_729


# ── Build comparison table ────────────────────────────────────────────────────

SCHEMES = {
    "CRL":              (crl_proof_size,      crl_update_ops,      crl_onchain_bytes,      crl_gas,      False, False),
    "RSA Accumulator":  (rsa_proof_size,      rsa_update_ops,      rsa_onchain_bytes,      rsa_gas,      True,  False),
    "Bilinear-Map Acc": (bilinear_proof_size, bilinear_update_ops, bilinear_onchain_bytes, bilinear_gas, True,  False),
    "Standard Merkle":  (std_merkle_proof_size, std_merkle_update_ops, std_merkle_onchain_bytes, std_merkle_gas, False, False),
    "ZeroID (Ours)":    (zeroid_proof_size,   zeroid_update_ops,   zeroid_onchain_bytes,   zeroid_gas,   True,  True),
}

COMPLEXITY = {
    "CRL":              ("O(n)",      "O(k)",          "O(n)",   "O(k·n)"),
    "RSA Accumulator":  ("O(1)",      "O(k) modexp",   "O(1)",   "O(1)"),
    "Bilinear-Map Acc": ("O(1)",      "O(k) pairing",  "O(1)",   "O(1)"),
    "Standard Merkle":  ("O(log n)",  "O(k·n)",        "O(1)",   "O(k)"),
    "ZeroID (Ours)":    ("O(log n)",  "O(k·log n)",    "O(1)",   "O(1)"),
}
#                        proof_size   update           storage   gas_txs


def build_table(n=1000, k=10):
    rows = []
    for scheme, (ps_fn, up_fn, ob_fn, gas_fn, privacy, batch) in SCHEMES.items():
        rows.append({
            "scheme":           scheme,
            "proof_size_bytes": ps_fn(n, k),
            "update_ops":       up_fn(n, k),
            "onchain_bytes":    ob_fn(n, k),
            "gas_cost":         gas_fn(n, k),
            "privacy":          "Yes" if privacy else "No",
            "batch_support":    "Yes" if batch else "No",
            "proof_complexity":  COMPLEXITY[scheme][0],
            "update_complexity": COMPLEXITY[scheme][1],
            "storage_complexity":COMPLEXITY[scheme][2],
            "gas_complexity":    COMPLEXITY[scheme][3],
        })
    return rows


def save_csv(rows):
    path = os.path.join(BASE_DIR, "comparison_table.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"  Saved: {path}")
    return path


def plot_bar_chart(rows, n=1000, k=10):
    schemes = [r["scheme"] for r in rows]
    metrics = {
        "Proof Size (bytes)":  [r["proof_size_bytes"] for r in rows],
        "Gas Cost":            [r["gas_cost"]          for r in rows],
        "On-chain Storage (B)":[r["onchain_bytes"]     for r in rows],
    }

    colors = ["#4f46e5", "#0891b2", "#16a34a"]
    x = np.arange(len(schemes))
    width = 0.25

    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    fig.suptitle(f"Comparative Analysis: n={n:,} credentials, k={k} revocations", fontsize=13, fontweight="bold")

    for ax, (title, values), color in zip(axes, metrics.items(), colors):
        bars = ax.bar(x, values, color=color, alpha=0.85, edgecolor="white")
        ax.set_title(title, fontsize=11, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(schemes, rotation=20, ha="right", fontsize=8)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda v, _: f"{int(v):,}"))
        ax.grid(axis="y", alpha=0.3)
        # highlight ZeroID bar
        bars[-1].set_edgecolor("#f59e0b")
        bars[-1].set_linewidth(2.5)

    plt.tight_layout()
    path = os.path.join(BASE_DIR, "comparison_chart.png")
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


def plot_complexity_chart():
    """Log-scale line chart: update ops vs n for each scheme."""
    ns = [50, 100, 250, 500, 1000, 2000, 5000]
    k  = 10

    fig, ax = plt.subplots(figsize=(8, 5))

    styles = {
        "CRL":              ("--",  "#dc2626"),
        "RSA Accumulator":  (":",   "#7c3aed"),
        "Bilinear-Map Acc": ("-.",  "#b45309"),
        "Standard Merkle":  ("--",  "#0891b2"),
        "ZeroID (Ours)":    ("-",   "#16a34a"),
    }

    for scheme, (ps_fn, up_fn, ob_fn, gas_fn, privacy, batch) in SCHEMES.items():
        ops = [up_fn(n, k) for n in ns]
        ls, color = styles[scheme]
        lw = 2.5 if scheme == "ZeroID (Ours)" else 1.5
        ax.plot(ns, ops, linestyle=ls, color=color, linewidth=lw,
                marker="o", markersize=4, label=scheme)

    ax.set_xlabel("Number of Credentials (n)")
    ax.set_ylabel("Update Operations (log scale)")
    ax.set_yscale("log")
    ax.set_title(f"Update Complexity vs Dataset Size (k={k} revocations)", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)

    path = os.path.join(BASE_DIR, "complexity_chart.png")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Saved: {path}")


def print_table(rows):
    print(f"\n{'Scheme':<20} {'Proof(B)':>9} {'Ops':>10} {'On-chain(B)':>12} {'Gas':>8} {'Privacy':>8} {'Batch':>6}")
    print("-" * 80)
    for r in rows:
        print(f"{r['scheme']:<20} {r['proof_size_bytes']:>9,} {r['update_ops']:>10,.0f} "
              f"{r['onchain_bytes']:>12,} {r['gas_cost']:>8,} {r['privacy']:>8} {r['batch_support']:>6}")


if __name__ == "__main__":
    N, K = 1000, 10
    print(f"\n=== Comparative Analysis: n={N}, k={K} ===")

    rows = build_table(N, K)
    print_table(rows)
    save_csv(rows)
    plot_bar_chart(rows, N, K)
    plot_complexity_chart()

    print("\n✅ Comparative analysis complete.")
    print("   Files: comparison_table.csv, comparison_chart.png, complexity_chart.png")