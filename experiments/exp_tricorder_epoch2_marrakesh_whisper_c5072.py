#!/usr/bin/env python3
"""TRICORDER Epoch-2 re-fly — the current-epoch revival scout (Whisper C5072, board #144).

Creator triple-GO general#11436 (streams 1/2/3); this flight is the GATE for stream 1 (the
TLS-turbine): is anything reviving on marrakesh in the CURRENT calibration window?

Identical instrument to the C5004 same-epoch graduation flight (one code path: build_twins /
DEPTHS / SEED imported from the widesweep, exactly as C5004 did). Differences, all logistics:
  - account: IBMQ_ALT4 (registry: only open free tank; whisper-de/WhisperPaid untouched)
  - fresh manifest path (the C5004 manifest is a flown record and stays untouched)
  - pending_jobs captured AT SUBMIT (Creator directive, flight-kit standard since ce5ad69)

PRE-REGISTERED SCOPE (before decode; inherits C5004's scope verbatim plus):
  - Decision rule (board #144, pre-stated): live revival with resolvable period -> open the
    turbine design row; epoch quiet -> post the null, stream 3 decision separately.
  - The kingston/C5005 {26,53,73} set carries NO expectation here: drifter sets are
    epoch-volatile (C5002); discovery is against the CURRENT marrakesh population.
  - Valid outcomes: revival found (with depth-period + amplitude) OR stable/monotone
    (equally valid; the null gates the fallback). No post-hoc pull toward drama.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from exp_crossblock_widesweep import build_twins, SEED, DEPTHS
from qiskit import transpile
import numpy as np

BACKEND = "ibm_marrakesh"
NPHYS = 156
OUT = os.path.join(QROOT, "results", "exp_tricorder_epoch2_marrakesh_c5072_manifest.json")


def main(submit=False):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT4")  # named account, no fallback (c4217_018)
    backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"marrakesh cal epoch: {props.last_update_date}")

    twins, active = build_twins(backend)
    print(f"[$0-validate] twin register (active 2q qubits): {len(active)} on marrakesh")

    pubs, meta = [], []
    for D, mc in twins:
        tqc = transpile(mc, backend, optimization_level=0, initial_layout=list(range(NPHYS)),
                        seed_transpiler=SEED)
        pubs.append((tqc, None, 12000))
        meta.append({"block": f"twin_d{D}", "d2q": D, "shots": 12000})

    man = {"card": "exp_tricorder_epoch2_marrakesh", "cycle": "C5072", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date), "depths": DEPTHS,
           "register": active, "seed": SEED, "account": "IBMQ_ALT4",
           "purpose": "Current-epoch revival scout (board #144, Creator GO general#11436): gate for the TLS-turbine",
           "prereg_scope": {
               "inherits": "C5004 same-epoch scope verbatim (exp_tricorder_sameepoch_marrakesh_manifest.json)",
               "decision_rule": "live revival + resolvable period -> turbine design row; quiet -> null posted, stream-3 fallback decided separately",
               "no_expectation_carried": "kingston/C5005 {26,53,73} set is epoch-stale by C5002; discovery vs CURRENT marrakesh population",
               "valid_outcomes": ["revival found (depth-period + amplitude)", "stable/monotone (null gates fallback)"]},
           "pubs_meta": meta}
    if submit:
        man["pending_jobs_at_submit"] = backend.status().pending_jobs
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {BACKEND} (pending at submit: {man['pending_jobs_at_submit']})")
    else:
        print("[dry] not submitted (pass --submit to fly)")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
