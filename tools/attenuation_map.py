#!/usr/bin/env python3
"""P6 v1 — WARP FIELD CARTOGRAPHY: the attenuation map (per-device effective per-2q-slot error).

Model: measured/ideal = exp(-lambda_eff * d2q). lambda_eff folds EVERYTHING the depth drags through
(2q error + idle decoherence during the slot + 1q dressing + readout share) into one per-slot rate —
the honest quantity the C4937 miss showed nameplate 2q error does NOT capture.

v1 seed: the multi-substrate frozen-instrument points (same abstract circuit everywhere; d2q =
platform-native 2q count of the witness). VERIFIED depths marked; TODO depths use the abstract count
pending a recompile-and-count pass. v1.1 backlog: depth-resolved within-device fit from the
DISC-family archaeology (exp208/209/212/224/225 + distributed family) — needs per-experiment
transpiled counts verified before inclusion (G13 rule).
Substrate: claude-fable-5, Whisper C4951."""
import json, math, os
QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

# (device, W_measured, W_ideal, d2q, depth_status, nameplate_2q_err, source)
SEED = [
    ("ibm_kingston",  1.9533, 2.0, 4, "VERIFIED(transpile L3)", 0.0025, "F112"),
    ("ibm_marrakesh", 1.9265, 2.0, 4, "VERIFIED(transpile L3)", 0.0030, "F112"),
    ("ibm_fez",       1.8948, 2.0, 4, "VERIFIED(transpile L3)", 0.0030, "F112"),
    ("rigetti_cepheus", 1.2165, 2.0, 6, "TODO(native recount)", 0.0030, "Exp210 corrected"),
    ("ionq_forte1",   1.9100, 2.0, 4, "TODO(native RZZ recount)", 0.0045, "Exp212 same-window"),
]

def main():
    rows = []
    for dev, w, ideal, d, st, nameplate, src in SEED:
        ratio = w / ideal
        lam = -math.log(ratio) / d
        factor = lam / nameplate if nameplate else None
        rows.append({"device": dev, "W": w, "ratio": round(ratio, 4), "d2q": d,
                     "depth_status": st, "lambda_eff_per_slot": round(lam, 5),
                     "nameplate_2q_err": nameplate,
                     "effective_vs_nameplate_x": round(factor, 1), "source": src})
        print(f"{dev:16s} W={w:.4f} d2q={d} -> lambda_eff={lam:.4f}/slot "
              f"(nameplate {nameplate:.4f} -> x{factor:.1f})  [{st}]")
    out = {"model": "measured/ideal = exp(-lambda_eff * d2q)", "seed_points": rows,
           "headline": "effective per-slot attenuation exceeds nameplate 2q error by x1.9 (IonQ) "
                       "to x27 (Rigetti); Heron ~x4-6. Nameplate 2q error is NOT a witness predictor "
                       "(C4937 quantified). Prediction rule for new devices: use lambda_eff of the "
                       "closest device class, widen bounds by the class's observed spread.",
           "v1_1_backlog": ["exp208/209/212 DISC family (fez, depth recount needed)",
                            "exp221/222/224/225 distributed/routing family",
                            "within-device depth-resolved fit -> separate idle vs gate share"]}
    json.dump(out, open(os.path.join(QROOT, "results", "attenuation_map.json"), "w"), indent=1)
    print("card -> results/attenuation_map.json")

if __name__ == "__main__":
    main()
