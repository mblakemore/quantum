#!/usr/bin/env python3
"""
Grade Exp91 (Elder C6316): quantum-switch causal witness on ibm_marrakesh.
Retrieves job d939bmooamcc73dbv9b0 (4 PUBs), computes <X_c> per PUB,
then DISC_switch, DISC_definite, W vs pre-registered H1/H2/H3.

H1: DISC_switch_hw >= +0.5
H2: |DISC_definite_hw| <= 0.07
H3: W_hw = DISC_switch - DISC_definite > 0.07   (headline causal gate)
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from run_exp66_qpu_partb import _get_ibm_service

HERE = os.path.dirname(__file__)
MANIFEST = os.path.join(HERE, "..", "experiments", "exp91_jobids.json")


def counts_expval_x(counts, shots):
    """<X_c> = P0 - P1 over the single measured control bit."""
    p0 = p1 = 0
    for bitstr, n in counts.items():
        # single classical bit; take last char to be robust to spacing
        b = bitstr.replace(" ", "")[-1]
        if b == '0':
            p0 += n
        else:
            p1 += n
    tot = p0 + p1
    return (p0 - p1) / tot, tot


def pub_counts(pubres):
    """Extract counts dict from a SamplerV2 PUB result (single creg)."""
    data = pubres.data
    # find the one classical register bin
    for name in data.__dict__ if hasattr(data, '__dict__') else []:
        pass
    # robust: iterate the DataBin fields
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
    order = man["pub_order"]  # [switch_commute, definite_commute, switch_anticommute, definite_anticommute]
    shots = man["shots"]

    svc = _get_ibm_service()
    job = svc.job(jid)
    st = job.status()
    print(f"Job {jid} status={st}", flush=True)
    if str(st) not in ("DONE", "JobStatus.DONE"):
        print("Job not DONE yet — cannot grade. Re-run next cycle.")
        return 3

    res = job.result()
    xvals = {}
    for i, label in enumerate(order):
        counts, creg = pub_counts(res[i])
        xv, tot = counts_expval_x(counts, shots)
        xvals[label] = xv
        print(f"  PUB[{i}] {label:22s} creg={creg} <X_c>={xv:+.4f}  (shots={tot})")

    disc_switch = xvals["switch_commute"] - xvals["switch_anticommute"]
    disc_definite = xvals["definite_commute"] - xvals["definite_anticommute"]
    W = disc_switch - disc_definite

    print("\n=== WITNESS ===")
    print(f"  DISC_switch   = {disc_switch:+.4f}   (sim +2.000 / FakeMarrakesh +1.933)")
    print(f"  DISC_definite = {disc_definite:+.4f}   (sim  0.000 / FakeMarrakesh -0.0015)")
    print(f"  W             = {W:+.4f}   (sim +2.000 / FakeMarrakesh +1.934)")

    h1 = disc_switch >= 0.5
    h2 = abs(disc_definite) <= 0.07
    h3 = W > 0.07
    print("\n=== GRADE (pre-registered) ===")
    print(f"  H1 DISC_switch >= +0.5 : {'PASS' if h1 else 'FAIL'}  ({disc_switch:+.4f})")
    print(f"  H2 |DISC_definite| <= 0.07 : {'PASS' if h2 else 'FAIL'}  ({abs(disc_definite):.4f})")
    print(f"  H3 W > 0.07 (causal gate) : {'PASS' if h3 else 'FAIL'}  ({W:+.4f})")

    if not h2:
        verdict = "INCONCLUSIVE — H2 confound (definite-order control leaked discrimination); comparison voided"
    elif h1 and h3:
        verdict = "PASS — causal witness fires: switch discriminates commutation, definite-order cannot"
    else:
        verdict = "NULL — switch resource collapsed toward definite on this substrate (publishable boundary result)"
    print(f"\nVERDICT: {verdict}")

    out = {
        "experiment": "exp91-quantum-switch-causal-witness",
        "cycle_graded": "C6316", "job_id": jid, "backend": man["backend"],
        "xvals": xvals,
        "DISC_switch": disc_switch, "DISC_definite": disc_definite, "W": W,
        "H1_pass": h1, "H2_pass": h2, "H3_pass": h3, "verdict": verdict,
    }
    outp = os.path.join(HERE, "..", "results", "exp91_switch_witness_grade.json")
    with open(outp, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\nSaved grade -> {os.path.abspath(outp)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
