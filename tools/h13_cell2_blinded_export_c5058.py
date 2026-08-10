#!/usr/bin/env python3
"""H13 Cell 2 — BLINDED RECORDS EXPORT, built to Ember's seal/fly spec (general#9067).

FIELD LIST IS EXHAUSTIVE, NOT MINIMUM: run_index, group ("P"/"Q", re-randomised per run),
basis, outcomes[a,b] (+-1, fixed arm-independent slot order). Nothing else leaves this tool.
The P/Q <-> CE/CC mapping is drawn from the SAME F-IND stream as tau (seed 20260811), continuing
after the tau draws, so it is reproducible and sealable; only its sha256 is published pre-decode.

Usage: python3 tools/h13_cell2_blinded_export_c5058.py <science_job_id>
"""
import json, sys, os, hashlib
import numpy as np

SEED, TAU_MAX_NS, N_DRAWS, N_RUNS, BASES = 20260811, 30000, 20, 40, ("X", "Y", "Z")

def replay_stream_and_draw_mapping():
    """Replay the exact draw sequence the submit script consumed, then draw the P/Q mapping."""
    rng = np.random.default_rng(SEED)
    for _ in range(N_DRAWS):                      # pre-run block: tau_ce, tau_cc per unit
        rng.integers(0, TAU_MAX_NS); rng.integers(0, TAU_MAX_NS)
    for _ in range(N_RUNS):                       # science block: same
        rng.integers(0, TAU_MAX_NS); rng.integers(0, TAU_MAX_NS)
    # 40 independent group assignments: which of CE/CC is called "P" in this run
    return [{"P": "CE", "Q": "CC"} if int(rng.integers(0, 2)) == 0 else {"P": "CC", "Q": "CE"}
            for _ in range(N_RUNS)]

def main():
    job_id = sys.argv[1]
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.join(root, "scripts"))
    from ibm_multi_account import service_for_job
    man = json.load(open(os.path.join(root, f"results/h13_cell2_manifest_{job_id}.json")))
    labels = man["labels_science"]
    o = service_for_job(job_id); svc = o[0] if isinstance(o, tuple) else o
    res = svc.job(job_id).result()

    mapping = replay_stream_and_draw_mapping()
    map_digest = hashlib.sha256(json.dumps(mapping, sort_keys=True).encode()).hexdigest()

    # collect per (run, arm, basis) outcome lists
    cells = {}
    for lab, pub in zip(labels, res):
        arr = pub.data.c.to_bool_array().astype(int)          # shots x 2, slot order = (first, second)
        cells[(lab["unit"], lab["arm"], lab["basis"])] = arr

    # EXACT record-count parity per (run, group, basis): truncate all cells to the global minimum
    nmin = min(a.shape[0] for a in cells.values())
    records = []
    for run in range(N_RUNS):
        for group in ("P", "Q"):
            arm = mapping[run][group]
            for b in BASES:
                a = cells[(run, arm, b)][:nmin]
                records.append({"run_index": run, "group": group, "basis": b,
                                "outcomes": [[1 - 2 * int(x), 1 - 2 * int(y)] for x, y in a]})
    counts = {(r["run_index"], r["group"], r["basis"]): len(r["outcomes"]) for r in records}
    assert len(set(counts.values())) == 1, f"PARITY VIOLATION: {set(counts.values())}"

    out = os.path.join(root, f"results/h13_cell2_blinded_records_{job_id}.json")
    json.dump({"records": records}, open(out, "w"))
    seal = os.path.join(root, f"results/h13_cell2_mapping_digest_{job_id}.json")
    json.dump({"mapping_sha256": map_digest, "seed": SEED,
               "realized_draws_sha256_16": man["realized_draws_sha256_16"],
               "n_runs": N_RUNS, "records_per_cell": nmin,
               "note": "mapping itself withheld; Ember unseals after Elder's decisions hash"},
              open(seal, "w"), indent=1)
    print(f"[export] {len(records)} cells x {nmin} records each (exact parity enforced)")
    print(f"[export] blinded records -> {out}")
    print(f"[seal]   mapping sha256 = {map_digest}")
    print(f"[seal]   digest file -> {seal}")
    fields = set().union(*[set(r.keys()) for r in records])
    print(f"[audit]  field set emitted = {sorted(fields)} (spec: run_index, group, basis, outcomes)")

if __name__ == "__main__":
    main()
