"""
setup_mozilla_dataset.py
========================
Run this from your PROJECT ROOT:

    python setup_mozilla_dataset.py

It will:
  1. Try to download the real CCADB dataset directly via Python
  2. If that fails → generate a realistic 3,500-record synthetic dataset

Output goes to:  backend/experiments/mozilla_certs.csv
(exactly where run_experiments_mozilla.py looks for it)

Then run your experiments from project root:
    python backend/experiments/run_experiments_mozilla.py
"""

import csv
import hashlib
import os
import random
import sys
import time

try:
    from urllib.request import urlopen, Request
    from urllib.error import URLError, HTTPError
except ImportError:
    urlopen = None

# ── Paths ──────────────────────────────────────────────────────────────────────
# Script can be run from project root OR from backend/experiments/
# We always write the CSV to backend/experiments/ (where the experiment script lives)
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = SCRIPT_DIR  # assumes this script is placed at project root

# Find backend/experiments/ relative to project root
EXPERIMENTS_DIR = os.path.join(PROJECT_ROOT, "backend", "experiments")

# Fallback: if run from inside backend/experiments/
if not os.path.isdir(EXPERIMENTS_DIR):
    EXPERIMENTS_DIR = SCRIPT_DIR

OUT_FILE     = os.path.join(EXPERIMENTS_DIR, "mozilla_certs.csv")
CCADB_URL    = "https://ccadb.my.salesforce-sites.com/ccadb/AllCertificateRecordsCSVFormatv4"
MIN_RECORDS  = 500
SYNTH_COUNT  = 3500


# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: Try downloading real CCADB data
# ══════════════════════════════════════════════════════════════════════════════

def try_download():
    print("=" * 62)
    print("  Attempting real CCADB download via Python...")
    print(f"  URL: {CCADB_URL}")
    print("=" * 62)

    if urlopen is None:
        print("  [SKIP] urllib not available.")
        return False

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        "Accept": "text/csv,text/plain,*/*",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.ccadb.org/resources",
    }

    try:
        req  = Request(CCADB_URL, headers=headers)
        resp = urlopen(req, timeout=30)
        raw  = resp.read().decode("utf-8", errors="replace")

        stripped = raw.strip()
        if stripped.startswith("<"):
            print("  [FAIL] Got HTML response instead of CSV.")
            print(f"  First 200 chars: {stripped[:200]}")
            return False

        lines = [l for l in stripped.splitlines() if l.strip()]
        print(f"  Downloaded {len(lines):,} lines  ({len(raw):,} bytes)")

        if len(lines) < MIN_RECORDS:
            print(f"  [FAIL] Too few lines ({len(lines)}). Probably an error page.")
            return False

        os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
        with open(OUT_FILE, "w", encoding="utf-8", newline="") as f:
            f.write(raw)

        print(f"  [OK] Real dataset saved → {OUT_FILE}")
        print(f"  Records: {len(lines) - 1:,} (excluding header)")
        return True

    except HTTPError as e:
        print(f"  [FAIL] HTTP {e.code}: {e.reason}")
    except URLError as e:
        print(f"  [FAIL] Network error: {e.reason}")
    except Exception as e:
        print(f"  [FAIL] {e}")

    return False


# ══════════════════════════════════════════════════════════════════════════════
# STEP 2: Generate synthetic fallback
# Column names MUST match what load_mozilla_csv() in run_experiments_mozilla.py
# searches for:
#   cn_col     → 'Common Name or Certificate Name'  ✓
#   issuer_col → 'Certificate Issuer Common Name'   ✓  (also tries 'Issuer Common Name')
#   fp_col     → 'SHA-256 Fingerprint'              ✓
# ══════════════════════════════════════════════════════════════════════════════

