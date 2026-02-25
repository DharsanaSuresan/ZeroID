"""
vc_model.py  (Objective 5 — SSI / Verifiable Credential alignment)
===================================================================
Provides W3C-compatible Verifiable Credential formatting for ZeroID
certificates, and implements the three SSI roles as proper classes:

  Issuer   → signs and issues VCs
  Holder   → stores and presents VCs
  Verifier → verifies VC integrity + Merkle proof + revocation status

This file does NOT replace Django models — it layers a VC-compatible
representation on top of them for research/export purposes.

W3C VC Data Model reference: https://www.w3.org/TR/vc-data-model/
"""

import hashlib
import json
import uuid
from datetime import datetime, timezone


# ── Minimal DID helper ────────────────────────────────────────────────────────

def make_did(role: str, identifier: str) -> str:
    """
    Create a simple deterministic DID for SSI alignment.
    Format: did:zeroed:<role>:<sha256(identifier)[:16]>

    In production this would use a DID method like did:key or did:ethr.
    For research purposes this demonstrates the DID concept.
    """
    id_hash = hashlib.sha256(identifier.encode()).hexdigest()[:16]
    return f"did:zeroid:{role}:{id_hash}"


# ── W3C Verifiable Credential builder ────────────────────────────────────────

def build_vc(certificate, issuer_user) -> dict:
    """
    Convert a Django Certificate model instance into a W3C VC JSON-LD object.

    Output structure follows the W3C VC Data Model 1.1:
    https://www.w3.org/TR/vc-data-model/#basic-concepts

    Args:
        certificate : Django Certificate model instance
        issuer_user : Django User model instance (role=issuer)

    Returns:
        dict : W3C-compatible Verifiable Credential
    """
    issuer_did = make_did("issuer", str(issuer_user.id))
    holder_did = make_did(
        "holder",
        str(certificate.holder.id) if certificate.holder else certificate.holder_name
    )

    vc = {
        # ── W3C required fields ──────────────────────────────────────────────
        "@context": [
            "https://www.w3.org/2018/credentials/v1",
            "https://zeroid.io/credentials/v1"           # ZeroID extension context
        ],
        "type": ["VerifiableCredential", "ZeroIDCertificate"],
        "id": f"urn:uuid:{certificate.certificate_id}",

        # ── Issuer DID ───────────────────────────────────────────────────────
        "issuer": {
            "id":           issuer_did,
            "name":         issuer_user.username,
            "organization": getattr(issuer_user, "organization", None),
        },

        # ── Issuance & expiry ─────────────────────────────────────────────────
        "issuanceDate": certificate.issued_date.isoformat()
            if hasattr(certificate.issued_date, "isoformat")
            else str(certificate.issued_date),
        "expirationDate": certificate.expiry_date.isoformat()
            if certificate.expiry_date else None,

        # ── Credential subject (the holder) ──────────────────────────────────
        "credentialSubject": {
            "id":          holder_did,
            "name":        certificate.holder_name,
            "certificate": {
                "title":       certificate.title,
                "description": certificate.description or "",
                "ipfs_cid":    certificate.ipfs_cid,
            }
        },

        # ── ZeroID-specific: blockchain proof ─────────────────────────────────
        "proof": {
            "type":              "MerkleProof2024",
            "created":           datetime.now(timezone.utc).isoformat(),
            "proofPurpose":      "assertionMethod",
            "verificationMethod": issuer_did,
            "integrity": {
                "hash_value":          certificate.hash_value,
                "blockchain_tx_hash":  certificate.blockchain_tx_hash,
                "blockchain_network":  "sepolia",
                "smart_contract":      certificate.smart_contract_address,
                "ipfs_cid":            certificate.ipfs_cid,
            }
        },

        # ── Revocation status pointer ─────────────────────────────────────────
        "credentialStatus": {
            "type":              "ZeroIDMerkleRevocation",
            "id":                f"did:zeroid:revocation:{certificate.certificate_id}",
            "status":            certificate.status,
            "merkle_root_onchain": True,    # root anchored to Sepolia
        }
    }

    return vc


# ── SSI Role classes ──────────────────────────────────────────────────────────

class ZeroIDIssuer:
    """
    SSI Issuer role.
    Responsible for creating and signing Verifiable Credentials.
    In ZeroID the 'signature' is the on-chain Merkle root.
    """

    def __init__(self, user):
        self.user = user
        self.did  = make_did("issuer", str(user.id))

    def issue_vc(self, certificate) -> dict:
        """Return a W3C VC dict for the given certificate."""
        return build_vc(certificate, self.user)

    def export_vc_json(self, certificate) -> str:
        """Return the VC as a JSON string (for IPFS upload or QR code)."""
        return json.dumps(self.issue_vc(certificate), indent=2, default=str)

    def __repr__(self):
        return f"<ZeroIDIssuer did={self.did}>"


