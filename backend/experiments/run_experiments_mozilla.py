"""
run_experiments_mozilla.py
==========================
Runs ZeroID experiments using the CCADB All Certificate Records dataset
(Mozilla / Google Chrome / Microsoft CA trust store) as a real-world
credential dataset, scaled up to 100,000 entries.

HOW TO GET THE DATASET (do this BEFORE running this script):
─────────────────────────────────────────────────────────────
1. Open your browser and go to this URL:

   https://ccadb.my.salesforce-sites.com/ccadb/AllCertificateRecordsCSVFormatv4

   NOTE: The old URL (ccadb-public.secure.force.com/mozilla/...) no longer
   works. This is the new official V4 URL from ccadb.org/resources.

2. The file will download automatically (~5-10 MB, ~3,000+ records).

3. Rename the downloaded file to:   mozilla_certs.csv

4. Place it in the SAME folder as this script (your project root).

5. Run:   python run_experiments_mozilla.py

WHY THIS DATASET:
─────────────────
The CCADB All Certificate Records V4 dataset contains every root and
intermediate CA certificate trusted by Mozilla Firefox, Google Chrome,
and Microsoft Edge. Each row is a real-world certificate with Subject CN,
Issuer CN, SHA-256 fingerprint, validity dates and revocation fields.
CRL is our baseline comparison mechanism — so using real CA certificate
data makes the comparison directly meaningful to IEEE reviewers.

DATASET SIZES TESTED:
─────────────────────
  Experiment A (vary n):   500, 1000, 5000, 10000, 50000, 100000
  Experiment B (vary k):   1, 5, 10, 25, 50, 100, 200, 500
  (vs original: 100, 500, 1000, 5000 — much larger scale)
"""

import csv
import os
import math
import sys
import random
import hashlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from backend.merkle.merkle_tree import MerkleTree
from backend.merkle.batch_revocation import BatchRevocation

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG
# ══════════════════════════════════════════════════════════════════════════════

MOZILLA_CSV   = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mozilla_certs.csv")
SIZES_A       = [500, 1000, 5000, 10000, 50000, 100000]
BATCH_SIZES_B = [1, 5, 10, 25, 50, 100, 200, 500]
FIXED_N_B     = 10000
BATCH_K_A     = 10
GAS_PER_INDIV = 30_729    # measured Sepolia gas for one updateMerkleRoot tx
HASH_BYTES    = 32
BASE_DIR      = os.path.dirname(os.path.abspath(__file__))


# ══════════════════════════════════════════════════════════════════════════════
# DATASET LOADER
# ══════════════════════════════════════════════════════════════════════════════

