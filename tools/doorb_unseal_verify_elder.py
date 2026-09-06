#!/usr/bin/env python3
"""doorb_unseal_verify_elder.py — verify a doorb v2 UNSEAL against its published commitment (Elder, C6655, board#400).

    python3 tools/doorb_unseal_verify_elder.py --commitment experiments/doorb_commitments/doorb_commitment_v2_n20_w12.json \
        --P <revealed P> --salt <revealed salt hex>
    exit 0 = MATCH (recomputed v2 preimage digest == commitment_sha256 AND weight(P) == sealed weight)
    exit 1 = MISMATCH (say which: digest / weight / alphabet)     exit 2 = cannot verify (file/import problem = UNKNOWN)

Uses the sealer's OWN preimage_v2 (tools/doorb_sealer_ember_c4262.py) so the verifier cannot drift from the seal;
every bound field (n, w, alphabet, identity_excluded, prereg_freeze, order_of_operations) is read from the
commitment record, never retyped. The sealer's --selftest (known preimage -> known digest) is the positive control.
"""
import argparse, importlib.util, json, os, sys
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--commitment", required=True); ap.add_argument("--P", required=True); ap.add_argument("--salt", required=True)
    a = ap.parse_args()
    try:
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        spec = importlib.util.spec_from_file_location("sealer", os.path.join(root, "tools/doorb_sealer_ember_c4262.py"))
        sealer = importlib.util.module_from_spec(spec); spec.loader.exec_module(sealer)
        c = json.load(open(a.commitment))
    except Exception as e:
        print(f"UNKNOWN: cannot verify ({e})"); return 2
    n = int(c["n"]); w = int(c["weight"]); P = a.P.strip().upper()
    problems = []
    if len(P) != n or any(ch not in c.get("alphabet", "IXYZ") for ch in P): problems.append(f"P is not {n} chars over {c.get('alphabet','IXYZ')}")
    wP = sum(1 for ch in P if ch != "I")
    if wP != w: problems.append(f"weight(P)={wP} != sealed weight {w}")
    if c.get("identity_excluded") in (True, "True", 1) and wP == 0: problems.append("all-identity P with identity_excluded")
    import hashlib
    pre = sealer.preimage_v2(n, w, P, a.salt.strip(), c["prereg_freeze"], c["order_of_operations"],
                             alphabet=c.get("alphabet", "IXYZ"), identity_excluded=c.get("identity_excluded") in (True, "True", 1))
    digest = hashlib.sha256(pre.encode()).hexdigest()
    if digest != c["commitment_sha256"]: problems.append(f"digest MISMATCH: recomputed {digest[:16]}… vs committed {c['commitment_sha256'][:16]}…")
    if problems:
        print("MISMATCH: " + "; ".join(problems)); return 1
    print(f"MATCH: v2 preimage digest {digest[:16]}… == commitment; weight {wP} == sealed {w}; n={n}; freeze {c['prereg_freeze']}"); return 0
if __name__ == "__main__": sys.exit(main())
