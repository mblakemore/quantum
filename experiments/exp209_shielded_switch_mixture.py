#!/usr/bin/env python3
"""Exp209 — THE SHIELDED SWITCH vs THE CLASSICAL MIXTURE: closing the loophole. C4905.

Horizons-5 P1, flight 2 (successor to Exp208), on the standing go. Exp208 certified that the
causal witness survives error detection — but only vs a PURE definite order (the W3 null). The
strong adversary, the one F77 closed for the BARE switch, is a CLASSICAL MIXTURE of the two
orders — a device that flips a coin each shot. This flight closes that loophole for the
SHIELDED switch: does fault-tolerant indefinite causal order beat not just one fixed order but
ANY causally-separable strategy?

The mixture (F73/F77 move): decohere the control's order-coherence by copying its value to a
junk ancilla between the two switch halves (CX(control, ancilla), ancilla traced out). The
circuit still LOOKS like a switch (same target ops, comparable depth) but the order is now a
classical coin-flip -> the witness must go inert. Inertness tracks causal separability, not
circuit structure or depth (F77's lesson).

Apparatus: Exp208 verbatim (control bare, target [[4,2,2]] logical, ops = logical Paulis
Xbar1/Zbar1, ZZZZ postselect) + a mixture arm that adds the decohering CX.

Arms x kinds x pairs (12 circuits):
  bare    {switch, mixture} x {commute, anti}   -> DISC_bare_switch (ref), DISC_bare_mixture
  logical {switch, mixture} x {commute, anti}   -> DISC_log_switch, DISC_log_mixture
  (definite-order null inherited from 208; here the tougher mixture adversary is the headline)

FROZEN GATES:
  W1_MIXTURE_INERT: |DISC_logical_mixture| <= 0.15 AND |DISC_bare_mixture| <= 0.15 (the
     classical mixture cannot witness order, shielded or not).
  W2_SWITCH_BEATS_MIXTURE: DISC_logical_switch - DISC_logical_mixture >= 0.5*DISC_bare_switch
     at >=5 sigma (the shielded switch strictly exceeds ANY classical mixture of orders).
  W3_SWITCH_ALIVE: DISC_logical_switch > 1.0 at >=5 sigma (reproduces 208's ~1.71 in-window).
  W4_DEPTH_DECORRELATION (reported): the mixture arm is >=depth of the switch arm yet inert -
     inertness tracks separability, not depth (F77).
  G_ACC: target ZZZZ acceptance >= 0.55 both arms.
Registered verdict = W1 and W2 and W3 and G_acc.
SCOPE: coherence-of-causal-order witness (F77), half-shielded target, single-syndrome partial
shield (inherited from 208). Closes the causal-separability loophole for the shielded switch on
silicon, same-window switch-vs-mixture (the F77 move, one level up into the code).
BUDGET CHECK (C4887): 208 measured DISC_log_switch 1.71; mixture -> ~0. W2 margin ~1.7 vs 0.5x
bar ~0.98. Ample. Filed: DISC_log_switch in [1.4,1.9]; |DISC_mixture| < 0.12; acceptance
in [0.65,0.90].
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ARMS = ("bare", "logical")
KINDS = ("switch", "mixture")
PAIRS = {"commute": ("X", "X"), "anti": ("X", "Z")}


def _ctrl_phys(qc, gate, c, t, cstate):
    if cstate == 0: qc.x(c)
    if gate == "X": qc.cx(c, t)
    elif gate == "Z": qc.cz(c, t)
    if cstate == 0: qc.x(c)


def bare_circuit(A, B, mixture):
    """control q0, target q1, mixture ancilla q2. Switch of A,B routed by control."""
    n = 3 if mixture else 2
    qc = QuantumCircuit(n, 1)
    qc.h(0)
    _ctrl_phys(qc, A, 0, 1, 0); _ctrl_phys(qc, B, 0, 1, 1)
    if mixture:
        qc.cx(0, 2)                            # decohere control's order-coherence (traced out)
    qc.barrier()
    _ctrl_phys(qc, B, 0, 1, 0); _ctrl_phys(qc, A, 0, 1, 1)
    qc.barrier(); qc.h(0); qc.measure(0, 0)
    return qc


def _ctrl_logical(qc, gate, c, cstate):
    if cstate == 0: qc.x(c)
    if gate == "X": qc.cx(c, 1); qc.cx(c, 2)
    elif gate == "Z": qc.cz(c, 1); qc.cz(c, 3)
    if cstate == 0: qc.x(c)


def logical_circuit(A, B, mixture):
    """control q0 (bare), target [[4,2,2]] q1-4, mixture ancilla q5."""
    n = 6 if mixture else 5
    qc = QuantumCircuit(n, 5)
    qc.h(0)
    qc.h(1); qc.cx(1, 2); qc.cx(1, 3); qc.cx(1, 4)   # target |0bar0bar>
    qc.barrier()
    _ctrl_logical(qc, A, 0, 0); _ctrl_logical(qc, B, 0, 1)
    if mixture:
        qc.cx(0, 5)                            # decohere control (traced out)
    qc.barrier()
    _ctrl_logical(qc, B, 0, 0); _ctrl_logical(qc, A, 0, 1)
    qc.barrier(); qc.h(0)
    for q in range(5): qc.measure(q, q)        # control (X) + target (Z) for ZZZZ
    return qc


def _xc_bare(counts):
    c = tot = 0
    for s, n in counts.items():
        c += (1 - 2 * int(s.replace(" ", "")[-1])) * n; tot += n
    return c / tot, tot


def _xc_logical(counts):
    acc = c = rej = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(5)]
        if v[1] ^ v[2] ^ v[3] ^ v[4]:
            rej += n; continue
        acc += n; c += (1 - 2 * v[0]) * n
    tot = acc + rej
    return (c / acc if acc else 0.0), acc, tot


def analyze(get):
    r = {}
    for kind in KINDS:
        for pair in PAIRS:
            xb, nb = _xc_bare(get("bare", kind, pair))
            xl, na, nt = _xc_logical(get("logical", kind, pair))
            r[("bare", kind, pair)] = {"xc": xb, "n": nb}
            r[("logical", kind, pair)] = {"xc": xl, "n_acc": na, "n": nt,
                                          "acceptance": na / nt if nt else 0.0}
    return r


def _disc(r, arm, kind):
    return r[(arm, kind, "commute")]["xc"] - r[(arm, kind, "anti")]["xc"]


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000; cache = {}
    def get(arm, kind, pair):
        k = (arm, kind, pair)
        if k not in cache:
            A, B = PAIRS[pair]
            qc = bare_circuit(A, B, kind == "mixture") if arm == "bare" \
                else logical_circuit(A, B, kind == "mixture")
            cache[k] = sim.run(qc, shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    ds_b = _disc(r, "bare", "switch"); dm_b = _disc(r, "bare", "mixture")
    ds_l = _disc(r, "logical", "switch"); dm_l = _disc(r, "logical", "mixture")
    print("Exp209 selftest (noiseless) | switch DISC ~ +2, MIXTURE ~ 0 (both arms)")
    print(f"  bare:    switch={ds_b:+.4f}  mixture={dm_b:+.4f}")
    print(f"  logical: switch={ds_l:+.4f}  mixture={dm_l:+.4f}  "
          f"acc={r[('logical','switch','commute')]['acceptance']:.3f}")
    assert abs(ds_b - 2) < 0.05 and abs(ds_l - 2) < 0.05, "switch must witness ~+2 both arms"
    assert abs(dm_b) < 0.05 and abs(dm_l) < 0.05, "classical mixture must be INERT (~0) both arms"
    for pair in PAIRS:
        assert abs(r[("logical", "switch", pair)]["acceptance"] - 1) < 0.02
    print("SELFTEST PASS: the shielded switch witnesses order (~+2) while the classical mixture "
          "of orders is inert (~0) — even with the target encoded and post-selected. The "
          "decohering CX kills the order-coherence; inertness tracks causal separability. "
          "Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names, builds = [], []
    for arm in ARMS:
        for kind in KINDS:
            for pair in PAIRS:
                A, B = PAIRS[pair]
                qc = bare_circuit(A, B, kind == "mixture") if arm == "bare" \
                    else logical_circuit(A, B, kind == "mixture")
                names.append([arm, kind, pair]); builds.append(qc)
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0)
                for qc in builds]
    n2 = {f"{a}_{k}": sum(1 for inst in c.data if inst.operation.num_qubits == 2)
          for (a, k, p), c in zip(names, circuits) if p == "commute"}
    print(f"  2q counts (commute reps): {n2}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp209_shielded_switch_mixture_manifest.json")
    man = {"exp": 209, "slug": "shielded_switch_mixture", "backend": backend_name,
           "shots": shots, "job_id": job.job_id(), "order": names, "n2": n2}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "W1_mixture_inert": "|DISC_logical_mixture| <= 0.15 AND |DISC_bare_mixture| <= 0.15",
        "W2_switch_beats_mixture": "DISC_logical_switch - DISC_logical_mixture >= "
                                   "0.5*DISC_bare_switch at >=5 sigma",
        "W3_switch_alive": "DISC_logical_switch > 1.0 at >=5 sigma",
        "W4_depth_decorrelation": "mixture arm >= switch depth yet inert (reported, F77)",
        "G_acc": "target ZZZZ acceptance >= 0.55 both arms",
        "registered_verdict": "W1 and W2 and W3 and G_acc",
        "scope": "coherence-of-causal-order witness (F77), half-shielded, single-syndrome; "
                 "closes causal-separability loophole for the shielded switch, same-window",
        "budget_predictions": "DISC_log_switch in [1.4,1.9]; |DISC_mixture| < 0.12; "
                              "acceptance in [0.65,0.90]"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp209_shielded_switch_mixture_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, (arm, kind, pair) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, kind, pair)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda a, k, p: raw[(a, k, p)])
    ds_b = _disc(r, "bare", "switch"); dm_b = _disc(r, "bare", "mixture")
    ds_l = _disc(r, "logical", "switch"); dm_l = _disc(r, "logical", "mixture")
    se = 1 / np.sqrt(shots)
    na = min(r[("logical", "switch", "commute")]["n_acc"], r[("logical", "switch", "anti")]["n_acc"])
    nam = min(r[("logical", "mixture", "commute")]["n_acc"], r[("logical", "mixture", "anti")]["n_acc"])
    se_ls = np.sqrt(2) / np.sqrt(max(na, 1)); se_lm = np.sqrt(2) / np.sqrt(max(nam, 1))
    se_bs = se * np.sqrt(2)
    acc = np.mean([r[("logical", k, p)]["acceptance"] for k in KINDS for p in PAIRS])
    diff = ds_l - dm_l
    z_w2 = (diff - 0.5 * ds_b) / np.sqrt(se_ls ** 2 + se_lm ** 2 + 0.25 * se_bs ** 2)
    z_w3 = (ds_l - 1.0) / se_ls
    print(f"Exp209 THE SHIELDED SWITCH vs THE CLASSICAL MIXTURE decode | job {man['job_id']}")
    print(f"  bare:    switch DISC={ds_b:+.4f}  mixture DISC={dm_b:+.4f}")
    print(f"  logical: switch DISC={ds_l:+.4f} (se {se_ls:.3f})  mixture DISC={dm_l:+.4f} "
          f"(se {se_lm:.3f})  acceptance={acc:.3f}")
    w1 = abs(dm_l) <= 0.15 and abs(dm_b) <= 0.15
    w2 = diff >= 0.5 * ds_b and z_w2 >= 5
    w3 = ds_l > 1.0 and z_w3 >= 5
    gacc = acc >= 0.55
    print(f"\nW1 MIXTURE INERT: log-mix {dm_l:+.3f}, bare-mix {dm_b:+.3f} {'OK' if w1 else 'MISS'}")
    print(f"W2 SWITCH BEATS MIXTURE: DISC_log switch-mix = {diff:+.3f} vs 0.5*bar {0.5*ds_b:.3f} "
          f"({z_w2:.1f} sigma) {'OK' if w2 else 'MISS'}")
    print(f"W3 SWITCH ALIVE: DISC_log_switch {ds_l:.3f} > 1.0 ({z_w3:.1f} sigma) {'OK' if w3 else 'MISS'}")
    print(f"G_ACC: acceptance {acc:.3f} {'OK' if gacc else 'MISS'}")
    ok = w1 and w2 and w3 and gacc
    win = ("THE SHIELDED SWITCH BEATS THE CLASSICAL MIXTURE — fault-tolerant indefinite causal "
           "order strictly exceeds ANY causally-separable strategy: the shielded witness fires "
           "while the classical coin-flip of orders is inert, target error-detected. The F77 "
           "loophole closed one level up, in the code")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "DISC_bare_switch": float(ds_b), "DISC_bare_mixture": float(dm_b),
               "DISC_logical_switch": float(ds_l), "DISC_logical_mixture": float(dm_l),
               "switch_minus_mixture": float(diff), "acceptance": float(acc),
               "sigma_w2": float(z_w2), "sigma_w3": float(z_w3),
               "w1": bool(w1), "w2": bool(w2), "w3": bool(w3), "g_acc": bool(gacc),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp209_shielded_switch_mixture_decode.json"), "w"), indent=1)
    print("-> results/exp209_shielded_switch_mixture_decode.json")


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
