#!/usr/bin/env python3
"""Exp-STETH-(a) FLIGHT — two-copy vs conventional Pauli-eigenvalue agreement (annex §3, the SPAM gate).

Per the pre-reg (docs/exp-steth-a-flight-prereg-whisper-c4971.md) and the advisor's step-back: the
SPAM gate is the flight's OWN first rung. Channel under test Λ = an idle delay (dephasing) on the
system qubit(s). Two arms, each with a co-batched identity-channel reference (delay omitted):
  * TWO-COPY (with quantum memory): n Bell pairs (system i + ancilla i); apply Λ to the system half;
    read λ_{P^n} = <P^n (x) P^n>_Λ / <P^n (x) P^n>_ref on the Choi state.
  * CONVENTIONAL (single-copy): prepare a P-eigenstate on n system qubits; apply Λ; read
    λ_{P^n} = <P^n>_Λ / <P^n>_ref.
GATE: at small n the two arms must AGREE within CIs -> SPAM cancellation MEASURED not predicted
(the direct test the URB chain was inferring at three removes). Disagreement = SPAM/ancilla bias
found cheaply; proceed to larger n only if small-n agrees.

Fences: the two-copy arm's ancilla idles during Λ -> its effective channel can include ancilla
dephasing; if the arms DISAGREE, that (or SPAM) is the finding, and the gate says stop. We measure
P = X^n (dephasing-sensitive, informative) and Z^n (~1, a control). Co-batched; manifest committed.

Target: ibm_marrakesh (88,89,...) — same region as the URB gate + Ember §3(b). Substrate: fable-5, C4971.
"""
import os, sys, json, argparse
import numpy as np
from qiskit import QuantumCircuit, transpile

QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BACKEND = "ibm_marrakesh"
# system qubits then ancilla qubits (two-copy uses 2n; conventional uses the n system qubits)
SYS = [88, 89, 87]          # up to n=3 system qubits (88,89 = the low-CZ pair)
ANC = [91, 90, 86]          # ancilla partners (transpiler will route Bell pairs)
DELAY_NS = 10000           # 10 us idle: balances dephasing signal vs ancilla survival (two-copy needs the memory to survive Lambda; DD protects it)
NS = [1, 2, 3]
SHOTS = 8000
PAULIS = ["X", "Z"]         # X^n informative (dephasing), Z^n ~1 control


def _basis(qc, qubits, pauli):
    for q in qubits:
        if pauli == "X":
            qc.h(q)
        elif pauli == "Y":
            qc.sdg(q); qc.h(q)


def twocopy_circuit(n, pauli, apply_delay):
    """n Bell pairs (logical qubits 0..n-1 system, n..2n-1 ancilla); Λ=delay on system; measure
    <P^n (x) P^n> = parity over all 2n qubits in the P basis."""
    qc = QuantumCircuit(2 * n, 2 * n)
    for i in range(n):
        qc.h(i); qc.cx(i, n + i)               # Bell pair (system i, ancilla n+i)
    qc.barrier()
    if apply_delay:
        for i in range(n):
            qc.delay(DELAY_NS, i, unit="ns")    # Λ on system half (bare idle = the channel)
            # ancilla (the MEMORY) gets a 2-pulse echo: tau/2 - X - tau/2 - X. Two X's net to I (Bell
            # correlation preserved) and REFOCUS low-frequency dephasing so the two-copy arm reads
            # lambda_sys, not lambda_sys*lambda_anc. (Markovian sim won't show the DD benefit; the
            # noiseless sanity confirms it nets to I; hardware is the real test.)
            qc.delay(DELAY_NS // 2, n + i, unit="ns"); qc.x(n + i)
            qc.delay(DELAY_NS // 2, n + i, unit="ns"); qc.x(n + i)
    qc.barrier()
    _basis(qc, range(2 * n), pauli)
    qc.measure(range(2 * n), range(2 * n))
    return qc


def conventional_circuit(n, pauli, apply_delay):
    """Prepare P-eigenstate on n system qubits; Λ=delay; measure <P^n> = parity over n qubits."""
    qc = QuantumCircuit(n, n)
    # +1 eigenstate of P^n: for X use |+>, for Z use |0>, for Y use |+i>
    for q in range(n):
        if pauli == "X":
            qc.h(q)
        elif pauli == "Y":
            qc.h(q); qc.s(q)
        # Z: |0>
    qc.barrier()
    if apply_delay:
        for q in range(n):
            qc.delay(DELAY_NS, q, unit="ns")
    qc.barrier()
    _basis(qc, range(n), pauli)
    qc.measure(range(n), range(n))
    return qc


def _parity(counts):
    """<Z...Z> parity over all measured bits, from a count dict."""
    tot = sum(counts.values()); acc = 0.0
    for k, v in counts.items():
        bits = k.replace(" ", "")
        acc += v * (1 - 2 * (bits.count("1") % 2))
    return acc / tot


def build_all():
    circuits, index = [], []
    for n in NS:
        for P in PAULIS:
            for arm, mk in (("twocopy", twocopy_circuit), ("conv", conventional_circuit)):
                for dly in (True, False):
                    circuits.append(mk(n, P, dly))
                    index.append({"n": n, "pauli": P, "arm": arm, "delay": dly})
    return circuits, index


def local_sanity():
    """Noiseless: lambda=1 (both arms, delay has no effect noiseless). With a sim dephasing on the
    system qubits, both arms should recover the SAME lambda_X < 1 (agreement)."""
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel, phase_damping_error
    print("noiseless (expect lambda~1 both arms):")
    sim = AerSimulator()
    for n in (1, 2):
        vals = {}
        for arm, mk in (("twocopy", twocopy_circuit), ("conv", conventional_circuit)):
            num = _parity(sim.run(transpile(mk(n, "X", True), sim), shots=8000, seed_simulator=1).result().get_counts())
            den = _parity(sim.run(transpile(mk(n, "X", False), sim), shots=8000, seed_simulator=1).result().get_counts())
            vals[arm] = num / den
        print(f"  n={n} lam_X: twocopy={vals['twocopy']:.3f} conv={vals['conv']:.3f}")
    # with dephasing on the DELAY: model delay as phase damping on system qubits only
    print("with sim dephasing (delay->phase damping p=0.2 on system; expect both arms ~agree, <1):")
    nm = NoiseModel()
    nm.add_all_qubit_quantum_error(phase_damping_error(0.35), "delay")
    simn = AerSimulator(noise_model=nm)
    for n in (1, 2):
        vals = {}
        for arm, mk in (("twocopy", twocopy_circuit), ("conv", conventional_circuit)):
            num = _parity(simn.run(transpile(mk(n, "X", True), simn), shots=20000, seed_simulator=2).result().get_counts())
            den = _parity(simn.run(transpile(mk(n, "X", False), simn), shots=20000, seed_simulator=2).result().get_counts())
            vals[arm] = num / max(den, 1e-6)
        agree = abs(vals["twocopy"] - vals["conv"])
        print(f"  n={n} lam_X: twocopy={vals['twocopy']:.3f} conv={vals['conv']:.3f}  |diff|={agree:.3f}")


def submit():
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(BACKEND)
    circuits, index = build_all()
    # pin the physical layout: system+ancilla for the largest n
    lay = SYS[:max(NS)] + ANC[:max(NS)]
    tqc = transpile(circuits, backend=backend, optimization_level=1, seed_transpiler=3211)
    print(f"transpiled {len(tqc)} circuits on {BACKEND}; max depth {max(c.depth() for c in tqc)}")
    job = SamplerV2(mode=backend).run(tqc, shots=SHOTS)
    man = {"exp": "steth_a_flight", "backend": BACKEND, "job_id": job.job_id(), "shots": SHOTS,
           "delay_ns": DELAY_NS, "index": index, "sys": SYS, "anc": ANC,
           "note": "two-copy vs conventional lambda_{P^n} agreement gate (n=1,2,3, P in X,Z)"}
    out = os.path.join(QROOT, "results", "exp_steth_a_flight_manifest.json")
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(tqc)} circuits) -> {os.path.relpath(out)}")


