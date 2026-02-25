"""
plot_mozilla.py
===============
Generates colorful publication-quality graphs from Mozilla/CCADB
experiment results produced by run_experiments_mozilla.py.

Run after experiments:
    python plot_mozilla.py

Produces 7 color PNG files (220 DPI, suitable for IEEE conference paper):
  fig_A_latency.png         — Revocation latency vs n
  fig_A_hash_ops.png        — Hash operations vs n
  fig_A_proof_size.png      — Proof size vs n (vs CRL baseline)
  fig_B_gas_savings.png     — Gas savings % vs batch size k
  fig_B_bw_savings.png      — Bandwidth savings % vs batch size k
  fig_B_batch_hash_ops.png  — Batch hash ops vs k + O(k log n) theory line
  fig_B_batch_time.png      — Batch processing time vs k
"""

import os
import math
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ── Load results ──────────────────────────────────────────────────────────────
a = pd.read_csv(os.path.join(BASE_DIR, "results_mozilla_A.csv"))
b = pd.read_csv(os.path.join(BASE_DIR, "results_mozilla_B.csv"))

# ── Color palette ─────────────────────────────────────────────────────────────
# Colorblind-friendly and prints well
C = {
    "blue":   "#1D4ED8",   # delta / primary
    "teal":   "#0891B2",   # batch / secondary
    "green":  "#16A34A",   # savings / positive metric
    "orange": "#EA580C",   # baseline / comparison
    "purple": "#7C3AED",   # bandwidth
    "red":    "#DC2626",   # reference lines
    "theory": "#6B7280",   # theoretical overlay
    "crl":    "#B45309",   # CRL baseline
}

# ── Plot settings ─────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':     'serif',
    'font.size':       11,
    'axes.titlesize':  11,
    'axes.labelsize':  11,
    'legend.fontsize': 9,
    'xtick.labelsize': 9.5,
    'ytick.labelsize': 9.5,
    'axes.linewidth':  1.1,
    'lines.linewidth': 2.2,
    'grid.linewidth':  0.6,
    'grid.alpha':      0.4,
})

def fmt_n(x, _):
    if x >= 1_000_000: return f"{int(x/1_000_000)}M"
    if x >= 1_000:     return f"{int(x/1_000)}k"
    return str(int(x))

def annotate(ax, xs, ys, fmt="{:.1f}%", yoff=9, color='#374151'):
    for x, y in zip(xs, ys):
        ax.annotate(fmt.format(y), (x, y),
                    textcoords="offset points", xytext=(0, yoff),
                    ha="center", fontsize=8, color=color)

def save(name):
    path = os.path.join(BASE_DIR, name)
    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {name}")

def style_ax(ax):
    ax.grid(True, linestyle=':', alpha=0.45)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)


# ════════════════════════════════════════════════════════════════════════════
# FIG A1 — Revocation Latency vs n
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(a["n"], a["delta_time_ms"],
        label="Delta Revocation (1 credential)",
        color=C["blue"], marker='o', markersize=7, linewidth=2.2)
ax.plot(a["n"], a["batch_time_ms"],
        label="Batch Revocation (k=10 credentials)",
        color=C["teal"], marker='s', markersize=7, linewidth=2.2, linestyle='--')
ax.set_xscale('log')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_n))
ax.set_xlabel("Number of Credentials (n)")
ax.set_ylabel("Revocation Latency (ms)")
ax.set_title("Revocation Latency vs Dataset Size\n(CCADB Real CA Certificate Dataset, n = 500 to 100,000)")
ax.legend(framealpha=0.9)
style_ax(ax)
ax.fill_between(a["n"], a["delta_time_ms"], a["batch_time_ms"],
                alpha=0.07, color=C["teal"])
save("fig_A_latency.png")


# ════════════════════════════════════════════════════════════════════════════
# FIG A2 — Hash Operations vs n
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(a["n"], a["delta_hash_ops"],
        label="Delta Revocation (1 credential)",
        color=C["blue"], marker='o', markersize=7, linewidth=2.2)
ax.plot(a["n"], a["batch_hash_ops"],
        label="Batch Revocation (k=10 credentials)",
        color=C["teal"], marker='s', markersize=7, linewidth=2.2, linestyle='--')

# Theoretical O(log n) and O(10 log n) overlays
n_vals = np.array(a["n"], dtype=float)
log_n  = np.ceil(np.log2(n_vals)).astype(int)
ax.plot(n_vals, log_n,      label="O(log n) theoretical",
        color=C["theory"], linestyle=':', linewidth=1.5, marker='')
ax.plot(n_vals, 10 * log_n, label="O(10·log n) theoretical",
        color=C["theory"], linestyle='-.', linewidth=1.5, marker='')

ax.set_xscale('log')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_n))
ax.set_xlabel("Number of Credentials (n)")
ax.set_ylabel("Hash Computations")
ax.set_title("Hash Operations vs Dataset Size\n(Measured vs O(log n) and O(k·log n) theoretical bounds)")
ax.legend(framealpha=0.9)
style_ax(ax)
save("fig_A_hash_ops.png")


# ════════════════════════════════════════════════════════════════════════════
# FIG A3 — Merkle Proof Size vs n (vs CRL baseline)
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(a["n"], a["proof_size_bytes"],
        label="ZeroID Merkle Proof (bytes)",
        color=C["green"], marker='D', markersize=7, linewidth=2.2)
annotate(ax, a["n"], a["proof_size_bytes"], fmt="{:.0f}B", color=C["green"])

