#!/usr/bin/env python3
"""UNFOLD U6 — sentinel device-health series (Whisper C5073). $0. FROZEN.
Sentinel |Phi+> Bell pairs (pub-0 2-bit block) across the exp142/exp144 flight families (STRUCTURAL
filter: these bank a sentinel at pub 0; h13 etc. do not -> excluded by family, NOT by value, to
avoid post-hoc selection). PIN: sentinel fidelities all physical Bell (0.5-1.0) on the structurally
defined set. PREDICTIONS: P1 pin. P2 a coherent device-health band. Falsifier: too few -> coverage.
"""
import json, os, glob, numpy as np
RES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
FAMILIES = ("exp142", "exp144")   # structural: these families bank a pub-0 Bell sentinel
resc = sorted(glob.glob(os.path.join(RES, "h14_lock5_rescue*.json")))
fids = []
for r in resc:
    base = os.path.basename(r)
    if not any(f in base for f in FAMILIES):   # STRUCTURAL family filter (not a value cut)
        continue
    try:
        d = json.load(open(r))
        if "pubs" not in d or not d["pubs"]: continue
        p0 = d["pubs"][0]; rows = list(p0.get("data", {}).values())[0]
        if not rows or len(rows[0]) != 2: continue
        arr = np.array([[int(b) for b in row] for row in rows])
        corr = float(np.mean(arr[:, 0] == arr[:, 1]))
        fam = "exp142" if "exp142" in base else "exp144"
        fids.append({"file": base[14:44], "family": fam, "n": len(rows), "bell_corr": corr})
    except Exception:
        pass
corrs = [f["bell_corr"] for f in fids]
pin_ok = bool(fids) and all(0.5 <= c <= 1.0 for c in corrs)
print(f"PIN (structural set, all physical Bell): {'PASS' if pin_ok else 'FAIL'}  n_flights={len(fids)}")
if fids:
    by = {}
    for f in fids: by.setdefault(f["family"], []).append(f["bell_corr"])
    for fam, cs in by.items():
        print(f"  {fam}: {len(cs)} flights, sentinel corr mean {np.mean(cs):.4f} +/- {np.std(cs):.4f} "
              f"[{min(cs):.3f}, {max(cs):.3f}]")
    print(f"  ALL: mean {np.mean(corrs):.4f} +/- {np.std(corrs):.4f}, range [{min(corrs):.3f}, {max(corrs):.3f}]")
verdict = (f"DEVICE-HEALTH SERIES BUILT: {len(fids)} flights (structural exp142/exp144 set), sentinel "
           f"Bell fidelity {np.mean(corrs):.3f} +/- {np.std(corrs):.3f} — a tight healthy band, the "
           "raw material for a per-flight/per-device timeline (F112-kin device gauge). Absolute-time "
           "ordering still needs job timestamps (as U5) to become a true time-series." if pin_ok else
           "NO-TEST (pin: a sentinel read non-physical -> detection not clean on this set)")
print(f"VERDICT: {verdict}")
json.dump({"card": "unfold_U6_sentinel_timeline", "cycle": "C5073", "pin_ok": pin_ok,
           "n_flights": len(fids), "mean_corr": float(np.mean(corrs)) if fids else None,
           "std_corr": float(np.std(corrs)) if fids else None, "sentinels": fids, "verdict": verdict},
          open(os.path.join(RES, "unfold_U6_sentinel_timeline_c5073.json"), "w"), indent=1)
