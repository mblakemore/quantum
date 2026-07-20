#!/usr/bin/env python3
"""Exp241 — THE REPEATED ROUNDS: does live correction pay when you do it over and over? C4919.

The flight Exp240 unlocked. 240 stood up ONE non-destructive syndrome round (learn the error without
collapsing the data, feed-forward the fix) and priced its cost (~45% coherence/round). The primitive
that continuous fault tolerance is built on is doing that round REPEATEDLY: idle, diagnose, fix, reset
the ancillas, repeat — keeping the logical qubit alive across many rounds. The honest question is
whether repeated correction removes more error than its own machinery introduces (the 239b overhead-vs-
protection tension, now for the live loop).

CLEAN CONTROL — the SHAM arm: run the IDENTICAL circuit (same idle, same syndrome extraction, same
mid-circuit ancilla measurement, same reset) but SKIP the feed-forward correction. The only difference
between CORRECTED and SHAM is whether the fix is applied — same qubits, same gate/measurement noise,
same timing — so any advantage is the correction itself, not qubit choice or machinery (the 239b
confound cannot recur: the control is inside the circuit).

METHOD: logical |1_L>=|111> (the T1-decaying state; relaxation |1>->|0> = bit-flips). R rounds, each:
idle tau on the data, extract the two parity syndromes onto ancillas, measure them mid-circuit, (CORRECTED
only) feed-forward X on the flagged qubit, reset ancillas. After R rounds read the data and majority-
vote the logical bit. Corrected should sustain many rounds (it removes <=1 flip/round); sham accumulates
flips and fails once >1 total. Crossover in R shows whether the live loop nets a benefit on ibm_fez.

FROZEN GATE (both directions reportable):
  G1_CORRECTION_PAYS: exists R>=1 with F_corrected(R) - F_sham(R) >= 0.05 — repeated live correction
     keeps |1_L> alive better than the identical machinery WITHOUT the fix.
     HELD = the live QEC loop nets a benefit over multiple rounds on ibm_fez.
     NOT HELD = the per-round machinery cost (240's ~45%) swamps the protection — honest, and it
     quantifies how many live rounds current hardware can sustain (a real, buildable number).
  Registered verdict = G1. REPORTED either way: F_corrected/F_sham vs R, the crossover/best-R, and a
     bare single-qubit reference idled the same total time.
SCOPE: 3-qubit bit-flip code, bit-flip/T1 channel, repeated live rounds with reset + if_test feed-
  forward. Builds directly on 240. The sham arm isolates correction from machinery. Frugal.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
ROUNDS = (0, 1, 2, 3, 4)
TAU_US = 30                                  # idle per round


def coded_circuit(R, tau_us, correct, inject=None):
    """R live rounds on |1_L>. correct=feed-forward on; inject={round:[qubits]} for deterministic
    selftest errors (used INSTEAD of idle), else real idle decay."""
    d = QuantumRegister(3, "d"); a = QuantumRegister(2, "a")
    syns = [ClassicalRegister(2, f"syn{r}") for r in range(R)]
    out = ClassicalRegister(3, "out")
    qc = QuantumCircuit(d, a, *syns, out)
    qc.x(d[0]); qc.cx(d[0], d[1]); qc.cx(d[0], d[2])         # |1_L> = |111>
    for r in range(R):
        qc.barrier()
        if inject is not None:
            for q in inject.get(r, []): qc.x(d[q])           # deterministic error (selftest)
        elif tau_us > 0:
            for i in range(3): qc.delay(tau_us, d[i], unit="us")   # real idle decay (hardware)
        qc.cx(d[0], a[0]); qc.cx(d[1], a[0])                 # a0 = z0 ^ z1
        qc.cx(d[1], a[1]); qc.cx(d[2], a[1])                 # a1 = z1 ^ z2
        qc.measure(a[0], syns[r][0]); qc.measure(a[1], syns[r][1])
        if correct:
            with qc.if_test((syns[r], 1)): qc.x(d[0])
            with qc.if_test((syns[r], 3)): qc.x(d[1])
            with qc.if_test((syns[r], 2)): qc.x(d[2])
        qc.reset(a[0]); qc.reset(a[1])                        # reuse ancillas next round
    qc.barrier()
    for i in range(3): qc.measure(d[i], out[i])
    return qc


def bare_circuit(R, tau_us):
    qc = QuantumCircuit(1, 1)
    qc.x(0)
    if R > 0 and tau_us > 0: qc.delay(R * tau_us, 0, unit="us")   # same total idle
    qc.measure(0, 0)
    return qc


def _majority_from_out(counts):
    """majority vote of the 3 'out' bits -> P(logical=1). counts already the 'out' register."""
    ok = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(3)]
        tot += n
        if (v[0] + v[1] + v[2]) >= 2: ok += n
    return ok / tot


def _out_marginal(counts):
    """extract 'out' register (token 0 = last created) from Aer combined counts."""
    out = {}
    for s, n in counts.items():
        key = s.split(" ")[0]
        out[key] = out.get(key, 0) + n
    return out


def _bare_fid(counts):
    ok = tot = 0
    for s, n in counts.items():
        tot += n
        if int(s.replace(" ", "")[-1]) == 1: ok += n
    return ok / tot


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    print("Exp241 selftest | THE REPEATED ROUNDS — repeated live correction vs sham (no fix)")
    # deterministic: one flip per round on a rotating qubit. Corrected fixes each round -> |111>.
    # Sham accumulates -> after >=2 rounds majority fails.
    for R in (1, 2, 3):
        inj = {r: [r % 3] for r in range(R)}   # round r flips qubit r%3
        fc = _majority_from_out(_out_marginal(sim.run(coded_circuit(R, 0, True, inject=inj),
                                                       shots=shots).result().get_counts()))
        fs = _majority_from_out(_out_marginal(sim.run(coded_circuit(R, 0, False, inject=inj),
                                                       shots=shots).result().get_counts()))
        print(f"  R={R} (one flip/round): corrected {fc:.3f}  sham {fs:.3f}")
        assert fc > 0.99, "corrected must recover every round's single flip -> |111>"
        if R >= 2:
            assert fs < 0.5, "sham must accumulate flips and fail the final majority for R>=2"
    print("SELFTEST PASS: repeated feed-forward correction recovers a per-round flip every round "
          "(corrected stays |111>), while the identical sham circuit without the fix accumulates errors "
          "and fails. The live loop logic is correct; hardware decides whether it pays vs its own noise.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = []
    for R in ROUNDS:
        order.append(["corr", R]); order.append(["sham", R]); order.append(["bare", R])
    def build(o):
        k, R = o
        if k == "bare": return bare_circuit(R, TAU_US)
        return coded_circuit(R, TAU_US, k == "corr")
    circuits = [transpile(build(o), backend=backend, optimization_level=1, seed_transpiler=0) for o in order]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)} (repeated mid-circuit measure+reset+if_test)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp241_repeated_rounds_manifest.json")
    man = {"exp": 241, "slug": "repeated_rounds", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order, "rounds": list(ROUNDS), "tau_us": TAU_US,
           "prereg": {"G1_correction_pays": "exists R>=1 with F_corrected - F_sham >= 0.05",
                      "registered_verdict": "G1 — HELD=live loop nets benefit over rounds, NOT HELD=machinery swamps (honest)",
                      "reported": "F_corrected/F_sham vs R, best-R crossover, bare reference",
                      "scope": "3-qubit bit-flip code, T1 channel, repeated live rounds; sham arm isolates correction from machinery"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp241_repeated_rounds_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    idx_of = {tuple(o): i for i, o in enumerate(man["order"])}
    def outc(o):
        r0 = res[idx_of[tuple(o)]]
        return getattr(r0.data, "out").get_counts()
    print(f"Exp241 THE REPEATED ROUNDS decode | job {man['job_id']} | tau={man['tau_us']}us/round")
    print("  R | F_corrected  F_sham   advantage | F_bare(single)")
    best_adv = -1.0; best_R = None
    fc_c, fs_c, fb_c = {}, {}, {}
    for R in man["rounds"]:
        fc = _majority_from_out(outc(["corr", R]))
        fs = _majority_from_out(outc(["sham", R]))
        fb = _bare_fid(getattr(res[idx_of[("bare", R)]].data, list(res[idx_of[("bare", R)]].data.keys())[0]).get_counts())
        fc_c[R], fs_c[R], fb_c[R] = fc, fs, fb
        adv = fc - fs
        if R >= 1 and adv > best_adv: best_adv, best_R = adv, R
        print(f"  {R} |   {fc:.3f}      {fs:.3f}    {adv:+.3f}  |   {fb:.3f}")
    g1 = best_adv >= 0.05
    print(f"\nG1 CORRECTION PAYS: best F_corrected-F_sham = {best_adv:+.3f} at R={best_R} >= 0.05 {'OK' if g1 else 'MISS'}")
    if g1:
        win = (f"THE REPEATED ROUNDS PAY — over R live rounds the fed-forward correction keeps |1_L> alive "
               f"better than the identical machinery WITHOUT the fix (best +{best_adv:.3f} at R={best_R}): "
               f"the continuous-QEC loop nets a benefit on ibm_fez, correction beating its own overhead")
    else:
        win = (f"MACHINERY-LIMITED (honest) — repeated live correction does not beat the sham (best "
               f"{best_adv:+.3f} at R={best_R}); the per-round syndrome+measure+reset overhead (240's ~45%) "
               f"swamps the protection. Quantifies the live-round budget current hardware sustains")
    print(f"VERDICT: {win}")
    json.dump({"job_id": man["job_id"], "rounds": man["rounds"], "tau_us": man["tau_us"],
               "F_corrected": fc_c, "F_sham": fs_c, "F_bare": fb_c,
               "best_advantage": best_adv, "best_R": best_R, "g1_correction_pays": bool(g1)},
              open(os.path.join(HERE, "..", "results", "exp241_repeated_rounds_decode.json"), "w"), indent=1)
    print("-> results/exp241_repeated_rounds_decode.json")


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