# CRL baseline (linear) — show only up to n=5000 to keep scale readable
crl_n  = a[a["n"] <= 5000]["n"]
crl_sz = crl_n * 32
ax.plot(crl_n, crl_sz,
        label="CRL Baseline (n × 32 B, linear)",
        color=C["crl"], marker='^', markersize=6, linewidth=1.8, linestyle=':')

ax.set_xscale('log')
ax.xaxis.set_major_formatter(mticker.FuncFormatter(fmt_n))
ax.set_xlabel("Number of Credentials (n)")
ax.set_ylabel("Data Transferred (bytes)")
ax.set_title("Merkle Proof Size vs Dataset Size\n"
             "(32 B × ⌈log₂n⌉ nodes vs CRL linear growth)")
ax.legend(framealpha=0.9)
style_ax(ax)
save("fig_A_proof_size.png")


# ════════════════════════════════════════════════════════════════════════════
# FIG B1 — Gas Savings % vs Batch Size k
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.2))

# Filled area under the curve
ax.fill_between(b["batch_size"], b["gas_savings_pct"], alpha=0.12, color=C["green"])
ax.plot(b["batch_size"], b["gas_savings_pct"],
        label="Gas Savings (%)",
        color=C["green"], marker='D', markersize=7, linewidth=2.2)
annotate(ax, b["batch_size"], b["gas_savings_pct"], color=C["green"])
ax.axhline(y=90, color=C["red"], linestyle='--', linewidth=1.3, alpha=0.7,
           label="90% mark (k=10 reference)")

ax.set_xscale('log')
ax.set_ylim(0, 108)
ax.set_xlabel("Batch Size k (credentials per on-chain transaction)")
ax.set_ylabel("Gas Cost Reduction (%)")
ax.set_title("Gas Cost Reduction vs Batch Size\n"
             "(n=10,000 CCADB records; 1 batch tx vs k individual transactions)")
ax.legend(framealpha=0.9)
style_ax(ax)
save("fig_B_gas_savings.png")


# ════════════════════════════════════════════════════════════════════════════
# FIG B2 — Bandwidth Savings % vs Batch Size k
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.2))

ax.fill_between(b["batch_size"], b["bandwidth_savings_pct"], alpha=0.12, color=C["purple"])
ax.plot(b["batch_size"], b["bandwidth_savings_pct"],
        label="Bandwidth Savings vs CRL (%)",
        color=C["purple"], marker='v', markersize=7, linewidth=2.2, linestyle='--')
annotate(ax, b["batch_size"], b["bandwidth_savings_pct"], color=C["purple"])
ax.axhline(y=90, color=C["red"], linestyle='--', linewidth=1.3, alpha=0.7,
           label="90% reference (k=10)")

ax.set_xscale('log')
ax.set_ylim(0, 108)
ax.set_xlabel("Batch Size k (credentials per root update)")
ax.set_ylabel("Bandwidth Reduction (%)")
ax.set_title("Bandwidth Reduction vs Batch Size\n"
             "(ZeroID sends 32 B root vs CRL sends k × 32 B)")
ax.legend(framealpha=0.9)
style_ax(ax)
save("fig_B_bw_savings.png")


# ════════════════════════════════════════════════════════════════════════════
# FIG B3 — Batch Hash Operations vs k (measured + theoretical)
# ════════════════════════════════════════════════════════════════════════════
log_n_fixed = math.ceil(math.log2(10000))   # = 14

fig, ax = plt.subplots(figsize=(7, 4.2))
ax.plot(b["batch_size"], b["batch_hash_ops"],
        label="Measured Batch Hash Ops",
        color=C["teal"], marker='s', markersize=7, linewidth=2.2)
ax.plot(b["batch_size"], b["batch_size"] * log_n_fixed,
        label=f"Theoretical O(k·log n),  log₂(10k) = {log_n_fixed}",
        color=C["theory"], linestyle=':', linewidth=1.6, marker='')
annotate(ax, b["batch_size"], b["batch_hash_ops"], fmt="{:.0f}", color=C["teal"])

ax.set_xlabel("Batch Size k")
ax.set_ylabel("Hash Computations")
ax.set_title("Batch Hash Operations vs Batch Size\n"
             "(Measured vs theoretical O(k·log n), n = 10,000)")
ax.legend(framealpha=0.9)
style_ax(ax)
save("fig_B_batch_hash_ops.png")


# ════════════════════════════════════════════════════════════════════════════
# FIG B4 — Batch Processing Time vs k
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(7, 4.2))
ax.bar(range(len(b["batch_size"])), b["batch_time_ms"],
       color=C["blue"], alpha=0.75, edgecolor='white', linewidth=0.6)
ax.plot(range(len(b["batch_size"])), b["batch_time_ms"],
        color=C["orange"], marker='o', markersize=6, linewidth=1.8,
        label="Batch Time (ms) — trend")
ax.set_xticks(range(len(b["batch_size"])))
ax.set_xticklabels([str(k) for k in b["batch_size"]], fontsize=9)
ax.set_xlabel("Batch Size k (credentials per batch)")
ax.set_ylabel("Processing Time (ms)")
ax.set_title("Batch Revocation Latency vs Batch Size\n"
             "(n = 10,000 CCADB records)")
ax.legend(framealpha=0.9)
style_ax(ax)
save("fig_B_batch_time.png")


print("\nAll 7 graphs generated successfully.")
print("Files are IEEE-ready at 220 DPI.")