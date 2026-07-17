#!/usr/bin/env python3
"""Exp144 A1(0b) — the REFERENCE ARM I should have flown, as a CX SWEEP (Ember).

A1(0) killed idle-dominance (ARM-CX 0.527 vs my pre-stated falsifier 0.25) but could not
ATTRIBUTE, because I omitted the zero: ARM-IDLE (6.3us, 12 CX) = 0.540 and ARM-CX (0.82us,
54 CX) = 0.527 differ by 0.013 despite 8x less duration and 4.5x more CX. Both arms sit at
~0.53 regardless of either channel — the signature of a saturated common floor I had no
arm to measure.

A single reference arm would give the floor. A SWEEP gives the floor AND the per-CX cost,
for the same money:

    ARM-REF   : Bell prep -> immediate measure        (0 extra CX)  -> the FLOOR
    ARM-CX12  : + 12 extra CX (2/pair)
    ARM-CX24  : + 24 extra CX (4/pair)
    ARM-CX42  : + 42 extra CX (matches A1(0)'s ARM-CX, and its 0.527 is the anchor)

All identity-equivalent (even count per pair). All ~sub-us, so idle is negligible in ALL
of them and cannot confound the slope. Fit P(all-6-survive) vs extra-CX:
  intercept -> the floor (prep + un-prep + readout)
  slope     -> per-CX label error, MEASURED, in-context

That number is the one nobody has: kingston's published 2q calibration says 0.1-0.2%;
Whisper back-solves ~10x low from A1(0). This measures it directly instead of back-solving.

Predictions BEFORE flight (pre-stated, mine):
  * If the floor dominates: REF is already ~0.4-0.5 and the sweep is FLAT.
    -> then A1(0) measured almost nothing and BOTH mechanisms remain open.
  * If CX dominates: REF is low (<0.2) and off-group climbs steeply with CX count;
    per-CX error back-solves to ~1-2% (10x the published 0.1-0.2%).
  * I expect the second. But I expected idle too, so the sweep decides, not me.

  python3 exp144_a1b_cxsweep_ember.py --dry-run | --fly
"""
import argparse
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")

SHOTS = 4096
# extra CX per pair -> total across 6 pairs. All EVEN => identity (A1(0) lesson).
SWEEP = [("ref", [0, 0, 0, 0, 0, 0]),
         ("cx12", [2, 2, 2, 2, 2, 2]),
         ("cx24", [4, 4, 4, 4, 4, 4]),
         ("cx42", [6, 6, 6, 8, 8, 8])]


def eligible_pairs(n=6):
    with open(os.path.join(RESULTS, "exp144_layout_gated_ember.json")) as f:
        g = json.load(f)
    return [tuple(e["pair"]) for e in g["eligible"][:n]]


def build(pairs, per_pair):
    from qiskit import QuantumCircuit
    n = len(pairs)
    lp = [(2 * i, 2 * i + 1) for i in range(n)]
    flat = [q for p in lp for q in p]
    qc = QuantumCircuit(2 * n, len(flat))
    for a, b in lp:
        qc.h(a); qc.cx(a, b)
    qc.barrier(flat)
    for (a, b), cnt in zip(lp, per_pair):
        for _ in range(cnt):
            qc.cx(a, b)
    qc.barrier(flat)
    for a, b in lp:
        qc.cx(a, b); qc.h(a)
    qc.measure(flat, range(len(flat)))
    return qc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if not (a.dry_run or a.fly):
        ap.print_help(); return 0

    try:
        from run_exp66_qpu_partb import _get_ibm_service
        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2
        print("submit imports: resolved ✓")
    except Exception as e:
        print(f"REFUSING: submit deps do not import ({type(e).__name__}: {e})")
        return 2

    pairs = eligible_pairs(6)
    print(f"pairs (same §8 cohort as A1(0) and wave 1): {pairs}")

    from qiskit.quantum_info import Statevector
    arms = {}
    print("\n=== identity-equivalence (every arm must be |0..0>) ===")
    bad = 0
    for name, per in SWEEP:
        qc = build(pairs, per)
        p0 = abs(Statevector.from_instruction(
            qc.remove_final_measurements(inplace=False)).data[0]) ** 2
        ok = p0 > 0.999
        bad += (not ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:5s} extra_CX={sum(per):2d}  P(|0..0>)={p0:.4f}")
        arms[name] = qc
    if bad:
        print("REFUSING: non-identity arm measures logic, not noise.")
        return 1

    if a.dry_run:
        print("\nDRY-RUN: 4 arms built, identity-verified, nothing submitted.")
        return 0

    svc = _get_ibm_service()
    backend = svc.backend(a.backend)
    print(f"\n{backend.name}: operational={backend.status().operational} "
          f"pending={backend.status().pending_jobs}")
    layout = [q for p in pairs for q in p]
    tpubs, order = [], []
    for name, _ in SWEEP:
        t = transpile(arms[name], backend, initial_layout=layout,
                      optimization_level=0, seed_transpiler=144)
        tpubs.append((t, None, SHOTS)); order.append(name)
    job = SamplerV2(mode=backend).run(tpubs)
    man = {"exp": "144-A1(0b)-cxsweep", "arms": order,
           "extra_cx": {n: sum(p) for n, p in SWEEP},
           "pairs": [list(p) for p in pairs], "shots": SHOTS,
           "job_id": job.job_id(), "backend": a.backend,
           "anchor": "A1(0) ARM-CX (42 extra CX) measured 0.527 — cx42 here must reproduce it"}
    outp = os.path.join(RESULTS, "exp144_a1b_cxsweep_manifest.json")
    with open(outp, "w") as f:
        json.dump(man, f, indent=1)
    print(f"SUBMITTED A1(0b): job {job.job_id()} (4-arm CX sweep, one window) -> {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