def generate_synthetic():
    print("\n" + "=" * 62)
    print("  Generating synthetic CCADB-style dataset...")
    print(f"  Records : {SYNTH_COUNT:,}")
    print(f"  Output  : {OUT_FILE}")
    print("=" * 62)

    random.seed(42)

    CA_OWNERS = [
        "DigiCert Inc", "Sectigo Limited", "Let's Encrypt", "GlobalSign nv-sa",
        "IdenTrust", "Entrust Inc", "Comodo CA Limited", "GoDaddy.com Inc",
        "Amazon Trust Services", "Microsoft Corporation", "Google Trust Services",
        "ISRG", "QuoVadis Limited", "SwissSign AG", "T-Systems International GmbH",
        "Government of India NIC", "Certum", "Trustwave Holdings Inc", "Buypass AS",
        "Staat der Nederlanden", "FNMT-RCM Spain", "KISA Korea",
        "Actalis S.p.A", "Dhimyotis", "D-Trust GmbH", "e-tugra",
        "HARICA", "Hongkong Post", "JPKI", "NetLock Kft",
        "OISTE Foundation", "Secom Trust Systems", "SK ID Solutions",
        "Telia Company", "Thales DIS Finland", "TrustCor Systems",
        "TURKTRUST", "Visa",
    ]

    CERT_TYPES = [
        "Server Authentication CA", "Client Authentication CA",
        "Code Signing CA", "Email Protection CA", "Document Signing CA",
        "Government Identity CA", "Academic Credential CA",
        "OCSP Signing CA", "Root CA", "Intermediate CA",
        "Policy CA", "TLS Subordinate CA", "S/MIME Subordinate CA",
    ]

    MOZILLA_STATUS = ["Included", "Not Included", "Not Yet Included",
                      "Included - Constrained", "Revoked"]
    CHROME_STATUS  = ["Included", "Not Included", "Included - Constrained"]
    AUDITORS       = ["KPMG", "Ernst & Young", "BDO", "Deloitte", "PwC",
                      "A-SIT", "LSTI", ""]
    AUDIT_TYPES    = ["WebTrust", "ETSI EN 319 411", "ETSI TS 102 042", ""]

    # ── Column names must match _find_col() candidates in load_mozilla_csv() ──
    FIELDNAMES = [
        "Common Name or Certificate Name",   # → cn_col
        "Certificate Issuer Common Name",    # → issuer_col
        "SHA-256 Fingerprint",               # → fp_col
        "CA Owner",
        "Salesforce Record ID",
        "Parent Certificate Name",
        "Certificate Record Type",
        "Mozilla Status",
        "Chrome Status",
        "Microsoft Status",
        "Apple Status",
        "Revocation Status",
        "Valid From (GMT)",
        "Valid To (GMT)",
        "Technically Constrained",
        "Derived Trust Bits",
        "Full CRL Issued By This CA",
        "Auditor",
        "Standard Audit Type",
    ]

    used_fps = set()
    rows = []

    for i in range(SYNTH_COUNT):
        owner  = random.choice(CA_OWNERS)
        ctype  = random.choice(CERT_TYPES)
        yr_from = random.randint(2010, 2022)
        yr_to   = yr_from + random.randint(3, 15)

        seed_str = f"{owner}_{ctype}_{i}_{time.time_ns()}"
        fp = hashlib.sha256(seed_str.encode()).hexdigest().upper()
        while fp in used_fps:
            fp = hashlib.sha256((seed_str + str(random.random())).encode()).hexdigest().upper()
        used_fps.add(fp)

        uid_short = fp[:8]
        cn        = f"{owner} {ctype} {uid_short}"
        sf_id     = f"001{hashlib.md5(fp.encode()).hexdigest()[:15].upper()}"

        rows.append({
            "Common Name or Certificate Name": cn,
            "Certificate Issuer Common Name": f"{owner} Root CA",
            "SHA-256 Fingerprint": fp,
            "CA Owner": owner,
            "Salesforce Record ID": sf_id,
            "Parent Certificate Name": f"{owner} Root CA",
            "Certificate Record Type": "Intermediate Certificate" if "Intermediate" in ctype or "Subordinate" in ctype else "Root Certificate",
            "Mozilla Status": random.choice(MOZILLA_STATUS),
            "Chrome Status": random.choice(CHROME_STATUS),
            "Microsoft Status": random.choice(["Included", "Not Included"]),
            "Apple Status": random.choice(["Included", "Not Included"]),
            "Revocation Status": random.choice(["", "Revoked", "On CRL"]),
            "Valid From (GMT)": f"{yr_from}.{random.randint(1,12):02d}.{random.randint(1,28):02d}",
            "Valid To (GMT)": f"{yr_to}.{random.randint(1,12):02d}.{random.randint(1,28):02d}",
            "Technically Constrained": random.choice(["true", "false"]),
            "Derived Trust Bits": random.choice(["Server Authentication", "Email", "Code Signing", ""]),
            "Full CRL Issued By This CA": f"http://crl.{owner.split()[0].lower()}.com/{uid_short}.crl" if random.random() > 0.3 else "",
            "Auditor": random.choice(AUDITORS),
            "Standard Audit Type": random.choice(AUDIT_TYPES),
        })

    os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
    with open(OUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    size_kb = os.path.getsize(OUT_FILE) / 1024
    print(f"\n  [OK] Generated {SYNTH_COUNT:,} records  ({size_kb:.0f} KB)")
    print()
    print("  Columns written (matching run_experiments_mozilla.py parser):")
    print("    cn_col     → 'Common Name or Certificate Name'")
    print("    issuer_col → 'Certificate Issuer Common Name'")
    print("    fp_col     → 'SHA-256 Fingerprint'")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    print("  ZeroID — CCADB Dataset Setup")
    print(f"  Writing to: {OUT_FILE}")
    print()

    # If valid file already exists, skip
    if os.path.exists(OUT_FILE):
        size_kb = os.path.getsize(OUT_FILE) / 1024
        if size_kb > 100:
            print(f"  File already exists ({size_kb:.0f} KB) and looks valid.")
            print("  Delete it and re-run to regenerate.")
            sys.exit(0)
        else:
            print(f"  Existing file is too small ({size_kb:.1f} KB) — replacing it.\n")

    # Try real download first, fallback to synthetic
    success = try_download()
    if not success:
        print("\n  Download failed — generating synthetic dataset instead...")
        generate_synthetic()

    print()
    print("=" * 62)
    print("  Done!  Now run from your project root:")
    print()
    print("    python backend/experiments/run_experiments_mozilla.py")
    print("    python backend/experiments/plot_mozilla.py")
    print("=" * 62)
    print()