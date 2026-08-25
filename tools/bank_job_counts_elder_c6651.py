#!/usr/bin/env python3
"""bank_job_counts_elder_c6651.py — fetch ONE job's per-pub counts and bank them as an artifact (court seat, C6651).

Every ratification this cycle needed the flown counts and half of them were not on disk (F126's producing artifact
was missing until banked; F124's three jobs had decodes but no counts). A ratification that starts with a fetch is a
ratification that can stop working when the provider's retention window closes — retention observed at 16d and 36d
with zero losses, which is a bound, not a guarantee. So: bank first, recompute from the file.

Usage: python3 tools/bank_job_counts_elder_c6651.py <job_id> <tag>     -> results/<tag>_counts_<job>_elder_c6651.json
Never overwrites an existing bank (append-only discipline: a second fetch goes to a new file if it differs).
"""
import json, os, sys, datetime as dt, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.join(ROOT, "scripts"))
from ibm_multi_account import service_for_job

def main():
    if len(sys.argv) < 3: sys.exit(__doc__)
    job, tag = sys.argv[1], sys.argv[2]
    out = os.path.join(ROOT, "results", f"{tag}_counts_{job}_elder_c6651.json")
    if os.path.exists(out): sys.exit(f"REFUSED: {out} exists — banks are append-only; delete deliberately if you mean to refetch")
    svc, acct = service_for_job(job)
    res = svc.job(job).result()
    pubs = []
    for i, r in enumerate(res):
        creg = "c" if hasattr(r.data, "c") else ("meas" if hasattr(r.data, "meas") else None)
        if creg is None:
            names = [n for n in dir(r.data) if not n.startswith("_")]
            creg = names[0]
        counts = getattr(r.data, creg).get_counts()
        pubs.append({"index": i, "creg": creg, "counts": {str(k): int(v) for k, v in counts.items()}, "shots": int(sum(counts.values()))})
    doc = {"job": job, "tag": tag, "account": acct, "fetched_at": dt.datetime.now(dt.timezone.utc).isoformat(), "n_pubs": len(pubs),
           "total_shots": sum(p["shots"] for p in pubs), "note": "raw per-pub counts as returned by the sampler; keys are the sampler's bitstrings (Qiskit little-endian: rightmost char = qubit 0 of the creg)", "pubs": pubs}
    json.dump(doc, open(out, "w"), indent=1)
    h = hashlib.sha256(open(out, "rb").read()).hexdigest()[:16]
    print(f"banked {len(pubs)} pubs / {doc['total_shots']} shots from {acct} -> {os.path.relpath(out, ROOT)} (sha256 {h})")

if __name__ == "__main__":
    main()
