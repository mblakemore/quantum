#!/usr/bin/env python3
"""Exp207 — DOES THE LOGICAL COMPUTER TRAVEL: cross-device portability of Exp206. C4904.

Horizons-4 U8 (the "are our laws generation-general?" exam), ADAPTED. The literal
cross-GENERATION exam is hardware-blocked: no Eagle-family device is on the open plan (only
Heron-r2 fez/marrakesh/kingston; logged logs/boundaries.md C4904). This is the strongest
AVAILABLE version — a cross-DEVICE (Heron->Heron) replication of the campaign's first
error-corrected computation (Exp206, certified on ibm_fez at 19.7 sigma) on a chip the
circuit has never seen: ibm_marrakesh. Same frozen circuits, same frozen decode, same gates.

Reuses Exp206 verbatim (imported) — the ONLY changes are the target backend and a
cross-device concordance gate. If a network member gains Eagle access, this exact bench is
the cross-generation flight with no edits.

FROZEN GATES (206's W1-W4 + G_acc, re-applied on the new device, PLUS):
  X1_CONCORDANCE: sign of the shield-beats-bare margin reproduces (logical-post > bare) AND
     |P_valid_logical(marrakesh) - 0.974(fez)| <= 0.10 AND |P_valid_bare(marrakesh) -
     0.897(fez)| <= 0.10 (the law travels within a device-drift band).
Registered verdict = W1-W4 and G_acc and X1_CONCORDANCE.
SCOPE: cross-device within one generation (Heron-r2), NOT cross-generation. The claim is
device-independence of the logical-beats-bare result, extending F112's bench-portability to
a Horizons-4 computational result. Textbook + F113 fence unchanged.
Usage: --submit [--backend ibm_marrakesh] | --decode
"""
import argparse, json, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp206_logical_computer import (bare_circuit, logical_circuit, find_decode,
                                     analyze_bare, analyze_logical, bare_valid_set)

FEZ_BARE = 0.8968     # Exp206 measured anchors (frozen reference for concordance)
FEZ_LOG = 0.9741


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import transpile
    dec, mask, vset = find_decode()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    builds = [("bare", bare_circuit()), ("logical", logical_circuit())]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0)
                for _, qc in builds]
    n2 = {name: sum(1 for inst in c.data if inst.operation.num_qubits == 2)
          for (name, _), c in zip(builds, circuits)}
    print(f"  {backend_name} 2q counts: {n2}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp207_crossdevice_manifest.json")
    man = {"exp": 207, "slug": "logical_computer_crossdevice", "backend": backend_name,
           "shots": shots, "job_id": job.job_id(), "order": ["bare", "logical"],
           "decode": {"dec": dec, "mask": list(mask)},
           "valid_set": sorted(list(z) for z in vset), "n2": n2,
           "fez_reference": {"bare": FEZ_BARE, "logical": FEZ_LOG},
           "prereg": {
               "W1_W4_Gacc": "Exp206 gates re-applied on the new device (frozen)",
               "X1_concordance": "sign(margin) reproduces (logical>bare) AND "
                                 "|P_log-0.974|<=0.10 AND |P_bare-0.897|<=0.10",
               "scope": "cross-DEVICE Heron-r2 (Eagle unavailable, boundaries.md C4904); "
                        "device-independence of logical-beats-bare, extends F112",
               "budget": "expect marrakesh within +-0.08 of fez both arms; margin sign "
                         "reproduces at >=3 sigma"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} (2 circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp207_crossdevice_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    dec = tuple(tuple(x) for x in man["decode"]["dec"]); mask = tuple(man["decode"]["mask"])
    vset = {tuple(z) for z in man["valid_set"]}
    rb = analyze_bare(raw["bare"]); rl = analyze_logical(raw["logical"], dec, mask)
    floor = len(vset) / 16
    seb = np.sqrt(rb["P_valid"] * (1 - rb["P_valid"]) / rb["n"])
    sel = np.sqrt(rl["P_valid_post"] * (1 - rl["P_valid_post"]) / max(rl["n_acc"], 1))
    zb = (rb["P_valid"] - floor) / seb; zl = (rl["P_valid_post"] - floor) / sel
    margin = rl["P_valid_post"] - rb["P_valid"]; se_m = np.sqrt(seb ** 2 + sel ** 2)
    zm = margin / se_m
    print(f"Exp207 CROSS-DEVICE ({man['backend']}) decode | job {man['job_id']} | "
          f"fez ref bare {FEZ_BARE:.3f} / logical {FEZ_LOG:.3f}")
    print(f"  bare:    P(valid) = {rb['P_valid']:.4f} ({zb:.0f} sigma over floor)")
    print(f"  logical: P(valid|acc) = {rl['P_valid_post']:.4f} ({zl:.0f} sigma), "
          f"acceptance = {rl['acceptance']:.4f}")
    print(f"  shield-beats-bare margin = {margin:+.4f} ({zm:.1f} sigma)")
    w1 = rb["P_valid"] > 0.55 and zb >= 5 and rl["P_valid_post"] > 0.55 and zl >= 5
    cov = all(rb["z_counts"].get(str(z), 0) >= 0.5 / len(vset)
              and rl["z_counts"].get(str(z), 0) >= 0.5 / len(vset) for z in vset)
    w3 = len(vset) < 16
    w4 = margin > 0 and zm >= 3
    gacc = rl["acceptance"] >= 0.55
    conc = (margin > 0 and abs(rl["P_valid_post"] - FEZ_LOG) <= 0.10
            and abs(rb["P_valid"] - FEZ_BARE) <= 0.10)
    print(f"\nW1 SOLVER {'OK' if w1 else 'MISS'} | W2 COVERAGE {'OK' if cov else 'MISS'} | "
          f"W3 NONTRIVIAL {'OK' if w3 else 'MISS'} | W4 SHIELD-BEATS-BARE {'OK' if w4 else 'MISS'} "
          f"| G_ACC {'OK' if gacc else 'MISS'}")
    print(f"X1 CONCORDANCE: margin sign {'+' if margin > 0 else '-'}; "
          f"|dP_log|={abs(rl['P_valid_post']-FEZ_LOG):.3f} |dP_bare|={abs(rb['P_valid']-FEZ_BARE):.3f} "
          f"(<=0.10) {'OK' if conc else 'MISS'}")
    ok = w1 and cov and w3 and w4 and gacc and conc
    win = ("THE LOGICAL COMPUTER TRAVELS — logical-beats-bare reproduces on a second Heron "
           "chip within device drift: the result is device-independent (within-generation), "
           "not fez-specific")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    print("  (scope: cross-DEVICE Heron-r2; cross-GENERATION Eagle remains hardware-blocked, "
          "boundaries.md C4904)")
    json.dump({"job_id": man["job_id"], "backend": man["backend"], "bare": rb, "logical": rl,
               "margin": float(margin), "sigma_margin": float(zm),
               "fez_bare": FEZ_BARE, "fez_logical": FEZ_LOG,
               "d_logical": float(abs(rl["P_valid_post"] - FEZ_LOG)),
               "d_bare": float(abs(rb["P_valid"] - FEZ_BARE)),
               "w1": bool(w1), "w2_coverage": bool(cov), "w3": bool(w3), "w4": bool(w4),
               "g_acc": bool(gacc), "concordance": bool(conc), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp207_crossdevice_decode.json"), "w"), indent=1)
    print("-> results/exp207_crossdevice_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--submit", action="store_true"); ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_marrakesh"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
