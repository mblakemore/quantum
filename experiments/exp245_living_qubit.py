#!/usr/bin/env python3
"""Exp245 — THE LIVING QUBIT: the measured lifespan of a self-healing qubit. C4925.

Horizons-6 P2 (the-living-ship doc). Exp241 proved repeated live correction PAYS and COMPOUNDS through
R=4 (corrected beat an identical no-fix sham by a gap growing +0.054->+0.341). P2 turns that demo into a
NUMBER: push the round-sweep until the advantage PEAKS and TURNS OVER (the point where the per-round
machinery cost finally outruns the protection — the limit of self-healing), and extract the
COHERENCE-LIFESPAN EXTENSION FACTOR — how many times longer a self-healing qubit remembers |1_L> than
the identical machinery WITHOUT the fix.

CONFOUND-FREE by construction (241's design): CORRECTED and SHAM are the SAME circuit — same data
qubits, same idle, same non-destructive syndrome extraction, same mid-circuit measurement, same reset —
differing ONLY in whether the feed-forward X is applied. Any difference is the correction, not qubit
choice or machinery (the 239b lesson built in). A bare single qubit idled the same total time is
reported as CONTEXT (not qubit-matched, the 241 caveat).

METHOD: |1_L>=|111>; R rounds of {idle tau -> parity syndrome (2 ancillas) -> measure mid-circuit ->
(CORRECTED) feed-forward X -> reset}; majority-vote readout. Sweep R to catch the turnover. The lifespan
metric is ROUNDS-TO-THRESHOLD: the (interpolated) R at which majority fidelity crosses F=0.75 (halfway
from 1 to the 0.5 mixed floor); extension factor = R75(corrected) / R75(sham).

FROZEN GATE (both directions reportable — a lifespan is a measurement, not a target):
  G1_LIVING: (a) peak advantage max_R [F_corrected(R) - F_sham(R)] >= 0.10 (correction pays across the
     sweep, confirming+extending 241) AND (b) extension factor R75(corrected)/R75(sham) >= 1.3 (the
     self-healing qubit's information half-life is at least 1.3x the un-corrected machinery's).
     HELD = a measured self-healing lifespan. REPORTED regardless: full F_corr/F_sham/F_bare curves,
     peak advantage & the round R* where it peaks, whether a turnover is observed, and the factor.
SCOPE: 3-qubit bit-flip code, bit-flip/T1 channel, repeated live rounds (reset + if_test feed-forward),
  tau=30us/round. Extends 241. The certified claim is corrected-vs-sham (confound-free); bare is context.
  Deep at high R (each round adds machinery) — the deep points ARE the turnover regime, expected noisy.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
ROUNDS = (0, 1, 2, 3, 4, 6, 8)               # spans past 241's R=4 to catch the turnover
TAU_US = 30


def coded_circuit(R, tau_us, correct, inject=None):
    d = QuantumRegister(3, "d"); a = QuantumRegister(2, "a")
    syns = [ClassicalRegister(2, f"syn{r}") for r in range(R)]
    out = ClassicalRegister(3, "out")
    qc = QuantumCircuit(d, a, *syns, out)
    qc.x(d[0]); qc.cx(d[0], d[1]); qc.cx(d[0], d[2])           # |1_L> = |111>
    for r in range(R):
        qc.barrier()
        if inject is not None:
            for q in inject.get(r, []): qc.x(d[q])
        elif tau_us > 0:
            for i in range(3): qc.delay(tau_us, d[i], unit="us")
        qc.cx(d[0], a[0]); qc.cx(d[1], a[0])
        qc.cx(d[1], a[1]); qc.cx(d[2], a[1])
        qc.measure(a[0], syns[r][0]); qc.measure(a[1], syns[r][1])
        if correct:
            with qc.if_test((syns[r], 1)): qc.x(d[0])
            with qc.if_test((syns[r], 3)): qc.x(d[1])
            with qc.if_test((syns[r], 2)): qc.x(d[2])
        qc.reset(a[0]); qc.reset(a[1])
    qc.barrier()
    for i in range(3): qc.measure(d[i], out[i])
    return qc


def bare_circuit(R, tau_us):
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    if R > 0 and tau_us > 0: qc.delay(R * tau_us, 0, unit="us")
    qc.measure(0, 0)
    return qc


def _majority(counts):
    ok = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(3)]; tot += n
        if (v[0] + v[1] + v[2]) >= 2: ok += n
    return ok / tot


def _out_marginal(counts):
    out = {}
    for s, n in counts.items():
        k = s.split(" ")[0]; out[k] = out.get(k, 0) + n
    return out


def _bare_fid(counts):
    ok = tot = 0
    for s, n in counts.items():
        tot += n
        if int(s.replace(" ", "")[-1]) == 1: ok += n
    return ok / tot


def _r_to_threshold(rounds, fids, thr=0.75):
    """interpolated round at which F crosses thr on the way down; >max if never crosses."""
    for i in range(1, len(rounds)):
        if fids[i - 1] >= thr > fids[i]:
            frac = (fids[i - 1] - thr) / (fids[i - 1] - fids[i]) if fids[i - 1] != fids[i] else 0
            return rounds[i - 1] + frac * (rounds[i] - rounds[i - 1])
    return float(rounds[-1]) if fids[-1] >= thr else 0.0


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    print("Exp245 selftest | THE LIVING QUBIT — repeated live correction, lifespan of self-healing")
    for R in (1, 2, 3):
        inj = {r: [r % 3] for r in range(R)}   # one flip/round rotating -> corrected recovers, sham fails R>=2
        fc = _majority(_out_marginal(sim.run(coded_circuit(R, 0, True, inject=inj), shots=shots).result().get_counts()))
        fs = _majority(_out_marginal(sim.run(coded_circuit(R, 0, False, inject=inj), shots=shots).result().get_counts()))
        print(f"  R={R} (one flip/round): corrected {fc:.3f}  sham {fs:.3f}")
        assert fc > 0.99, "corrected must recover a per-round single flip"
        if R >= 2: assert fs < 0.5, "sham must accumulate and fail"
    # metric sanity: a faster-decaying curve must reach threshold at fewer rounds
    r_fast = _r_to_threshold([0, 1, 2, 3], [1.0, 0.6, 0.3, 0.1])
    r_slow = _r_to_threshold([0, 1, 2, 3], [1.0, 0.9, 0.8, 0.7])
    print(f"  metric check: R75(fast decay)={r_fast:.2f} < R75(slow decay)={r_slow:.2f}")
    assert r_fast < r_slow, "extension-factor metric must order lifespans correctly"
    print("SELFTEST PASS: live loop recovers per-round flips (corrected) while sham accumulates, and the "
          "rounds-to-threshold lifespan metric orders decay curves correctly. Hardware measures the factor.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = []
    for R in ROUNDS:
        order.append(["corr", R]); order.append(["sham", R]); order.append(["bare", R])
    def build(o):
        k, R = o
        return bare_circuit(R, TAU_US) if k == "bare" else coded_circuit(R, TAU_US, k == "corr")
    circuits = [transpile(build(o), backend=backend, optimization_level=1, seed_transpiler=0) for o in order]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)} (repeated live rounds; deep at high R = turnover regime)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp245_living_qubit_manifest.json")
    man = {"exp": 245, "slug": "living_qubit", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order, "rounds": list(ROUNDS), "tau_us": TAU_US,
           "prereg": {"G1_living": "peak (F_corr-F_sham) >= 0.10 AND extension R75(corr)/R75(sham) >= 1.3",
                      "registered_verdict": "G1 — a measured self-healing lifespan; both directions reported",
                      "reported": "full curves, peak advantage & R*, turnover, extension factor",
                      "scope": "3-qubit bit-flip code, T1 channel, repeated live rounds; corrected-vs-sham certified, bare context"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp245_living_qubit_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    idx_of = {tuple(o): i for i, o in enumerate(man["order"])}
    def outc(o):
        return getattr(res[idx_of[tuple(o)]].data, "out").get_counts()
    rounds = man["rounds"]
    print(f"Exp245 THE LIVING QUBIT decode | job {man['job_id']} | tau={man['tau_us']}us/round")
    print("  R | F_corrected  F_sham   advantage | F_bare")
    fc, fs, fb = [], [], []
    for R in rounds:
        c = _majority(outc(["corr", R])); s = _majority(outc(["sham", R]))
        r0 = res[idx_of[("bare", R)]]; b = _bare_fid(getattr(r0.data, list(r0.data.keys())[0]).get_counts())
        fc.append(c); fs.append(s); fb.append(b)
        print(f"  {R} |   {c:.3f}      {s:.3f}    {c-s:+.3f}  |  {b:.3f}")
    advs = [fc[i] - fs[i] for i in range(len(rounds))]
    peak = max(advs[1:]); rstar = rounds[advs.index(peak)]
    turnover = next((rounds[i] for i in range(2, len(rounds)) if advs[i] < advs[i - 1] - 0.02), None)
    r75_c = _r_to_threshold(rounds, fc); r75_s = _r_to_threshold(rounds, fs); r75_b = _r_to_threshold(rounds, fb)
    ext = (r75_c / r75_s) if r75_s > 0 else float("inf")
    ext_b = (r75_c / r75_b) if r75_b > 0 else float("inf")
    g1 = peak >= 0.10 and ext >= 1.3
    print(f"\n  peak advantage {peak:+.3f} at R*={rstar}"
          + (f"; turnover at R={turnover}" if turnover else "; no turnover yet in range"))
    print(f"  rounds-to-F0.75: corrected {r75_c:.2f} | sham {r75_s:.2f} | bare {r75_b:.2f}  (each round = {man['tau_us']}us)")
    print(f"  LIFESPAN EXTENSION FACTOR: corrected vs sham = {ext:.2f}x | corrected vs bare (context) = {ext_b:.2f}x")
    print(f"\nG1 LIVING: peak {peak:+.3f}>=0.10 AND extension {ext:.2f}x>=1.3 {'OK' if g1 else 'MISS'}")
    if g1:
        win = (f"THE LIVING QUBIT — a self-healing qubit with a MEASURED lifespan: repeated live correction "
               f"extends |1_L>'s information half-life to {ext:.2f}x the identical un-corrected machinery "
               f"(and ~{ext_b:.1f}x a bare qubit), the advantage peaking at R*={rstar}"
               + (f" then turning over at R={turnover} as the per-round cost catches up" if turnover else "")
               + ". The campaign's first qubit that heals faster than it forgets, quantified")
    else:
        win = (f"HONEST NULL — the lifespan extension is {ext:.2f}x (< 1.3) / peak advantage {peak:+.3f}: the "
               f"per-round machinery cost limits the self-healing gain on this hardware. The measured ceiling.")
    print(f"VERDICT: {win}")
    json.dump({"job_id": man["job_id"], "rounds": rounds, "F_corrected": fc, "F_sham": fs, "F_bare": fb,
               "peak_advantage": peak, "R_star": rstar, "turnover_R": turnover,
               "R75_corrected": r75_c, "R75_sham": r75_s, "R75_bare": r75_b,
               "extension_vs_sham": ext, "extension_vs_bare": ext_b, "g1_living": bool(g1)},
              open(os.path.join(HERE, "..", "results", "exp245_living_qubit_decode.json"), "w"), indent=1)
    print("-> results/exp245_living_qubit_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
