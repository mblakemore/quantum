#!/usr/bin/env python3
"""H13 Cell 2 — BLINDED RECORDS EXPORT — reconciles Ember's seal spec (#9067) with Elder's
decoder seam + unpaired requirement (#9069).

THE RECONCILIATION (author seat, C5058): Ember's run_index+group form makes PAIRING RECOVERABLE
(same run_index => one CE, one CC), which is the FORCED-CHOICE experiment; section A prices the
UNPAIRED one. Elder's recommendation is adopted: 80 opaque sets, shuffled, no run_index, no group
field, pairing unrecoverable from content, ordering or filename. Ember's INTENT — that no single
inference generalises across sets — is strictly better served: there is no label to generalise.
The seal becomes an 80-entry {set_id -> arm} mapping; only its sha256 is published pre-decode.

FILE SEAM (Elder #9069, frozen contract): one file per record set, flat dir, opaque uuid names,
{"records":[{"basis":"XX","a":0,"b":1}, ...]}; RAW 0/1 emitted — his decoder owns the 0->+1,1->-1
mapping and this tool does NOT re-map upstream. No arm/scenario/label/circuit key anywhere.

Usage: python3 tools/h13_cell2_blinded_export_c5058.py <job_id> [--prerun] [--calibration-only]
"""
import json, sys, os, hashlib
import numpy as np

SEED, TAU_MAX_NS, N_DRAWS, N_RUNS, BASES = 20260811, 30000, 20, 40, ("X", "Y", "Z")

def sealed_permutation(n_sets):
    """Continue the SAME F-IND stream past the tau draws; shuffle set order + assign opaque ids."""
    rng = np.random.default_rng(SEED)
    for _ in range(N_DRAWS + N_RUNS):
        rng.integers(0, TAU_MAX_NS); rng.integers(0, TAU_MAX_NS)
    perm = rng.permutation(n_sets)
    uids = [hashlib.sha256(f"{SEED}:{i}".encode()).hexdigest()[:16] for i in range(n_sets)]
    return perm, uids

def main():
    job_id = sys.argv[1]
    prerun = "--prerun" in sys.argv
    calib_only = "--calibration-only" in sys.argv
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(root, "scripts"))
    from ibm_multi_account import service_for_job
    manp = [f for f in os.listdir(os.path.join(root, "results")) if f.startswith("h13_cell2_manifest_")][0]
    man = json.load(open(os.path.join(root, "results", manp)))
    labels = man["labels_prerun"] if prerun else man["labels_science"]
    o = service_for_job(job_id); svc = o[0] if isinstance(o, tuple) else o
    res = svc.job(job_id).result()

    # one SET = (unit, arm): 3 diagonal bases inside it. 40 runs x 2 arms = 80 sets.
    sets = {}
    for lab, pub in zip(labels, res):
        arr = pub.data.c.to_bool_array().astype(int)       # shots x 2; slot order = (first-listed, second-listed)
        sets.setdefault((lab["unit"], lab["arm"]), {})[lab["basis"]] = arr
    keys = sorted(sets.keys())
    nmin = min(a.shape[0] for s in sets.values() for a in s.values())   # EXACT parity, enforced
    perm, uids = sealed_permutation(len(keys))

    outdir = os.path.join(root, f"results/h13_cell2_blinded_{'prerun' if prerun else 'science'}_{job_id}")
    os.makedirs(outdir, exist_ok=True)
    mapping = {}
    for slot, src_idx in enumerate(perm):
        unit, arm = keys[src_idx]
        uid = uids[slot]
        recs = []
        for b in BASES:
            a = sets[(unit, arm)][b][:nmin]
            recs += [{"basis": b + b, "a": int(x), "b": int(y)} for x, y in a]   # RAW 0/1, no upstream re-map
        json.dump({"records": recs}, open(os.path.join(outdir, f"{uid}.json"), "w"))
        mapping[uid] = arm
        if calib_only: break
    digest = hashlib.sha256(json.dumps(mapping, sort_keys=True).encode()).hexdigest()
    print(f"[export] {len(mapping)} sets x {nmin*3} records ({nmin} per basis, exact parity) -> {outdir}")
    print(f"[audit]  per-record fields = ['basis','a','b']; per-file keys = ['records']; no arm/scenario/label/circuit")
    print(f"[seal]   {len(mapping)}-entry set_id->arm mapping sha256 = {digest}")
    if not calib_only:
        json.dump({"mapping_sha256": digest, "seed": SEED, "n_sets": len(mapping),
                   "records_per_basis": nmin, "realized_draws_sha256_16": man["realized_draws_sha256_16"],
                   "structure": "UNPAIRED — pairing unrecoverable from content, order or filename (Elder #9069)",
                   "note": "mapping withheld; Ember unseals after Elder's decisions hash"},
                  open(os.path.join(root, f"results/h13_cell2_mapping_digest_{job_id}.json"), "w"), indent=1)

if __name__ == "__main__":
    main()
