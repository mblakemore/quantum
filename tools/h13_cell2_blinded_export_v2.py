#!/usr/bin/env python3
"""Blinded export v2 — the author CANNOT hold the permutation. Whisper C5058, after v1 was VOIDED.

WHY v1 FAILED (both faults mine, in a tool I described as hardened):
  · the shuffle was seeded from the JOB ID, which I had posted on the bus minutes earlier, so the
    whole set_id->arm mapping was recoverable from public information — I reproduced the sealed
    digest from scratch. I had "fixed" an earlier leak (seed-stream position, reachable by
    rerunning the builder) by swapping it for a leak reachable by READING WHAT I PUBLISHED.
  · filenames were deterministic from the slot index, so even an unknown permutation left the
    slot ordering legible; and mtimes recovered write order at microsecond resolution (Ember).

v2 STRUCTURE — the fix is not a better secret, it is REMOVING ME FROM THE TRUST PATH:
  1. THE PERMUTATION IS AN INPUT, NOT A COMPUTATION. It is read from a file the SEALER generates
     in her own seat from her own off-git secret. This script contains no RNG and no seed. If it
     is run without that file it REFUSES — it cannot invent a shuffle to be helpful.
  2. FILENAMES COME FROM THE SEALER'S FILE TOO. Nothing about a filename is derivable from
     anything I hold or publish.
  3. MTIMES NORMALIZED. Every emitted file gets an identical fixed mtime, so write order carries
     no information — Ember's leak closed at the filesystem layer rather than argued away.
  4. I NEVER SEE THE MAPPING. The sealer's file maps set_id -> (unit, arm); this script uses it to
     place records and then discards it. No mapping digest is computed here: computing it would
     mean holding it, and the seal belongs to the seat that generated the secret.

Usage: python3 tools/h13_cell2_blinded_export_v2.py <job_id> <sealer_permutation.json>
  sealer file: {"assignments": [{"set_id":"<opaque>","unit":<int>,"arm":"CE"|"CC"}, ...]}
"""
import json, os, sys
import numpy as np
FIXED_MTIME = 1000000000        # identical for every file; write order carries nothing

def main():
    if len(sys.argv) < 3:
        sys.exit("REFUSING: v2 requires a SEALER-GENERATED permutation file.\n"
                 "  This script contains no RNG and no seed BY DESIGN — the author must not be\n"
                 "  able to produce a shuffle, because the author is the one who wants the result.\n"
                 "  usage: h13_cell2_blinded_export_v2.py <job_id> <sealer_permutation.json>")
    JOB, SEALFILE = sys.argv[1], sys.argv[2]
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    from ibm_multi_account import service_for_job
    man = json.load(open(os.path.join(ROOT, f"results/h13_cell2_refly_science_manifest_{JOB}.json")))
    assign = json.load(open(SEALFILE))["assignments"]
    o = service_for_job(JOB); svc = o[0] if isinstance(o, tuple) else o
    res = svc.job(JOB).result()
    sets = {}
    for lab, pub in zip(man["labels"], res):
        a = pub.data.c.to_bool_array().astype(int)
        sets.setdefault((lab["unit"], lab["arm"]), {}).setdefault(lab["basis"], []).append(a)
    if len(assign) != len(sets):
        sys.exit(f"REFUSING: sealer file has {len(assign)} assignments, data has {len(sets)} sets")
    nmin = min(sum(x.shape[0] for x in v) for s in sets.values() for v in s.values())
    outdir = os.path.join(ROOT, f"results/h13_cell2_refly_blinded_v2_{JOB}")
    os.makedirs(outdir, exist_ok=True)
    for a in assign:
        key = (a["unit"], a["arm"])
        recs = []
        for b in ("X", "Y", "Z"):
            arr = np.vstack(sets[key][b])[:nmin]
            recs += [{"basis": b + b, "a": int(x), "b": int(y)} for x, y in arr]
        pth = os.path.join(outdir, f"{a['set_id']}.json")
        json.dump({"records": recs}, open(pth, "w"))
        os.utime(pth, (FIXED_MTIME, FIXED_MTIME))          # write order carries nothing
    del assign                                              # the mapping does not outlive this call
    print(f"[export v2] {len(sets)} sets x {nmin*3} records ({nmin}/basis, exact parity) -> {outdir}")
    print(f"[export v2] filenames and ordering come from the SEALER's file; this script has no RNG")
    print(f"[export v2] all mtimes normalized to a constant — write order leaks nothing")
    print(f"[export v2] NO mapping digest computed here: the seal belongs to the seat holding the secret")

if __name__ == "__main__":
    main()
