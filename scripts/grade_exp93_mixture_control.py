#!/usr/bin/env python3
"""
Grade Exp93 (Elder C6342): same-device switch-vs-mixture causal-separability witness
on ibm_marrakesh, job d93p3cnu62ks73953cvg (6 PUBs, single calibration window).

Reads <X_c> per PUB (control = classical bit 0), then per-mode
  DISC(mode) = <X_c>_commute - <X_c>_anticommute
and witnesses
  W1 = DISC_switch - DISC_definite
  W2 = DISC_switch - DISC_mixture   (HEADLINE — causal-separability loophole on silicon)

Pre-registered hardware gates (experiments/exp93-...-preregistration.md HARDWARE ARM):
  H_HW1  DISC_switch      >= +1.40   (witness survives noise)
  H_HW2  |DISC_mixture|   <= 0.20    (classical mixture inert on device)
  H_HW3  W2               >= +0.40   (HEADLINE — witness survives sharper adversary)
  H_HW4  |W1 - W2|        <= 0.25    (corroborating — both separable controls inert)
Verdict PASS = H_HW1 & H_HW2 & H_HW3 ; H_HW4 corroborating.
"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
from run_exp66_qpu_partb import _get_ibm_service

HERE = os.path.dirname(__file__)
MANIFEST = os.path.join(HERE, "..", "experiments", "exp93_jobids.json")


def counts_expval_x(counts):
    """<X_c> = P0 - P1 over the single measured control bit (ancilla marginalized)."""
    p0 = p1 = 0
    for bitstr, n in counts.items():
        b = bitstr.replace(" ", "")[-1]  # control is classical bit 0
        if b == '0':
            p0 += n
        else:
            p1 += n
    tot = p0 + p1
    return (p0 - p1) / tot, tot


def pub_counts(pubres):
    """Extract counts dict from a SamplerV2 PUB result (single creg)."""
    data = pubres.data
    for name in dir(data):
        if name.startswith('_'):
            continue
        try:
            obj = getattr(data, name)
        except Exception:
            continue
        if hasattr(obj, 'get_counts'):
            return obj.get_counts(), name
    raise RuntimeError("no BitArray with get_counts in PUB data")


def main():
    with open(MANIFEST) as f:
        man = json.load(f)
    jid = man["job_id"]
    order = man["pub_order"]   # switch/definite/mixture x commute/anticommute
    shots = man["shots"]

    svc = _get_ibm_service()
    job = svc.job(jid)
    st = job.status()
    print(f"Job {jid} status={st}", flush=True)
    if str(st) not in ("DONE", "JobStatus.DONE", "Completed"):
        print("Job not DONE yet — cannot grade. Re-run next cycle.")
        return 3

    res = job.result()
    xvals = {}
    for i, label in enumerate(order):
        counts, creg = pub_counts(res[i])
        xv, tot = counts_expval_x(counts)
        xvals[label] = xv
        print(f"  PUB[{i}] {label:22s} creg={creg} <X_c>={xv:+.4f}  (shots={tot})")

    disc_switch   = xvals["switch_commute"]   - xvals["switch_anticommute"]
    disc_definite = xvals["definite_commute"] - xvals["definite_anticommute"]
    disc_mixture  = xvals["mixture_commute"]  - xvals["mixture_anticommute"]
    W1 = disc_switch - disc_definite
    W2 = disc_switch - disc_mixture
    se_disc = math.sqrt(2.0) / math.sqrt(shots)   # ~0.018
    se_w    = 2.0 / math.sqrt(shots)              # ~0.026

    print("\n=== WITNESS (sim: DISC_switch=+2.000, DISC_mixture=+0.014, W1=+2.000, W2=+1.986) ===")
    print(f"  DISC_switch   = {disc_switch:+.4f}   (SE~{se_disc:.3f})")
    print(f"  DISC_definite = {disc_definite:+.4f}   (SE~{se_disc:.3f})")
    print(f"  DISC_mixture  = {disc_mixture:+.4f}   (SE~{se_disc:.3f})")
    print(f"  W1 = DISC_switch - DISC_definite = {W1:+.4f}   (SE~{se_w:.3f})")
    print(f"  W2 = DISC_switch - DISC_mixture  = {W2:+.4f}   (SE~{se_w:.3f}) [HEADLINE]")

    h1 = disc_switch >= 1.40
    h2 = abs(disc_mixture) <= 0.20
    h3 = W2 >= 0.40
    h4 = abs(W1 - W2) <= 0.25
    print("\n=== GRADE (pre-registered hardware gates) ===")
    print(f"  H_HW1 DISC_switch >= +1.40      : {'PASS' if h1 else 'FAIL'}  ({disc_switch:+.4f})")
    print(f"  H_HW2 |DISC_mixture| <= 0.20    : {'PASS' if h2 else 'FAIL'}  ({abs(disc_mixture):.4f})")
    print(f"  H_HW3 W2 >= +0.40 (HEADLINE)    : {'PASS' if h3 else 'FAIL'}  ({W2:+.4f})")
    print(f"  H_HW4 |W1-W2| <= 0.25 (corrob.) : {'PASS' if h4 else 'FAIL'}  ({abs(W1-W2):.4f})")

    if not h1:
        verdict = ("INCONCLUSIVE — H_HW1 failed: the switch witness itself did not survive device "
                   "noise on this triple → W2 uninterpretable.")
    elif not h2:
        verdict = ("WEAKENING — H_HW2 failed: the classical-mixture control is NOT inert on device "
                   "(incomplete dephasing / leak channel). Report as weakening, no laundering.")
    elif h3:
        verdict = ("PASS — on ibm_marrakesh in ONE calibration window, the coherent quantum switch is "
                   "distinguished from a classical mixture of definite orders (W2 >= +0.40). "
                   "Causal-SEPARABILITY loophole closed on silicon, same-device, drift-free."
                   + ("" if h4 else " NOTE: H_HW4 corroborating gate FAILED — investigate W1/W2 split."))
    else:
        verdict = ("NULL — switch resource collapsed toward the mixture on this substrate "
                   "(W2 below headline gate). Publishable boundary result.")
    print(f"\nVERDICT: {verdict}")

    sigma_w2 = W2 / se_w if se_w else float('nan')
    out = {
        "experiment": "exp93-classical-mixture-control-hardware-arm",
        "cycle_graded": "C6342", "job_id": jid, "backend": man["backend"], "shots": shots,
        "control_target_ancilla": man.get("triple_control_target_ancilla"),
        "xvals": xvals,
        "DISC_switch": disc_switch, "DISC_definite": disc_definite, "DISC_mixture": disc_mixture,
        "W1": W1, "W2": W2, "W2_sigma_above_0": sigma_w2,
        "SE_disc": se_disc, "SE_w": se_w,
        "H_HW1_pass": h1, "H_HW2_pass": h2, "H_HW3_pass": h3, "H_HW4_pass": h4,
        "verdict": verdict,
    }
    outp = os.path.join(HERE, "..", "results", "exp93_mixture_control_grade.json")
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    with open(outp, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved grade -> {os.path.abspath(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
