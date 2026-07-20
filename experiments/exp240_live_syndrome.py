#!/usr/bin/env python3
"""Exp240 — THE LIVE SYNDROME: learn the error WITHOUT measuring the data, and keep the superposition. C4918.

Something solid to build on (Creator directive). Every code in the campaign so far decoded DESTRUCTIVELY
— a coherent inverse-encoder that collapses the logical qubit to read it. The primitive that ALL
scalable QEC is built on, and that we have never done, is NON-DESTRUCTIVE syndrome extraction: two
parity ancillas learn WHICH qubit flipped without learning WHAT the logical state is, so a logical
SUPERPOSITION survives the measurement; then a classical feed-forward applies the fix. This is the
beating heart of fault tolerance and the block that repeated-round correction and every logical gate
are built on.

The deep property, made witnessable: the ancilla a1 = z0 XOR z1 is a PARITY. On |+_L>=(|000>+|111>)/
sqrt2 both components have z0 XOR z1 = 0, so measuring a1 returns 0 DETERMINISTICALLY and does NOT
distinguish |000> from |111> — the superposition is preserved. A DIRECT measurement of z0 would give
0/1 at random and COLLAPSE it. So:
  ARM A (live/non-destructive): |+_L> -> inject bit-flip -> parity-ancilla syndrome (measure a1,a2,
     mid-circuit) -> feed-forward X on the flagged qubit -> read logical X-bar = X0X1X2. Expect <X-bar>
     ~ +1: the superposition SURVIVED and the error was corrected, all in one live pass.
  ARM B (destructive control): same, but MEASURE a data qubit (z0) directly instead of the parity. This
     collapses |+_L> -> <X-bar> ~ 0. Proves the ancilla method's non-destructiveness is real, not assumed.

FROZEN GATES (checked in selftest, statevector-exact):
  G1_LIVE_PRESERVES: over the error cases, <X-bar>(arm A, corrected) - <X-bar>(arm B, destructive) >=
     0.50 — the parity-ancilla syndrome preserves the logical superposition that a direct data
     measurement destroys.
  G2_SYNDROME_LEARNS: the mid-circuit (a1,a2) matches the injected error (X0->10, X1->11, X2->01,
     none->00) with >= 0.75 probability — the ancillas genuinely learn WHICH qubit flipped.
  Registered verdict = G1 and G2. REPORTED: per-error <X-bar> both arms, syndrome-match rates.
SCOPE: 3-qubit bit-flip code, single live round, bit-flip channel. First NON-DESTRUCTIVE syndrome
  extraction + feed-forward in the campaign (prior decodes were destructive coherent inverse-encoders).
  The BUILDABLE primitive: repeated rounds, logical gates between live-corrected qubits, and continuous
  QEC all compose from this. Uses mid-circuit measurement + if_test feed-forward (as exp227). Frugal.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
ERRORS = ("none", "0", "1", "2")
EXPECTED_SYN = {"none": 0, "0": 1, "1": 3, "2": 2}   # a1 + 2*a2, with a1=z0^z1, a2=z1^z2


def _err(qc, err):
    if err != "none": qc.x(int(err))


def circuit_live(err):
    """ARM A — non-destructive parity-ancilla syndrome + feed-forward, preserve |+_L>."""
    d = QuantumRegister(3, "d"); a = QuantumRegister(2, "a")
    syn = ClassicalRegister(2, "syn"); out = ClassicalRegister(3, "out")
    qc = QuantumCircuit(d, a, syn, out)
    qc.h(d[0]); qc.cx(d[0], d[1]); qc.cx(d[0], d[2])        # |+_L> = (|000>+|111>)/sqrt2
    qc.barrier()
    _err_reg(qc, d, err); qc.barrier()
    qc.cx(d[0], a[0]); qc.cx(d[1], a[0])                    # a1 = z0 ^ z1
    qc.cx(d[1], a[1]); qc.cx(d[2], a[1])                    # a2 = z1 ^ z2
    qc.measure(a[0], syn[0]); qc.measure(a[1], syn[1])       # LIVE syndrome (mid-circuit)
    with qc.if_test((syn, 1)): qc.x(d[0])                   # feed-forward correction
    with qc.if_test((syn, 3)): qc.x(d[1])
    with qc.if_test((syn, 2)): qc.x(d[2])
    qc.barrier()
    for i in range(3): qc.h(d[i])                           # read logical X-bar = X0X1X2
    for i in range(3): qc.measure(d[i], out[i])
    return qc


def circuit_destructive(err):
    """ARM B — control: measure a DATA qubit (z0) directly; collapses the superposition."""
    d = QuantumRegister(3, "d"); scr = ClassicalRegister(1, "scr"); out = ClassicalRegister(3, "out")
    qc = QuantumCircuit(d, scr, out)
    qc.h(d[0]); qc.cx(d[0], d[1]); qc.cx(d[0], d[2])
    qc.barrier()
    _err_reg(qc, d, err); qc.barrier()
    qc.measure(d[0], scr[0])                                # DIRECT data measurement -> collapse
    qc.barrier()
    for i in range(3): qc.h(d[i])
    for i in range(3): qc.measure(d[i], out[i])
    return qc


def _err_reg(qc, d, err):
    if err != "none": qc.x(d[int(err)])


def _xbar(counts):
    """<X-bar> = <X0X1X2> from the 3-bit 'out' register parity."""
    c = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); par = int(b[-1]) ^ int(b[-2]) ^ int(b[-3])
        c += (1 - 2 * par) * n; tot += n
    return c / tot


def _syn_match(counts, err):
    want = EXPECTED_SYN[err]; ok = tot = 0
    for s, n in counts.items():
        v = int(s.replace(" ", ""), 2); tot += n
        if v == want: ok += n
    return ok / tot


def _marginal(counts, token):
    """extract one classical register's marginal from Aer combined counts (space-separated, reverse
    creation order): token 0 = 'out' (last created), token 1 = 'syn'/'scr'."""
    out = {}
    for s, n in counts.items():
        key = s.split(" ")[token]
        out[key] = out.get(key, 0) + n
    return out


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    print("Exp240 selftest | THE LIVE SYNDROME — non-destructive parity extraction + feed-forward")
    worst_adv = 1.0; worst_syn = 1.0
    for err in ERRORS:
        rl = sim.run(circuit_live(err), shots=shots).result().get_counts()
        rd = sim.run(circuit_destructive(err), shots=shots).result().get_counts()
        xa = _xbar(_marginal(rl, 0))           # 'out' register = token 0
        xb = _xbar(_marginal(rd, 0))
        sm = _syn_match(_marginal(rl, 1), err)  # 'syn' register = token 1
        worst_adv = min(worst_adv, xa - xb); worst_syn = min(worst_syn, sm)
        print(f"  err {err}: <X-bar> live {xa:+.3f}  destructive {xb:+.3f}  adv {xa-xb:+.3f} | syndrome-match {sm:.3f}")
    assert worst_adv > 0.9, "live arm must preserve <X-bar> where destructive collapses it"
    assert worst_syn > 0.9, "parity ancillas must learn the injected error"
    print("SELFTEST PASS: parity-ancilla syndrome preserves the logical superposition (<X-bar>~+1) that a "
          "direct data measurement destroys (<X-bar>~0), AND learns which qubit flipped, correcting it "
          "by feed-forward — non-destructive live QEC. Cleared to fly.")


def _combined_from_data(r0):
    """rebuild a combined-string counts dict from a SamplerV2 result's registers (out + syn/scr)."""
    regs = list(r0.data.keys())
    per = {rg: getattr(r0.data, rg).get_counts() for rg in regs}
    return per


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [("live", e) for e in ERRORS] + [("destr", e) for e in ERRORS]
    builds = [circuit_live(e) if k == "live" else circuit_destructive(e) for k, e in order]
    circuits = [transpile(qc, backend=backend, optimization_level=1, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)} (mid-circuit measure + if_test)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp240_live_syndrome_manifest.json")
    man = {"exp": 240, "slug": "live_syndrome", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "prereg": {"G1_live_preserves": "<X-bar> live - destructive >= 0.50 over error cases",
                      "G2_syndrome_learns": "mid-circuit (a1,a2) matches injected error >= 0.75",
                      "registered_verdict": "G1 and G2",
                      "scope": "3-qubit bit-flip code, single live round, first non-destructive syndrome "
                               "extraction + feed-forward; buildable primitive for repeated-round QEC"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp240_live_syndrome_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    print(f"Exp240 THE LIVE SYNDROME decode | job {man['job_id']}")
    live_x, destr_x, syn_rates = {}, {}, {}
    for idx, (k, e) in enumerate([tuple(o) for o in man["order"]]):
        r0 = res[idx]
        xb = _xbar(getattr(r0.data, "out").get_counts())
        if k == "live":
            live_x[e] = xb
            syn_rates[e] = _syn_match(getattr(r0.data, "syn").get_counts(), e)
        else:
            destr_x[e] = xb
    print("  err  | <X-bar> live  destructive   advantage | syndrome-match")
    advs = []
    for e in ERRORS:
        adv = live_x[e] - destr_x[e]
        if e != "none": advs.append(adv)
        print(f"  {e:>4} |   {live_x[e]:+.3f}      {destr_x[e]:+.3f}      {adv:+.3f}  |   {syn_rates[e]:.3f}")
    mean_adv = float(np.mean(advs))
    err_syn = float(np.mean([syn_rates[e] for e in ("0", "1", "2")]))
    g1 = mean_adv >= 0.50
    g2 = err_syn >= 0.75
    print(f"\n  mean advantage (error cases) {mean_adv:+.3f} | mean syndrome-match (errors) {err_syn:.3f}")
    print(f"G1 LIVE PRESERVES: <X-bar> live-destructive = {mean_adv:+.3f} >= 0.50 {'OK' if g1 else 'MISS'}")
    print(f"G2 SYNDROME LEARNS: syndrome-match = {err_syn:.3f} >= 0.75 {'OK' if g2 else 'MISS'}")
    ok = g1 and g2
    win = ("THE LIVE SYNDROME — non-destructive parity-ancilla extraction learns WHICH qubit flipped "
           "without measuring the data, so the logical superposition SURVIVES (<X-bar> live stays high "
           "where a direct data read collapses it to ~0), and a classical feed-forward corrects it in one "
           "live pass. The campaign's first non-destructive syndrome extraction — the primitive repeated-"
           "round QEC and every logical gate build on, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "live_xbar": live_x, "destructive_xbar": destr_x,
               "syndrome_match": syn_rates, "mean_advantage": mean_adv, "mean_syndrome_match": err_syn,
               "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp240_live_syndrome_decode.json"), "w"), indent=1)
    print("-> results/exp240_live_syndrome_decode.json")


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
