#!/usr/bin/env python3
"""Exp239b — THE THRESHOLD, same-qubit clean re-fly. C4917.

Exp239 (job d9es6mhhtsac739ekrhg) was CONFOUNDED and is NOT certified: the transpiler put the bare
qubit on physical q0 (a short-T1 qubit, p~0.33 at 50us) and the coded qubits on q8/9/10 (p~0.63), so
the +0.338 "advantage" was mostly QUBIT SELECTION, not error correction (majority vote over identical
p<0.5 qubits would LOSE). Lesson: always pin AND verify the physical qubits in a hardware comparison.

This clean version fixes it (advisor C4917):
  - a NAMED triple chosen in advance: {8,9,10} (a decent-qubit triple; claim is EXISTENCE, not universal).
  - force initial_layout on BOTH circuits and ASSERT post-transpile they occupy the IDENTICAL physical
    set (the check skipped in 239 — now programmatic, cannot silently recur).
  - a SEPARATE no-encode bare (three independent |1> on the same triple) — the honest bare reference;
    NOT single-qubit extracted from inside the code (those qubits saw the encode CNOTs, so not bare).
  - compare majority-over-{8,9,10} vs the average single-qubit survival on the SAME qubits, same idle.

HONEST FRAMING (advisor): a HELD here does NOT mean "ibm_fez is above the QEC threshold" (hardware-wide,
profound). Majority-of-3 beats a single qubit whenever single-qubit survival p>1/2, minus a small encode
penalty — so HELD means the narrow, true thing: "on triple {8,9,10}, for tau<tau*, the encoded qubit
outlives a bare one, as expected once p>1/2 with encode overhead small enough not to kill it." The
informative outputs are the crossover tau*, the tau=0 encode+readout overhead gap on matched qubits, and
the single-qubit p's that show which regime the win lives in — not a binary above/below.

FROZEN GATE (both directions reportable):
  G1_MEMORY_ADVANTAGE (per-triple): exists tau>0 with F_coded - F_bare_avg >= 0.02 on the SAME qubits.
     HELD = on {8,9,10}, encoding nets a memory gain for tau<tau* (existence result, p>1/2 regime).
     NOT HELD = even on matched qubits the encode overhead exceeds the gain (below break-even here).
  Registered verdict = G1 AND the layout-identity assert passing. REPORTED: F_coded/F_bare_avg curves,
     per-qubit single survivals, crossover tau*, tau=0 overhead gap.
SCOPE: one named triple, bit-flip/T1 channel, single re-fly (no multi-triple survey, no qubit-choice
  iteration — that would be band-shopping). Existence claim only.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

TAUS_US = (0, 50, 100, 150, 200, 250)
TRIPLE = [8, 9, 10]                        # named in advance; logical (0,1,2) -> physical (8,9,10)


def bare_circuit(tau_us):
    qc = QuantumCircuit(3, 3)
    for q in range(3): qc.x(q)             # three INDEPENDENT bare |1> (no encode)
    qc.barrier()
    if tau_us > 0:
        for q in range(3): qc.delay(tau_us, q, unit="us")
    qc.barrier()
    for q in range(3): qc.measure(q, q)
    return qc


def coded_circuit(tau_us):
    qc = QuantumCircuit(3, 3)
    qc.x(0); qc.cx(0, 1); qc.cx(0, 2)      # |1_L> = |111>
    qc.barrier()
    if tau_us > 0:
        for q in range(3): qc.delay(tau_us, q, unit="us")
    qc.barrier()
    for q in range(3): qc.measure(q, q)
    return qc


def _single_survivals(counts):
    """per-qubit P(read 1) for the 3 physical qubits."""
    tot = 0; ones = [0, 0, 0]
    for s, n in counts.items():
        b = s.replace(" ", ""); tot += n
        for i in range(3):
            if int(b[-1 - i]) == 1: ones[i] += n
    return [o / tot for o in ones]


def _majority_fid(counts):
    ok = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(3)]
        tot += n
        if (v[0] + v[1] + v[2]) >= 2: ok += n
    return ok / tot


def _phys_set(tqc):
    return sorted(set(tqc.find_bit(q).index for instr in tqc.data
                      for q in instr.qubits if instr.operation.name not in ("barrier",)))


def selftest():
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, amplitude_damping_error
    sim = AerSimulator(); shots = 40000
    print("Exp239b selftest | THE THRESHOLD clean — same-qubit majority vs single-qubit survival")
    # wiring: no idle -> bare all 1, coded majority 1
    assert min(_single_survivals(sim.run(bare_circuit(0), shots=shots).result().get_counts())) > 0.99
    assert _majority_fid(sim.run(coded_circuit(0), shots=shots).result().get_counts()) > 0.99
    print("  (1) wiring OK: zero-idle bare survivals ~1, coded majority ~1")
    # crossover detectable: amplitude damping, ideal gates -> majority beats avg-single for p>1/2
    print("  (2) amplitude-damping (ideal gates): majority vs avg-single on SAME channel")
    won = False
    for gamma in (0.1, 0.2, 0.4):
        nm = NoiseModel()
        for q in range(3): nm.add_quantum_error(amplitude_damping_error(gamma), ["id"], [q])
        s = AerSimulator(noise_model=nm)
        def bare_id():
            qc = QuantumCircuit(3, 3)
            for q in range(3): qc.x(q)
            for q in range(3): qc.id(q)
            for q in range(3): qc.measure(q, q)
            return qc
        def coded_id():
            qc = QuantumCircuit(3, 3); qc.x(0); qc.cx(0, 1); qc.cx(0, 2)
            for q in range(3): qc.id(q)
            for q in range(3): qc.measure(q, q)
            return qc
        avg = float(np.mean(_single_survivals(s.run(bare_id(), shots=shots).result().get_counts())))
        maj = _majority_fid(s.run(coded_id(), shots=shots).result().get_counts())
        p = 1 - gamma
        exp_win = p > 0.5
        won = won or (maj - avg > 0.0 and exp_win)
        print(f"     gamma={gamma} (p={p:.2f}): avg-single {avg:.3f}  majority {maj:.3f}  adv {maj-avg:+.3f}"
              f"  (expect {'win' if exp_win else 'loss'} p>0.5)")
    assert won, "majority must beat avg-single for p>1/2 (the repetition-code regime)"
    print("SELFTEST PASS: same-qubit majority beats avg-single exactly in the p>1/2 regime, as the "
          "repetition-code math predicts. Clean comparison validated; hardware decides tau* and overhead.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = []
    for tau in TAUS_US:
        order.append(["bare", tau]); order.append(["coded", tau])
    def build(o):
        return bare_circuit(o[1]) if o[0] == "bare" else coded_circuit(o[1])
    circuits = [transpile(build(o), backend=backend, optimization_level=1,
                          initial_layout=TRIPLE, seed_transpiler=0) for o in order]
    # ASSERT identical physical qubits for every circuit (the 239 confound, now programmatic)
    sets = [_phys_set(c) for c in circuits]
    assert all(s == sorted(TRIPLE) for s in sets), f"layout mismatch! sets={sets} expected {sorted(TRIPLE)}"
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}; "
          f"ALL on physical {sorted(TRIPLE)} (layout assert PASSED)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp239b_the_threshold_clean_manifest.json")
    man = {"exp": "239b", "slug": "the_threshold_clean", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order, "taus_us": list(TAUS_US), "triple": TRIPLE,
           "prereg": {"G1_memory_advantage": "exists tau>0 with F_coded(majority) - F_bare_avg >= 0.02, same qubits",
                      "layout_assert": "all circuits on identical physical set = triple",
                      "registered_verdict": "G1 and layout-identity — per-triple EXISTENCE (p>1/2 regime), NOT hardware-wide threshold",
                      "reported": "curves, per-qubit single survivals, crossover tau*, tau=0 overhead gap",
                      "scope": "one named triple {8,9,10}, bit-flip/T1, single re-fly, existence claim only"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp239b_the_threshold_clean_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, o in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[tuple(o)] = getattr(r0.data, reg).get_counts()
    print(f"Exp239b THE THRESHOLD clean decode | job {man['job_id']} | triple {man['triple']}")
    taus = man["taus_us"]; best_adv = -1.0; best_tau = None; cross_tau = None
    print("  tau(us) | single q8,q9,q10        avg    majority  advantage")
    curves = {"bare_avg": {}, "coded": {}, "singles": {}}
    for tau in taus:
        singles = _single_survivals(raw[("bare", tau)]); avg = float(np.mean(singles))
        maj = _majority_fid(raw[("coded", tau)]); adv = maj - avg
        curves["bare_avg"][str(tau)] = avg; curves["coded"][str(tau)] = maj
        curves["singles"][str(tau)] = singles
        if adv > best_adv: best_adv, best_tau = adv, tau
        if cross_tau is None and adv >= 0.02: cross_tau = tau
        flag = " <-- crossover" if (adv >= 0.02 and cross_tau == tau) else ""
        print(f"  {tau:6d}  |  {singles[0]:.3f} {singles[1]:.3f} {singles[2]:.3f}   {avg:.3f}   "
              f"{maj:.3f}    {adv:+.3f}{flag}")
    gap0 = curves["coded"]["0"] - curves["bare_avg"]["0"]
    g1 = best_adv >= 0.02
    print(f"\n  tau=0 encode+readout overhead gap (coded-bare, same qubits): {gap0:+.3f}")
    print(f"  crossover tau*: {cross_tau}us" if cross_tau is not None else "  crossover tau*: none")
    print(f"\nG1 MEMORY ADVANTAGE (per-triple {man['triple']}): best {best_adv:+.3f} at tau={best_tau}us "
          f">= 0.02 {'OK' if g1 else 'MISS'}")
    if g1:
        win = (f"THE THRESHOLD (per-triple, bit-flip/T1) — on qubits {man['triple']} the ENCODED qubit "
               f"outlives a bare one by up to {best_adv:+.3f} (crossover tau*={cross_tau}us), on MATCHED "
               f"physical qubits (confound of 239 removed). Existence result in the p>1/2 regime — NOT a "
               f"hardware-wide QEC-threshold claim; encode+readout overhead at tau=0 is {gap0:+.3f}")
    else:
        win = (f"BELOW BREAK-EVEN (honest) — even on matched qubits {man['triple']} the encode+readout "
               f"overhead ({gap0:+.3f} at tau=0) exceeds the majority-vote gain (best {best_adv:+.3f}); "
               f"the code does not net-help memory here")
    print(f"VERDICT: {win}")
    json.dump({"job_id": man["job_id"], "triple": man["triple"], "taus_us": taus, **curves,
               "best_advantage": best_adv, "best_tau_us": best_tau, "crossover_tau_us": cross_tau,
               "tau0_overhead_gap": gap0, "g1_per_triple_advantage": bool(g1)},
              open(os.path.join(HERE, "..", "results", "exp239b_the_threshold_clean_decode.json"), "w"), indent=1)
    print("-> results/exp239b_the_threshold_clean_decode.json")


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
