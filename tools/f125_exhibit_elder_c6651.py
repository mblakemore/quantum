#!/usr/bin/env python3
"""F125 EXHIBIT (Elder C6651, court seat) — H10-B1 "time flip": the three flights re-decoded from BANKED RAW COUNTS
through the flight module's own build_pubs / MASKP / MASKS / SHOTS and the decode() arithmetic (lines 282-322 of
experiments/h10_b1_flight_whisper_c5018.py, reproduced here as a pure function so that decode() — which fetches and
OVERWRITES results/h10_b1_decode_<job>.json — is never called), then diffed field by field against the banked decodes.

The ceilings the G1 bar and the "113-200σ" headline are measured against were co-checked at C6578
(results/h10_b1_ceiling_cocheck_full_elder_c6578.json, parallel 0.8827 / causal 0.9056 recomputed to 1e-8); this
exhibit covers the OTHER half — the flown accuracies and the gate verdicts, including the G4b apparatus-health band
whose failure in every flight is why the row reads DOES NOT HOLD.
"""
import json, os, sys, importlib.util, numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); RES = os.path.join(ROOT, "results")
sys.path.insert(0, os.path.join(ROOT, "experiments")); sys.path.insert(0, os.path.join(ROOT, "scripts"))
spec = importlib.util.spec_from_file_location("h10_b1_flight_whisper_c5018", os.path.join(ROOT, "experiments", "h10_b1_flight_whisper_c5018.py"))
m = importlib.util.module_from_spec(spec); sys.modules["h10_b1_flight_whisper_c5018"] = m; spec.loader.exec_module(m)
JOBS = [("marrakesh", "d9ngftc60llc73ca2vo0"), ("fez", "d9nn1boqs0bc73e3kkh0"), ("kingston", "d9nqg4ssfqic73arbrf0")]

def redecode(counts_pubs):
    pubs = m.build_pubs(); assert len(pubs) == len(counts_pubs), (len(pubs), len(counts_pubs))
    wins = {"F": [], "P": [], "S": []}; per_pair = {}
    for p, cp in zip(pubs, counts_pubs):
        cnt = cp["counts"]; n = sum(cnt.values())
        if p["arm"] == "F":
            w = cnt.get(p["win_outcome"], 0) / n
        else:
            MASK = m.MASKP if p["arm"] == "P" else m.MASKS
            w = 0.0
            for s, c in cnt.items():
                if MASK[int(s, 2)] == (p["label"] == "M+"): w += c / n
        wins[p["arm"]].append(w); per_pair[f"{p['arm']}_{p['name']}"] = w
    out = {"per_pair": per_pair}; N = m.SHOTS * 21
    for arm in ("F", "P", "S"):
        mu = float(np.mean(wins[arm])); out[arm] = {"win": mu, "se": float(np.sqrt(max(mu * (1 - mu), 1e-12) / N))}
    pF, seF = out["F"]["win"], out["F"]["se"]; pP, seP = out["P"]["win"], out["P"]["se"]; pS, seS = out["S"]["win"], out["S"]["se"]
    out["G1"] = {"pass": bool((pF - 0.919746) / seF >= 5), "sig": (pF - 0.919746) / seF}
    out["G2"] = {"pass": bool((pF - pP) / np.hypot(seF, seP) >= 5), "sig": float((pF - pP) / np.hypot(seF, seP))}
    out["G3"] = {"pass": bool((pP - pS) / np.hypot(seP, seS) >= 5), "sig": float((pP - pS) / np.hypot(seP, seS))}
    out["G4a"] = {"pass": bool(0.78 <= pP <= 0.89), "value": pP}
    out["G4b"] = {"pass": bool(0.69 <= pS <= 0.75), "value": pS}
    edge = 0.665897 + 3 * seS
    out["A5_2_zone"] = {"evaluated_fault_edge": float(edge), "reading": pS,
                        "zone": ("FAULT" if pS <= edge else "ATTENUATION-CONSISTENT" if pS < 0.69 else "PASS-BAND" if pS <= 0.75 else "WRONG-STRATEGY"),
                        "sigma_from_edge": float((pS - edge) / seS)}
    out["VERDICT"] = "HOLDS" if all(out[g]["pass"] for g in ("G1", "G2", "G3", "G4a", "G4b")) else "DOES NOT HOLD"
    return out

def flatten(o, path=""):
    if isinstance(o, dict):
        for k, v in o.items(): yield from flatten(v, f"{path}/{k}")
    else: yield path, o

def main():
    report = {"cycle": "C6651", "grader": "elder", "scope": "F125 exhibit — three H10-B1 flights re-decoded from banked raw counts", "flights": {}}
    for backend, job in JOBS:
        bank = json.load(open(os.path.join(RES, f"h10_b1_counts_{job}_elder_c6651.json")))
        banked = json.load(open(os.path.join(RES, f"h10_b1_decode_{job}.json")))
        out = redecode(bank["pubs"])
        mine = dict(flatten(out)); theirs = dict(flatten(banked))
        keys = [k for k in theirs if k in mine]
        mism = [(k, mine[k], theirs[k]) for k in keys if not (mine[k] == theirs[k] or (isinstance(mine[k], float) and isinstance(theirs[k], (int, float)) and abs(mine[k] - theirs[k]) <= 1e-9))]
        report["flights"][backend] = {"job": job, "n_pubs": len(bank["pubs"]), "total_shots": bank["total_shots"],
                                      "fields_compared": len(keys), "fields_matched": len(keys) - len(mism), "mismatches": [{"field": k, "recomputed": a, "banked": b} for k, a, b in mism][:20],
                                      "F_win": out["F"]["win"], "G1_sigma_over_ceiling_0.919746": out["G1"]["sig"], "G4b": out["G4b"], "zone": out["A5_2_zone"]["zone"], "verdict": out["VERDICT"], "verdict_banked": banked.get("VERDICT")}
        print(f"{backend:9s} {job}: {len(keys)-len(mism)}/{len(keys)} fields match; F {out['F']['win']:.4f} (G1 {out['G1']['sig']:.1f}σ over 0.919746); P {out['P']['win']:.4f}; S {out['S']['win']:.4f} G4b {'PASS' if out['G4b']['pass'] else 'FAIL'} zone {out['A5_2_zone']['zone']}; verdict {out['VERDICT']} (banked {banked.get('VERDICT')}); mismatches {len(mism)}")
    path = os.path.join(RES, "f125_exhibit_elder_c6651.json"); json.dump(report, open(path, "w"), indent=1, default=float); print("->", path)

if __name__ == "__main__":
    main()