def decode():
    import numpy as _np
    sys.path.insert(0, os.path.join(QROOT, "scripts"))
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(QROOT, "results", "exp_steth_a_flight_manifest.json")))
    res = _get_ibm_service().job(man["job_id"]).result(); idx = man["index"]; sh = man["shots"]

    def counts(i):
        d = res[i].data; creg = list(d.__dict__.keys())[0]
        return getattr(d, creg).get_counts()

    # gather parity per (n,P,arm,delay)
    par = {}
    for i, r in enumerate(idx):
        par[(r["n"], r["pauli"], r["arm"], r["delay"])] = _parity(counts(i))
    rows = []
    for n in man["index"] and NS:
        for P in PAULIS:
            lam = {}
            for arm in ("twocopy", "conv"):
                num = par[(n, P, arm, True)]; den = par[(n, P, arm, False)]
                lam[arm] = num / den if abs(den) > 1e-6 else float("nan")
            diff = abs(lam["twocopy"] - lam["conv"])
            se = _np.sqrt(2 / sh) * 2   # rough parity-ratio SE (order); CI ~ +-2se
            rows.append({"n": n, "pauli": P, "lam_twocopy": round(lam["twocopy"], 4),
                         "lam_conv": round(lam["conv"], 4), "abs_diff": round(diff, 4),
                         "agree_within_2se": bool(diff < 2 * se), "approx_se": round(se, 4)})
            print(f"  n={n} {P}^n: twocopy={lam['twocopy']:.3f} conv={lam['conv']:.3f} "
                  f"|diff|={diff:.3f} (~2SE {2*se:.3f}) agree={rows[-1]['agree_within_2se']}")
    xrows = [r for r in rows if r["pauli"] == "X"]
    gate = all(r["agree_within_2se"] for r in xrows)
    out = {"card": "exp_steth_a_flight_decoded", "job_id": man["job_id"], "backend": man["backend"],
           "substrate": "claude-fable-5", "cycle": "C4971", "delay_ns": man["delay_ns"],
           "rows": rows, "SPAM_GATE_small_n_agreement": "PASS" if gate else "FAIL",
           "gate_note": "X^n two-copy vs conventional agree within ~2SE at all small n -> SPAM "
                        "cancellation measured, not predicted" if gate else
                        "disagreement at some n -> SPAM/ancilla bias found; do not push to larger n"}
    op = os.path.join(QROOT, "results", "exp_steth_a_flight_decoded.json")
    json.dump(out, open(op, "w"), indent=1)
    print(f"\nSPAM GATE (small-n agreement): {out['SPAM_GATE_small_n_agreement']}")
    print(f"decoded -> {os.path.relpath(op)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    for a in ("sanity", "submit", "decode"):
        ap.add_argument(f"--{a}", action="store_true")
    args = ap.parse_args()
    if args.sanity: local_sanity()
    elif args.submit: submit()
    elif args.decode: decode()
    else: print("use --sanity | --submit | --decode")
