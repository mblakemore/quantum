#!/usr/bin/env python3
"""ARM-N RE-FLY bundle builder (Whisper C5018) — written BEFORE the flight, so nothing has to
be authored while data is on the table (the discipline Ember demonstrated at quantum@fe16a24).

Emits, from the landed job:
  * readout.{drifter,null} + *_ids   — pairs SELECTED by the frozen rule from cal_START,
                                        VERIFIED (by Ember's tool) against cal_END
  * hazard_removed_dt                — the receipt (general#4852/#4857 key): measured
                                        census->cal_start drift per candidate = the gap this
                                        design removes rather than detects. Gates nothing.
  * structure/durations/trial_order  — preconditions 2 and 3 inputs
  * pairing_reproduction             — rule + cal_start marginals so Elder recomputes and
                                        compares; divergence is fail-closed, not adjudicated.
Data pubs are NOT opened here: cal blocks only (blind discipline).
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))
from exp_armn_refly_whisper_c5018 import frozen_pairing, SELECT_BAR

def marg(res, i, q):
    c = res[i].data.meas.get_counts(); t = sum(c.values())
    return sum(n for bs, n in c.items() if bs.replace(" ", "")[::-1][q] == "1") / t

def build_bundle(jid):
    from ibm_multi_account import service_for_job
    man = json.load(open(os.path.join(RES, f"armn_refly_manifest_{jid}.json")))
    svc, _ = service_for_job(jid); res = svc.job(jid).result()
    ci = {m["block"]: i for i, m in enumerate(man["pubs_meta"]) if m["block"].startswith("cal")}
    cand = man["candidates"]["drifter"] + man["candidates"]["null"]
    def prof(tag0, tag1):
        return {q: (marg(res, ci[tag0], q) + (1 - marg(res, ci[tag1], q))) / 2 for q in cand}
    p_start, p_end = prof("cal0_start", "cal1_start"), prof("cal0_end", "cal1_end")
    pairs, ungraded = frozen_pairing(p_start, man["candidates"]["drifter"],
                                     man["candidates"]["null"])
    cen = {int(k): v for k, v in man["census_profiles"].items()}
    bundle = {
        "readout": {"drifter": [round(p_start[p["drifter"]], 6) for p in pairs],
                    "null": [round(p_start[p["null"]], 6) for p in pairs],
                    "drifter_ids": [p["drifter"] for p in pairs],
                    "null_ids": [p["null"] for p in pairs]},
        "readout_bracket": {"start": {"drifter": [round(p_start[p["drifter"]], 6) for p in pairs],
                                      "null": [round(p_start[p["null"]], 6) for p in pairs],
                                      "drifter_ids": [p["drifter"] for p in pairs],
                                      "null_ids": [p["null"] for p in pairs]},
                            "end": {"drifter": [round(p_end[p["drifter"]], 6) for p in pairs],
                                    "null": [round(p_end[p["null"]], 6) for p in pairs],
                                    "drifter_ids": [p["drifter"] for p in pairs],
                                    "null_ids": [p["null"] for p in pairs]}},
        # THE RECEIPT — measured census->start drift, the hazard the design removed
        "hazard_removed_dt": {str(q): round(abs(p_start[q] - cen[q]), 6) for q in cand if q in cen},
        "hazard_removed_note": ("measured census->cal_start profile drift per candidate; this is "
                                "the gap the single-job design eliminates by construction rather "
                                "than detects. Gates nothing; quantifies the design argument."),
        "pairing_reproduction": {"rule": man["frozen_pairing_rule"], "select_bar": SELECT_BAR,
                                 "cal_start_profiles": {str(q): round(v, 6) for q, v in p_start.items()},
                                 "flown_pairs": pairs, "not_graded": ungraded},
        "structure": {"drifter": {f"q{p['drifter']}": man["structures"][f"q{p['drifter']}"] for p in pairs},
                      "null": {f"q{p['null']}": man["structures"][f"q{p['null']}"] for p in pairs}},
        "scheduled_duration_dt": {"drifter": {f"q{p['drifter']}": man["durations"][f"q{p['drifter']}"]["Q"] for p in pairs},
                                  "null": {f"q{p['null']}": man["durations"][f"q{p['null']}"]["Q"] for p in pairs}},
        # trial_order delivered so check 4 VERIFIES rather than argues (Ember #4889). Honest
        # scope note: in this design the circuits are deterministic and per-block, so the order
        # is consumed at DECODE (which trial takes which shots), not at flight. Delivering it
        # lets the checker confirm the order the decode will actually use, generated here as a
        # pure function of the PUBLIC seed fixed before any label existed.
        "trial_order": {f"k{k}": [int(x) for x in
                                  np.random.default_rng(man["trial_order_seed"] + k).permutation(man["M"])]
                        for k in man["rungs_assembled_at_decode"]},
        "trial_order_seed": man["trial_order_seed"], "M": man["M"],
        # DECLARE the derivation (Ember #4909): a consumer that infers the scheme can only say
        # "it matched something"; one that reads it declared can say "it matched the DECLARED
        # scheme". Same fix pattern as the drifter cut — the rule goes in the artifact.
        "trial_order_derivation": ("per rung k: numpy.random.default_rng(trial_order_seed + k)"
                                   ".permutation(M) — independent generator per rung, NOT a "
                                   "sequential draw from one generator (which is what the first "
                                   "arm-N flight used)."),
        "trial_order_scope": ("decode-consumed, not flight-encoded: deterministic circuits mean "
                              "trial assignment happens at decode. Pure function of the public "
                              "seed, which was fixed before labels existed and cannot encode them."),
        "job_id": jid, "note": "cal pubs only; data pubs UNOPENED at bundle time",
    }
    out = os.path.join(RES, f"armn_refly_bundle_{jid}.json")
    json.dump(bundle, open(out, "w"), indent=1)
    worst = max((abs(p_start[p["drifter"]] - p_start[p["null"]]) for p in pairs), default=0)
    print(f"pairs selected: {[(p['drifter'], p['null'], p['diff']) for p in pairs]}")
    print(f"not graded (no qualifying partner): {ungraded}")
    print(f"worst selection diff {worst:.6f} (bar {SELECT_BAR}); receipt entries "
          f"{len(bundle['hazard_removed_dt'])}, max hazard removed "
          f"{max(bundle['hazard_removed_dt'].values(), default=0):.6f}")
    print(f"-> {out}")

if __name__ == "__main__":
    build_bundle(sys.argv[1])
