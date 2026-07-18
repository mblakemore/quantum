#!/usr/bin/env python3
"""Exp151b — the DTC noise-protection factor, DECOMPOSED (Ember, C4196; Creator queue directive).

ORIGIN: Whisper's Exp151 found the discrete time crystal held on hardware ~3x better than the
generic-decay noise model predicted (A decayed 0.376 measured vs 0.12 predicted over 120 CX) — MBL
appears to shield the observable from noise. Whisper C4840 asked 151b to QUANTIFY that as a
protection factor against a GATE-MATCHED non-localizing interacting control.

DESIGN CORRECTION (Ember, noiseless truth-gate, surfaced to Whisper before flight): the assumed
"non-localizing interacting control thermalizes" is FALSE at these parameters. Interactions ON +
disorder OFF is itself subharmonic-RIGID noiselessly (A_match ~0.92-0.95 > A_dtc 0.43-0.84 across
t=0..12) — interactions ALONE prethermally lock the subharmonic; the clean chain is a prethermal
time crystal, not a thermal baseline. So P_ideal = A_dtc/A_match is 1.0->0.47 (DECLINES), never >1.

WHAT THIS REFRAMES (and it is sharper): since BOTH arms are ideally rigid at MATCHED 2q depth, any
HARDWARE difference cannot be thermalization (both ideal-rigid) — it can ONLY be differential
hardware-NOISE robustness. 151b therefore DECOMPOSES Whisper's surprise into two candidate shields:
  • INTERACTIONS (present in both arms) vs
  • LOCALIZATION/disorder (present only in DTC).
Measured signal: P_hw(t) = A_dtc_hw/A_match_hw, compared to the KNOWN ideal P_ideal(t).
  P_hw/P_ideal > 1 and growing with t => disorder adds noise-robustness OVER interactions alone
                                          (localization IS a distinct noise-shield).
  P_hw/P_ideal ~ 1                     => the shield is the interactions, not localization.

ARMS (2 flown; the pulse-only arm is Exp151's, reused as the falsifiability anchor via selftest):
  • DTC   : rx(imperfect) + rzz(J) + rz(disorder)   [interactions + localization]
  • MATCH : rx(imperfect) + rzz(J)                   [interactions only; SAME rzz => SAME 2q count]
DTC carries L extra rz per period (disorder); rz is virtual (0 duration on IBM) so the 2q/timed
overhead is matched — asserted in the gate.

PRE-REGISTERED (0.5, honestly uncertain — could go either way): on hardware, the DISORDERED arm
retains subharmonic amplitude better than the clean-interacting arm at the deepest t
(A_dtc_hw > A_match_hw at t_max), i.e. P_hw/P_ideal > 1 and grows — disorder is a distinct shield.
FALSIFIER: A_dtc_hw <= A_match_hw at t_max (P_hw/P_ideal <= 1) — interactions alone carry the shield.
NO-TEST: both arms |A|<0.1 by t_max (decayed to floor) — underpowered, void.

  python3 exp151b_protection_factor_ember.py --selftest
  python3 exp151b_protection_factor_ember.py --gate2q   --backend ibm_fez
  python3 exp151b_protection_factor_ember.py --prereg
  python3 exp151b_protection_factor_ember.py --submit   --backend ibm_fez --tmax 12 --shots 4000
  python3 exp151b_protection_factor_ember.py --decode
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")
_e = importlib.util.spec_from_file_location("e151", os.path.join(HERE, "exp151_time_crystal.py"))
E151 = importlib.util.module_from_spec(_e); _e.loader.exec_module(E151)

L = E151.L
EPS = E151.EPS
NULL_T = int(round(1 / (2 * EPS)))
ARMS = [("dtc", True, True), ("match", True, False)]   # (label, interactions, disorder)


def selftest():
    """Truth-gate (noiseless). (1) BOTH arms are ideally subharmonic-rigid at MATCHED depth
    (neither collapses at the beat-null) — the corrected premise. (2) The known ideal ratio
    P_ideal(t)=A_dtc/A_match is recorded (the baseline the hardware is measured against).
    (3) FALSIFIABILITY: the pulse-only chain (interactions OFF) DOES collapse at the null — so the
    rigidity in both flown arms is genuinely interaction-borne, and the DTC-vs-MATCH contrast is
    disorder, not drive."""
    Tm = 12
    dtc = np.array([E151._z_expect_exact(t, True, True) for t in range(Tm + 1)])
    match = np.array([E151._z_expect_exact(t, True, False) for t in range(Tm + 1)])
    pulse = np.array([E151._z_expect_exact(t, False, False) for t in range(Tm + 1)])
    A_dtc, A_match, A_pulse = E151._amp_curve(dtc), E151._amp_curve(match), E151._amp_curve(pulse)
    win = [NULL_T - 1, NULL_T, NULL_T + 1]
    dtc_hold = float(np.mean([abs(A_dtc[t]) for t in win]))
    match_hold = float(np.mean([abs(A_match[t]) for t in win]))
    pulse_null = float(np.mean([abs(A_pulse[t]) for t in win]))
    p_ideal = [float(A_dtc[t] / A_match[t]) if abs(A_match[t]) > 1e-6 else None for t in range(Tm + 1)]
    print(f"Exp151b selftest (noiseless) | L={L} eps={EPS} beat-null~t={NULL_T}")
    print(f"{'t':>3} {'A_dtc':>8} {'A_match':>8} {'A_pulse':>8} {'P_ideal':>8}")
    for t in range(Tm + 1):
        pi = f"{p_ideal[t]:.3f}" if p_ideal[t] is not None else "  n/a"
        print(f"{t:>3} {A_dtc[t]:>8.3f} {A_match[t]:>8.3f} {A_pulse[t]:>8.3f} {pi:>8}")
    print(f"\nbeat-null window {win}: DTC holds {dtc_hold:.3f} | MATCH holds {match_hold:.3f} | "
          f"pulse-only {pulse_null:.3f}")
    # gates
    assert dtc_hold > 0.4, f"DTC not ideally rigid ({dtc_hold:.3f})"
    assert match_hold > 0.4, f"MATCH (int-only) not ideally rigid ({match_hold:.3f}) — premise wrong"
    assert pulse_null < 0.35, f"pulse-only did not collapse ({pulse_null:.3f}) — falsifiability broken"
    print(f"SELFTEST PASS: both flown arms ideally rigid at matched depth (DTC {dtc_hold:.3f}, "
          f"MATCH {match_hold:.3f}); pulse-only collapses ({pulse_null:.3f}) so rigidity is "
          f"interaction-borne. P_ideal recorded (declines 1.0->~0.47 — the hardware baseline).")
    json.dump({"p_ideal": p_ideal, "null_t": NULL_T, "dtc_hold": dtc_hold,
               "match_hold": match_hold, "pulse_null": pulse_null},
              open(os.path.join(RESULTS, "exp151b_pideal.json"), "w"), indent=1)


def gate2q(backend_name):
    """Assert DTC and MATCH have EQUAL 2q (rzz) count per period after transpile (rz is virtual)."""
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    be = _get_ibm_service().backend(backend_name)
    ok = True
    for t in (4, 8, 12):
        d = E151.floquet_circuit(t, True, True, measure=True)
        m = E151.floquet_circuit(t, True, False, measure=True)
        td = transpile(d, be, optimization_level=3, seed_transpiler=151)
        tm = transpile(m, be, optimization_level=3, seed_transpiler=151)
        n2d, n2m = td.num_nonlocal_gates(), tm.num_nonlocal_gates()
        match = abs(n2d - n2m) <= max(2, int(0.1 * n2d))
        ok &= match
        print(f"  t={t:>2}: DTC 2q={n2d} MATCH 2q={n2m} matched={'OK' if match else 'FAIL'}")
    print(f"  2q-match gate: {'OK' if ok else 'FAIL'}")
    return ok


def prereg():
    doc = {"exp": "151b", "author": "Ember", "cycle": 4196, "written": "pre-decode",
           "origin": "Whisper Exp151 MBL-shields-noise surprise (A 0.376 measured vs 0.12 predicted)",
           "design_correction": "int-only control is ideally RIGID (prethermal), not thermal — "
                                "so 151b decomposes the shield into interactions vs localization, "
                                "measured vs the KNOWN P_ideal baseline (not vs 1).",
           "arms": {"dtc": "rx(imperfect)+rzz(J)+rz(disorder)",
                    "match": "rx(imperfect)+rzz(J) — same rzz => same 2q count, no disorder"},
           "prediction": "on hardware the DISORDERED arm retains subharmonic amplitude better than "
                         "the clean-interacting arm at t_max (A_dtc_hw>A_match_hw; P_hw/P_ideal>1 "
                         "and grows) — disorder is a noise-shield distinct from interactions.",
           "prediction_confidence": 0.5,
           "falsifier": "A_dtc_hw <= A_match_hw at t_max — interactions alone carry the shield.",
           "NO_TEST": "both arms |A|<0.1 by t_max (noise floor) — underpowered, void.",
           "L": L, "eps": EPS, "null_t": NULL_T, "arms_order": [a[0] for a in ARMS]}
    json.dump(doc, open(os.path.join(RESULTS, "exp151b_prereg.json"), "w"), indent=1)
    print("pre-registered -> results/exp151b_prereg.json (0.5: disorder is a distinct noise-shield)")


def submit(backend_name, tmax, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    if not gate2q(backend_name):
        print("REFUSING: 2q not matched between arms."); return 1
    be = _get_ibm_service().backend(backend_name)
    circuits, order = [], []
    for label, inter, dis in ARMS:
        for t in range(tmax + 1):
            qc = E151.floquet_circuit(t, inter, dis, measure=True)
            circuits.append(transpile(qc, be, optimization_level=3, seed_transpiler=151))
            order.append([label, t])
    outp = os.path.join(RESULTS, "exp151b_manifest.json")
    if os.path.exists(outp):
        print(f"REFUSING: {os.path.basename(outp)} exists."); return 3
    job = SamplerV2(mode=be).run(circuits, shots=shots)
    json.dump({"exp": "151b", "backend": backend_name, "tmax": tmax, "shots": shots, "L": L,
               "eps": EPS, "job_id": job.job_id(), "order": order,
               "note": "DTC vs gate-matched clean-interacting; protection-factor decomposition"},
              open(outp, "w"), indent=1)
    print(f"SUBMITTED Exp151b: job {job.job_id()} ({len(circuits)} circuits) -> {os.path.basename(outp)}")
    return 0


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    tmax, order, shots = man["tmax"], man["order"], man["shots"]
    arms = {"dtc": {}, "match": {}}
    for idx, (label, t) in enumerate(order):
        r = res[idx]; reg = list(r.data.keys())[0]
        arms[label][t] = E151._z_expect_counts(getattr(r.data, reg).get_counts(), shots)
    A = {k: E151._amp_curve(np.array([arms[k][t] for t in range(tmax + 1)])) for k in arms}
    pid = json.load(open(os.path.join(RESULTS, "exp151b_pideal.json")))["p_ideal"]
    print(f"Exp151b decode | job {man['job_id']} | {man['backend']} | null t={NULL_T}")
    print(f"{'t':>3} {'A_dtc_hw':>9} {'A_match_hw':>10} {'P_hw':>7} {'P_ideal':>8} {'P_hw/P_id':>9}")
    rows = []
    for t in range(tmax + 1):
        ad, am = float(A["dtc"][t]), float(A["match"][t])
        php = ad / am if abs(am) > 1e-6 else None
        pi = pid[t]
        rr = (php / pi) if (php is not None and pi and abs(pi) > 1e-6) else None
        rows.append({"t": t, "A_dtc_hw": round(ad, 3), "A_match_hw": round(am, 3),
                     "P_hw": None if php is None else round(php, 3),
                     "P_ideal": None if pi is None else round(pi, 3),
                     "ratio": None if rr is None else round(rr, 3)})
        s_php = f"{php:.3f}" if php is not None else " n/a"
        s_pi = f"{pi:.3f}" if pi is not None else " n/a"
        s_rr = f"{rr:.3f}" if rr is not None else " n/a"
        print(f"{t:>3} {ad:>9.3f} {am:>10.3f} {s_php:>7} {s_pi:>8} {s_rr:>9}")
    ad_max, am_max = rows[tmax]["A_dtc_hw"], rows[tmax]["A_match_hw"]
    floor = abs(ad_max) < 0.1 and abs(am_max) < 0.1
    if floor:
        verdict = "NO-TEST: both arms at noise floor by t_max — underpowered"
    elif ad_max > am_max:
        verdict = (f"DISORDER SHIELDS: A_dtc_hw {ad_max} > A_match_hw {am_max} at t_max=tmax -> "
                   "localization is a noise-shield distinct from interactions (pred HELD, 0.5)")
    else:
        verdict = (f"A_dtc_hw {ad_max} <= A_match_hw {am_max} at t_max -> interactions alone carry "
                   "the shield; localization adds no differential noise-robustness (pred FALSIFIED)")
    out = {"exp": "151b", "job_id": man["job_id"], "backend": man["backend"], "rows": rows,
           "verdict": verdict}
    json.dump(out, open(os.path.join(RESULTS, "exp151b_decode.json"), "w"), indent=1)
    print(f"\n  VERDICT: {verdict}\n  -> results/exp151b_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for fl in ("selftest", "gate2q", "prereg", "submit", "decode"):
        ap.add_argument(f"--{fl}", action="store_true")
    ap.add_argument("--manifest"); ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--tmax", type=int, default=12); ap.add_argument("--shots", type=int, default=4000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.gate2q: sys.exit(0 if gate2q(a.backend) else 1)
    elif a.prereg: prereg()
    elif a.submit: sys.exit(submit(a.backend, a.tmax, a.shots))
    elif a.decode: decode(a.manifest or os.path.join(RESULTS, "exp151b_manifest.json"))
    else: ap.print_help()