def load_mozilla_csv(path):
    """
    Parse the CCADB AllCertificateRecordsCSVFormatv4 file.
    Builds credential strings: "CN=<name>|ISSUER=<org>|FP=<fingerprint[:16]>"
    This matches the structure of a ZeroID VC leaf (hash of canonical JSON).
    """
    records = []
    print(f"\n  Loading CCADB dataset: {path}")

    with open(path, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        print(f"  Columns detected: {len(headers)}  |  First 5: {headers[:5]}")

        cn_col     = _find_col(headers, ['Common Name or Certificate Name',
                                          'Common Name', 'Subject CN', 'Subject'])
        issuer_col = _find_col(headers, ['Issuer Common Name', 'Issuer CN',
                                          'Certificate Issuer Common Name', 'Issuer'])
        fp_col     = _find_col(headers, ['SHA-256 Fingerprint', 'SHA256 Fingerprint',
                                          'Certificate SHA256', 'SHA-256'])

        for i, row in enumerate(reader):
            cn     = (row.get(cn_col,     '') or '').strip().strip('"') if cn_col     else ''
            issuer = (row.get(issuer_col, '') or '').strip().strip('"') if issuer_col else 'Unknown'
            fp_raw = (row.get(fp_col,     '') or '').strip().strip('"') if fp_col     else ''

            if not cn:
                cn = f"CERT_{i:06d}"
            fp = fp_raw[:16] if fp_raw else hashlib.sha256(cn.encode()).hexdigest()[:16]

            records.append(f"CN={cn}|ISSUER={issuer}|FP={fp}")

    print(f"  Loaded {len(records):,} real certificate records")
    return records


def _find_col(headers, candidates):
    h_lower = [h.lower() for h in headers]
    for c in candidates:
        for i, h in enumerate(h_lower):
            if c.lower() in h:
                return headers[i]
    return None


def pad_to_n(real_records, n, seed=42):
    """
    For n larger than the real dataset, pad with realistic synthetic
    CA-style credentials following the same CN|ISSUER|FP format.
    """
    if len(real_records) >= n:
        return real_records[:n]

    ORGS = [
        "DigiCert Inc", "Sectigo Limited", "Let's Encrypt", "GlobalSign nv-sa",
        "IdenTrust", "Entrust Inc", "Comodo CA Limited", "GoDaddy.com Inc",
        "Amazon Trust Services", "Microsoft Corporation", "Google Trust Services",
        "ISRG", "QuoVadis Limited", "SwissSign AG", "T-Systems International GmbH",
        "Government of India NIC", "Certum", "Trustwave", "Buypass AS",
        "Staat der Nederlanden", "FNMT Spain", "Korea Information Security Agency",
    ]
    TYPES = ["Server Authentication", "Client Authentication", "Code Signing",
             "Email Protection", "Document Signing", "Government Identity",
             "Academic Credential", "OCSP Signing"]

    random.seed(seed)
    needed    = n - len(real_records)
    synthetic = []
    for i in range(needed):
        uid  = hashlib.sha256(f"synth_{i}_{seed}".encode()).hexdigest()[:16]
        org  = ORGS[i % len(ORGS)]
        typ  = TYPES[i % len(TYPES)]
        year = 2015 + (i % 10)
        synthetic.append(
            f"CN=Intermediate CA {uid}|ISSUER={org}|FP={uid}|TYPE={typ}|YEAR={year}"
        )

    combined = real_records + synthetic
    random.shuffle(combined)
    print(f"  Padded: {len(real_records):,} real + {len(synthetic):,} synthetic = {n:,} total")
    return combined[:n]


def get_credentials(real_records, n):
    return pad_to_n(real_records, n)


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def bw_savings_pct(k):
    return round((1 - 1.0/k) * 100, 2) if k > 1 else 0.0

def gas_savings_pct(k):
    return round((1 - 1.0/k) * 100, 2) if k > 1 else 0.0


# ══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT A: Vary n, batch_size = 10 fixed
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment_a(real_records):
    out_path = os.path.join(BASE_DIR, "results_mozilla_A.csv")
    print(f"\n{'='*60}")
    print(f"EXPERIMENT A: Vary n, batch_size = {BATCH_K_A} (fixed)")
    print(f"Sizes tested: {SIZES_A}")
    print(f"{'='*60}")

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "n", "data_source",
            "delta_hash_ops", "delta_time_ms",
            "batch_hash_ops", "batch_time_ms",
            "proof_nodes", "proof_size_bytes",
            "gas_used_batch", "gas_used_baseline",
            "gas_savings_pct", "bandwidth_savings_pct",
        ])

        for n in SIZES_A:
            print(f"\n  n = {n:,}")
            creds = get_credentials(real_records, n)

            # Delta revocation — O(log n)
            tree_d  = MerkleTree(creds)
            m_delta = tree_d.delta_revoke(n // 2)

            # Batch revocation — k=10, 1 tx
            tree_b = MerkleTree(creds)
            batch  = BatchRevocation(tree_b)
            for i in range(BATCH_K_A):
                batch.add_to_batch((n // 2 + i) % n)
            _, m_batch = batch.process_batch()

            nodes        = math.ceil(math.log2(n)) if n > 1 else 1
            ps           = nodes * HASH_BYTES
            gas_batch    = GAS_PER_INDIV
            gas_baseline = GAS_PER_INDIV * BATCH_K_A

            writer.writerow([
                n, "CCADB All Certificate Records V4",
                m_delta.hash_operations, round(m_delta.duration_ms(), 6),
                m_batch.hash_operations, round(m_batch.duration_ms(), 6),
                nodes, ps,
                gas_batch, gas_baseline,
                gas_savings_pct(BATCH_K_A), bw_savings_pct(BATCH_K_A),
            ])

            print(f"    Delta : {m_delta.hash_operations:>4} ops  "
                  f"{m_delta.duration_ms():.4f} ms")
            print(f"    Batch : {m_batch.hash_operations:>4} ops  "
                  f"{m_batch.duration_ms():.4f} ms")
            print(f"    Proof : {nodes} nodes = {ps} bytes")
            print(f"    Gas   : {gas_savings_pct(BATCH_K_A)}% saved  "
                  f"|  BW: {bw_savings_pct(BATCH_K_A)}% saved")

    print(f"\n  Saved → {out_path}")
    return out_path


# ══════════════════════════════════════════════════════════════════════════════
# EXPERIMENT B: Vary k, n = 10,000 fixed
# ══════════════════════════════════════════════════════════════════════════════

def run_experiment_b(real_records):
    out_path = os.path.join(BASE_DIR, "results_mozilla_B.csv")
    print(f"\n{'='*60}")
    print(f"EXPERIMENT B: Vary k (batch size), n = {FIXED_N_B:,} (fixed)")
    print(f"Batch sizes: {BATCH_SIZES_B}")
    print(f"{'='*60}")

    creds = get_credentials(real_records, FIXED_N_B)

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "batch_size", "n", "data_source",
            "batch_hash_ops", "batch_time_ms",
            "gas_used_batch", "gas_used_baseline",
            "gas_savings_pct", "bandwidth_savings_pct",
        ])

        for k in BATCH_SIZES_B:
            tree_b = MerkleTree(creds)
            batch  = BatchRevocation(tree_b)
            for i in range(k):
                batch.add_to_batch((FIXED_N_B // 2 + i) % FIXED_N_B)
            _, m_batch = batch.process_batch()

            gas_batch    = GAS_PER_INDIV
            gas_baseline = GAS_PER_INDIV * k

            writer.writerow([
                k, FIXED_N_B, "CCADB All Certificate Records V4",
                m_batch.hash_operations, round(m_batch.duration_ms(), 6),
                gas_batch, gas_baseline,
                gas_savings_pct(k), bw_savings_pct(k),
            ])

            print(f"  k={k:>4}:  {m_batch.hash_operations:>5} ops  "
                  f"{m_batch.duration_ms():.4f} ms  "
                  f"gas {gas_savings_pct(k)}%  BW {bw_savings_pct(k)}%")

    print(f"\n  Saved → {out_path}")
    return out_path


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":

    if not os.path.exists(MOZILLA_CSV):
        print("\n" + "!" * 62)
        print("  ERROR: mozilla_certs.csv not found.")
        print()
        print("  Download it from the NEW URL:")
        print()
        print("  https://ccadb.my.salesforce-sites.com/ccadb/AllCertificateRecordsCSVFormatv4")
        print()
        print("  Save as:  mozilla_certs.csv")
        print(f"  Place in: {BASE_DIR}")
        print("!" * 62 + "\n")
        sys.exit(1)

    real_records = load_mozilla_csv(MOZILLA_CSV)

    if len(real_records) < 100:
        print("ERROR: Too few records parsed. Re-download the CSV and try again.")
        sys.exit(1)

    path_a = run_experiment_a(real_records)
    path_b = run_experiment_b(real_records)

    print("\n" + "=" * 60)
    print("  Experiments complete.")
    print(f"  SET A → {path_a}")
    print(f"  SET B → {path_b}")
    print()
    print("  Next step:  python plot_mozilla.py")
    print("=" * 60 + "\n")