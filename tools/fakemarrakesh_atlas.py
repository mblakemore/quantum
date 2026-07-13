#!/usr/bin/env python3
"""FakeMarrakesh+ residual atlas v1 (Whisper C4564, gaps-round-2 item #1).

Assembles the preview-vs-measured table across the campaign: for every experiment
where BOTH a noise-model preview (FakeMarrakesh / from_backend Aer) AND a hardware
result exist for the same observable, one row:

    (experiment, observable, family, depth_2q, delays, ideal, preview, measured,
     window_sentinel_hw, window_sentinel_preview, source)

Emits results/model_residual_atlas.json + a markdown table, and computes the
headline statistic: the MODEL OPTIMISM factor  ln(ratio_preview / ratio_hw)
(how much of the ideal→hardware haircut the noise model fails to predict),
by depth class.

v1 scope note: rows are harvested from machine-readable results where available
and CURATED WITH CITATIONS where the number lives in a finding/prereg doc (older
arcs are heterogeneous text). Growth rule (same as the spec ledger): every future
graded experiment appends its row in the grade cycle. Rows deliberately EXCLUDE
sim-only experiments and hardware-only experiments (no pair, no row).
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "..", "results")

# family: 'amplitude' = signal-amplitude-like (depth-decay-law scope),
#         'probability' = bounded score/retention (own floor), kept separate.
ROWS = [
    # ---- witness arc (4-CZ class) ----
    dict(exp="exp91/F75", observable="witness W", family="amplitude", depth=4,
         delays=False, ideal=2.0, preview=1.934, measured=1.781,
         sent_hw=None, sent_prev=None,
         source="F75 finding table (sim/noise-model/hardware)"),
    dict(exp="exp93/F77", observable="DISC_switch (same-window)", family="amplitude",
         depth=4, delays=False, ideal=2.0, preview=1.93, measured=1.900,
         sent_hw=None, sent_prev=None,
         source="F77 finding + ORQ P2 table"),
    # ---- game (probability family) ----
    dict(exp="exp105", observable="game score", family="probability", depth=4,
         delays=False, ideal=1.0, preview=None, measured=0.9769,
         sent_hw=None, sent_prev=None,
         source="exp105_hw_results.json (no FakeMarrakesh game preview banked -> no optimism stat)"),
    # ---- capacity arc (amplitude family) ----
    dict(exp="exp106/F83", observable="capacity Rbar", family="amplitude", depth=4,
         delays=False, ideal=8 / 15, preview=0.510, measured=0.5034,
         sent_hw=None, sent_prev=None,
         source="exp106 prereg sim gates + exp106_hw_results.json"),
    dict(exp="exp107/F85", observable="capacity Rbar (N=3)", family="amplitude",
         depth=110, delays=False, ideal=0.6730, preview=0.518, measured=0.3817,
         sent_hw=0.669, sent_prev=0.744,
         source="F85 finding (preview R~0.518, deep sentinel 0.744 vs 0.671/0.655/0.681)"),
    dict(exp="exp107 deep sentinel", observable="retention P(000)", family="probability",
         depth=110, delays=False, ideal=1.0, preview=0.744, measured=0.669,
         sent_hw=None, sent_prev=None, source="F85 finding"),
    # ---- thermal arc ----
    dict(exp="exp108", observable="thermal Delta", family="amplitude", depth=22,
         delays=False, ideal=0.2319, preview=0.2275, measured=0.1796,
         sent_hw=0.856, sent_prev=0.9575,
         source="exp108_feasibility.json + exp108_grade.json"),
    dict(exp="exp108 retention", observable="retention P(c=+,t=0)", family="probability",
         depth=22, delays=False, ideal=1.0, preview=0.9575, measured=0.856,
         sent_hw=None, sent_prev=None, source="exp108 grade"),
    # exp108b (C4591): NO-TEST — calib gate failed (T1 queue-drift), preview-vs-measured
    # comparison of the THERMAL observable would be conditioned on a broken prep; the
    # honest atlas row is the retention sentinel only (prep-independent probe).
    dict(exp="exp108b retention (NO-TEST run)", observable="retention P(c=+,t=0)",
         family="probability", depth=22, delays=True, ideal=1.0, preview=0.9555,
         measured=0.908, sent_hw=None, sent_prev=None,
         source="exp108b_feasibility.json + exp108b_grade.json (first delay-bearing row)"),
    dict(exp="exp108c retention (WIN run)", observable="retention P(c=+,t=0)",
         family="probability", depth=22, delays=True, ideal=1.0, preview=0.9555,
         measured=0.9425, sent_hw=None, sent_prev=None,
         source="exp108c_grade.json (good window: mean of 3 replicates 0.940-0.951)"),
    # ---- resource-comparison arc ----
    dict(exp="exp111 switch S", observable="matched-filter S (parity)",
         family="amplitude", depth=4, delays=False, ideal=0.2500, preview=0.2463,
         measured=0.2221, sent_hw=None, sent_prev=None,
         source="exp111_S_previews.json + exp111_grade.json (preview = opt-3 circuits, noted)"),
    dict(exp="exp111 paths S", observable="matched-filter S (visibility)",
         family="amplitude", depth=3, delays=False, ideal=0.1250, preview=0.1275,
         measured=0.1140, sent_hw=None, sent_prev=None,
         source="exp111_S_previews.json + exp111_grade.json (label-avg depth 2-4)"),
    # ---- routing arc (Exp110, C4597) ----
    dict(exp="exp110 swap N=6", observable="mean 4-prep survival",
         family="probability", depth=18, delays=False, ideal=1.0, preview=0.9644,
         measured=0.9452, sent_hw=None, sent_prev=None,
         source="exp110_grade.json (good window; model GOOD for unitary routing)"),
    dict(exp="exp110 teleport N=6", observable="mean 4-prep survival (feedforward)",
         family="probability+feedforward", depth=12, delays=False, ideal=1.0,
         preview=0.9237, measured=0.7477, sent_hw=None, sent_prev=None,
         source="exp110_grade.json — FIRST feedforward row: +0.212 ln = the unmodeled "
                "feedforward-latency cost; largest observable-family gap in the atlas"),
    dict(exp="exp113 teleported witness", observable="DISC (teleported control)",
         family="amplitude+feedforward-frame", depth=6, delays=False, ideal=2.0,
         preview=1.9375, measured=1.8250, sent_hw=None, sent_prev=None,
         source="exp113_grade.json (frame arm; +0.060 ln — teleport haircut visible, model-blind as usual)"),
    dict(exp="exp114 purified", observable="CHSH S (post-selected)",
         family="amplitude", depth=10, delays=False, ideal=2.264, preview=2.1892,
         measured=2.1437, sent_hw=None, sent_prev=None,
         source="exp114_grade.json (layout-matched preview; +0.021 ln — model GOOD at 10 CZ)"),
    dict(exp="exp114 raw@p*", observable="CHSH S (injected noise)",
         family="amplitude", depth=1, delays=False, ideal=1.998, preview=1.899,
         measured=1.9037, sent_hw=None, sent_prev=None,
         source="exp114_grade.json (-0.002 ln — dead on)"),
    # ---- comms arc ----
    dict(exp="exp109 superdense", observable="p_success (4-msg decode)",
         family="probability", depth=2, delays=False, ideal=1.0, preview=0.9794,
         measured=0.9688, sent_hw=0.982, sent_prev=None,
         source="exp109_feasibility.json + exp109_grade.json"),
]


def compute(rows):
    out = []
    for r in rows:
        row = dict(r)
        if r["preview"] is not None:
            row["ratio_preview"] = r["preview"] / r["ideal"]
            row["ratio_hw"] = r["measured"] / r["ideal"]
            row["optimism_ln"] = float(np.log(row["ratio_preview"] / row["ratio_hw"]))
        out.append(row)
    return out


def main():
    rows = compute(ROWS)
    amp = [r for r in rows if r.get("optimism_ln") is not None]
    print(f"{'experiment':24s} {'obs':28s} {'d':>4s} {'prev/ideal':>10s} {'hw/ideal':>9s} {'optimism':>9s}")
    for r in amp:
        print(f"{r['exp']:24s} {r['observable']:28s} {r['depth']:4d} "
              f"{r['ratio_preview']:10.3f} {r['ratio_hw']:9.3f} {r['optimism_ln']:+9.3f}")
    # depth-class summary
    classes = {"shallow (<=8 CZ)": [r for r in amp if r["depth"] <= 8],
               "mid (9-50 CZ)": [r for r in amp if 8 < r["depth"] <= 50],
               "deep (>50 CZ)": [r for r in amp if r["depth"] > 50]}
    print("\nMODEL OPTIMISM by depth class (ln ratio_preview/ratio_hw):")
    summary = {}
    for name, rs in classes.items():
        if rs:
            v = [r["optimism_ln"] for r in rs]
            summary[name] = {"n": len(v), "mean": float(np.mean(v)),
                             "spread": float(np.max(v) - np.min(v)) if len(v) > 1 else 0.0}
            print(f"  {name:18s} n={len(v)}  mean={np.mean(v):+.3f}  "
                  f"values={[f'{x:+.3f}' for x in v]}")
    out = {"version": 1, "cycle": "C4564-whisper", "rows": rows,
           "optimism_by_depth_class": summary,
           "headline": ("The noise model under-predicts the ideal->hardware haircut by a "
                        "depth-growing factor: ~1-9% shallow, ~11-24% mid, ~11-31% deep "
                        "(ln units); within-class spread is window-dominated (F81), so "
                        "corrections should be SENTINEL-ANCHORED, not global constants."),
           "growth_rule": "append one row per graded experiment, in the grade cycle."}
    path = os.path.join(RES, "model_residual_atlas.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, default=float)
    print(f"\nwrote {os.path.abspath(path)}")


if __name__ == "__main__":
    main()