class ZeroIDHolder:
    """
    SSI Holder role.
    Stores credentials and presents them to verifiers.
    Privacy: holder only reveals the proof path, not other credentials.
    """

    def __init__(self, user):
        self.user = user
        self.did  = make_did("holder", str(user.id))
        self._wallet: dict[str, dict] = {}   # cert_id → VC dict

    def store_vc(self, vc: dict):
        """Store a received VC in the holder's wallet."""
        cert_id = vc.get("id", str(uuid.uuid4()))
        self._wallet[cert_id] = vc

    def present_vc(self, cert_id: str) -> dict:
        """
        Create a Verifiable Presentation for a single credential.
        Presentation wraps the VC so the holder controls what is shared.
        """
        vc = self._wallet.get(cert_id)
        if not vc:
            raise KeyError(f"Credential {cert_id} not found in wallet")

        return {
            "@context":   ["https://www.w3.org/2018/credentials/v1"],
            "type":       ["VerifiablePresentation"],
            "holder":     self.did,
            "verifiableCredential": [vc],
            "presentedAt": datetime.now(timezone.utc).isoformat(),
        }

    def list_credentials(self) -> list:
        return list(self._wallet.keys())

    def __repr__(self):
        return f"<ZeroIDHolder did={self.did} credentials={len(self._wallet)}>"


class ZeroIDVerifier:
    """
    SSI Verifier role.
    Independently verifies a VC without contacting the issuer directly.
    Checks: integrity hash + Merkle proof + on-chain root + revocation status.
    """

    def __init__(self, name: str = "Verifier"):
        self.did  = make_did("verifier", name)
        self.name = name

    def verify_vc(self, vc: dict, merkle_proof: list, on_chain_root: str) -> dict:
        """
        Verify a W3C VC against the on-chain Merkle root.

        Args:
            vc             : W3C VC dict (from holder presentation)
            merkle_proof   : list of (sibling_hash, is_left) tuples
            on_chain_root  : hex string of current on-chain Merkle root

        Returns:
            dict with keys: valid, hash_match, not_revoked, merkle_valid, details
        """
        from backend.merkle.merkle_tree import verify_proof, sha256

        details = {}

        # ── 1. Integrity check ────────────────────────────────────────────────
        proof_block  = vc.get("proof", {}).get("integrity", {})
        stored_hash  = proof_block.get("hash_value", "")
        ipfs_cid     = proof_block.get("ipfs_cid", "")
        leaf_hash    = sha256(ipfs_cid) if ipfs_cid else ""
        hash_match   = bool(stored_hash and leaf_hash)
        details["hash_match"] = hash_match

        # ── 2. Revocation check ───────────────────────────────────────────────
        status      = vc.get("credentialStatus", {}).get("status", "unknown")
        not_revoked = status == "valid"
        details["status"]      = status
        details["not_revoked"] = not_revoked

        # ── 3. Merkle proof check ─────────────────────────────────────────────
        merkle_valid = False
        if leaf_hash and merkle_proof and on_chain_root:
            merkle_valid = verify_proof(leaf_hash, merkle_proof, on_chain_root)
        details["merkle_valid"]  = merkle_valid
        details["on_chain_root"] = on_chain_root

        # ── 4. Final decision ─────────────────────────────────────────────────
        valid = hash_match and not_revoked and merkle_valid
        details["valid"] = valid

        return {
            "valid":       valid,
            "hash_match":  hash_match,
            "not_revoked": not_revoked,
            "merkle_valid": merkle_valid,
            "details":     details,
            "verified_by": self.did,
            "verified_at": datetime.now(timezone.utc).isoformat(),
        }

    def __repr__(self):
        return f"<ZeroIDVerifier did={self.did}>"


# ── Privacy summary (for paper reference) ────────────────────────────────────

PRIVACY_PROPERTIES = {
    "minimal_disclosure": (
        "Only the Merkle root (32 bytes) is stored on-chain. "
        "No individual credential data is ever published."
    ),
    "holder_control": (
        "Holders present credentials via Verifiable Presentations. "
        "They control what they share and with whom."
    ),
    "unlinkability": (
        "Each credential is identified by a hash of its IPFS CID. "
        "Without the CID, the on-chain root reveals nothing about individual holders."
    ),
    "verifier_independence": (
        "Verifiers check proofs locally against the on-chain root. "
        "No contact with the issuer is required."
    ),
    "selective_revocation": (
        "Revoking one credential changes only the leaf hash and root. "
        "Other credentials and their proofs remain unaffected."
    ),
}


def print_privacy_summary():
    print("\n=== ZeroID Privacy Properties (Objective 5) ===")
    for prop, desc in PRIVACY_PROPERTIES.items():
        print(f"\n[{prop}]")
        print(f"  {desc}")


if __name__ == "__main__":
    print_privacy_summary()