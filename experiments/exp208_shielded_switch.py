#!/usr/bin/env python3
"""Exp208 — THE SHIELDED SWITCH: does the causal witness survive error detection? C4905.

Horizons-5 P1, flight 1 (docs/star-trek-horizons-5-the-five-year-mission-whisper-c4905.md),
on Creator directive ("fly priority #1"). The composition nobody has done: put the campaign's
crown jewel (indefinite causal order, F73-F82) BEHIND the campaign's shield ([[4,2,2]], F191+).

STAGED FIRST FLIGHT (half-shielded, per the roadmap): the switch's TARGET is encoded in one
[[4,2,2]] logical qubit; the CONTROL stays bare. The target operations A,B become LOGICAL
Paulis (Xbar1 = X0X1, Zbar1 = Z0Z2 in the 191 map) — which obey the SAME commutation algebra
as physical X,Z, so the witness structure is preserved at the logical level. Post-select on the
target block's ZZZZ stabilizer (single-syndrome partial shield, catches X-type errors — stated).

Why the target measurement doesn't disturb the witness: at the end of the switch, control and
target are UNENTANGLED — the commutator phase is kicked back onto the control, the target
disentangles (this is why the bare witness reads the control alone). So measuring the target for
its syndrome is compatible with reading the control's X-coherence.

Witness (exp91/F75 machinery): control c in |+>, 4 controlled gates route the order; read c in
X. COMMUTE (A=B=X) -> c stays |+> -> <Xc>=+1; ANTICOMMUTE (A=X,B=Z, XZ=-ZX) -> c->|-> ->
<Xc>=-1. DISC = <Xc>_commute - <Xc>_anticommute (switch ~+2 noiseless; definite-order ~0).

Arms x pairs (8 circuits): {bare, logical} x {switch, definite} x is folded into commute/
anticommute settings.
  bare      2q: control + physical target (exp91 verbatim) -> DISC_bare (reference)
  logical   5q: control + [[4,2,2]] target, controlled logical Paulis, ZZZZ postselect
  definite  arms: target ops applied UNCONDITIONALLY, control spectator -> DISC ~ 0 (null)

FROZEN GATES:
  W1_SHIELD_PRESERVES: DISC_logical >= 0.5 * DISC_bare at >=5 sigma (the shield preserves the
     causal witness the way it preserved CHSH (196) and Fisher info (205)).
  W2_WITNESS_ALIVE: DISC_logical > 1.0 at >=5 sigma (a real fraction of the noiseless ~2; order-
     coherence genuinely survives postselection).
  W3_NULLS: |DISC_bare_definite| <= 0.15 AND |DISC_logical_definite| <= 0.15 (definite order
     cannot discriminate, shielded or not).
  W4_REFERENCE (reported): DISC_logical vs DISC_bare gap — does the shield preserve or improve?
  G_ACC: target block acceptance (ZZZZ even) >= 0.55.
Registered verdict = W1 and W2 and W3 and G_ACC.
SCOPE: coherence-of-causal-order witness (each gate queried twice — F77 honest scope, inherited),
NOT a black-box query separation; half-shielded (target only), single-syndrome partial shield;
expectation-value witness, logical-level postselection. If W1 holds, the natural successor is the
fully-logical witness + shielded ICO capacity activation (F83 logically).
BUDGET CHECK (C4887): DISC_bare ~2 ideal, hardware haircut -> ~1.6-1.9; W1 needs only 0.5x; the
shield's postselection recovered CHSH (196) and Fisher (205) at >0.9 contrast. Ample.
Filed: DISC_bare in [1.5,1.95]; DISC_logical in [1.3,1.9]; acceptance in [0.65,0.85].
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ARMS = ("bare", "logical")
KINDS = ("switch", "definite")
PAIRS = {"commute": ("X", "X"), "anti": ("X", "Z")}


# ---------------- bare (physical target) — exp91 verbatim ----------------

def _ctrl_phys(qc, gate, c, t, cstate):
    if cstate == 0: qc.x(c)
    if gate == "X": qc.cx(c, t)
    elif gate == "Z": qc.cz(c, t)
    if cstate == 0: qc.x(c)


def bare_circuit(A, B, definite):
    qc = QuantumCircuit(2, 1)
    qc.h(0)                                   # control |+>, target |0>
    if not definite:
        _ctrl_phys(qc, A, 0, 1, 0); _ctrl_phys(qc, B, 0, 1, 1)
        qc.barrier()
        _ctrl_phys(qc, B, 0, 1, 0); _ctrl_phys(qc, A, 0, 1, 1)
    else:
        for g in (A, B):
            if g == "X": qc.x(1)
            elif g == "Z": qc.z(1)
    qc.barrier(); qc.h(0); qc.measure(0, 0)
    return qc


# ---------------- logical (encoded target) ----------------
# control = q0 (bare). target block = q1..q4, 191 map (block-local i -> q(1+i)):
#   Xbar1 = X(q1)X(q2)   Zbar1 = Z(q1)Z(q3)   ZZZZ = Z q1..q4

def _ctrl_logical(qc, gate, c, cstate):
    """controlled logical Pauli on the target block, controlled by c==cstate."""
    if cstate == 0: qc.x(c)
    if gate == "X":
        qc.cx(c, 1); qc.cx(c, 2)              # controlled Xbar1 = c-(X0X1)
    elif gate == "Z":
        qc.cz(c, 1); qc.cz(c, 3)              # controlled Zbar1 = c-(Z0Z2)
    if cstate == 0: qc.x(c)


def _uncond_logical(qc, gate):
    if gate == "X": qc.x(1); qc.x(2)
    elif gate == "Z": qc.z(1); qc.z(3)


def logical_circuit(A, B, definite):
    qc = QuantumCircuit(5, 5)
    qc.h(0)                                   # bare control |+>
    qc.h(1); qc.cx(1, 2); qc.cx(1, 3); qc.cx(1, 4)   # target |0bar0bar> = GHZ4
    qc.barrier()
    if not definite:
        _ctrl_logical(qc, A, 0, 0); _ctrl_logical(qc, B, 0, 1)
        qc.barrier()
        _ctrl_logical(qc, B, 0, 0); _ctrl_logical(qc, A, 0, 1)
    else:
        _uncond_logical(qc, A); _uncond_logical(qc, B)
    qc.barrier()
    qc.h(0)                                   # control X-readout
    for q in range(5): qc.measure(q, q)       # control + target (Z basis) for ZZZZ check
    return qc


def _xc_bare(counts):
    c = tot = 0
    for s, n in counts.items():
        c += (1 - 2 * int(s.replace(" ", "")[-1])) * n; tot += n
    return c / tot, tot


def _xc_logical(counts):
    """Postselect target ZZZZ parity even; <Xc> from the control bit (q0)."""
    acc = c = rej = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(5)]
        par = v[1] ^ v[2] ^ v[3] ^ v[4]       # ZZZZ on target
        if par:
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
    key = lambda p: ("xc")
    xc_c = r[(arm, kind, "commute")]["xc"]; xc_a = r[(arm, kind, "anti")]["xc"]
    return xc_c - xc_a


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000; cache = {}
    def get(arm, kind, pair):
        k = (arm, kind, pair)
        if k not in cache:
            A, B = PAIRS[pair]
            qc = bare_circuit(A, B, kind == "definite") if arm == "bare" \
                else logical_circuit(A, B, kind == "definite")
            cache[k] = sim.run(qc, shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    db_s = _disc(r, "bare", "switch"); db_d = _disc(r, "bare", "definite")
    dl_s = _disc(r, "logical", "switch"); dl_d = _disc(r, "logical", "definite")
    print("Exp208 selftest (noiseless) | switch DISC ~ +2, definite ~ 0, both arms")
    print(f"  bare:    switch DISC={db_s:+.4f}  definite DISC={db_d:+.4f}")
    print(f"  logical: switch DISC={dl_s:+.4f}  definite DISC={dl_d:+.4f}  "
          f"acc={r[('logical','switch','commute')]['acceptance']:.3f}")
    assert abs(db_s - 2) < 0.05, "bare switch must witness ~+2"
    assert abs(dl_s - 2) < 0.05, "LOGICAL switch must witness ~+2 (shield preserves the witness)"
    assert abs(db_d) < 0.05 and abs(dl_d) < 0.05, "definite-order nulls must be ~0"
    for pair in PAIRS:
        assert abs(r[("logical", "switch", pair)]["acceptance"] - 1) < 0.02, "noiseless acc ~1"
    print("SELFTEST PASS: the causal witness survives encoding — logical switch DISC ~ +2 with "
          "the target in [[4,2,2]] and post-selected on ZZZZ; definite-order nulls dead; "
          "acceptance ~1 noiseless. The commutation algebra is preserved at the logical level. "
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
                qc = bare_circuit(A, B, kind == "definite") if arm == "bare" \
                    else logical_circuit(A, B, kind == "definite")
                names.append([arm, kind, pair]); builds.append(qc)
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0)
                for qc in builds]
    n2 = {f"{a}_{k}": sum(1 for inst in c.data if inst.operation.num_qubits == 2)
          for (a, k, p), c in zip(names, circuits) if p == "commute"}
    print(f"  2q counts (commute reps): {n2}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp208_shielded_switch_manifest.json")
    man = {"exp": 208, "slug": "shielded_switch", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names, "n2": n2}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "W1_shield_preserves": "DISC_logical(switch) >= 0.5*DISC_bare(switch) at >=5 sigma",
        "W2_witness_alive": "DISC_logical(switch) > 1.0 at >=5 sigma",
        "W3_nulls": "|DISC_bare(definite)| <= 0.15 AND |DISC_logical(definite)| <= 0.15",
        "W4_reference": "DISC_logical vs DISC_bare gap (reported)",
        "G_acc": "target ZZZZ acceptance >= 0.55",
        "registered_verdict": "W1 and W2 and W3 and G_acc",
        "scope": "coherence-of-causal-order witness (F77), half-shielded (target only), "
                 "single-syndrome ZZZZ partial shield",
        "budget_predictions": "DISC_bare in [1.5,1.95]; DISC_logical in [1.3,1.9]; "
                              "acceptance in [0.65,0.85]"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp208_shielded_switch_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, (arm, kind, pair) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, kind, pair)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda a, k, p: raw[(a, k, p)])
    db_s = _disc(r, "bare", "switch"); db_d = _disc(r, "bare", "definite")
    dl_s = _disc(r, "logical", "switch"); dl_d = _disc(r, "logical", "definite")
    se = 1 / np.sqrt(shots)
    na = min(r[("logical", "switch", "commute")]["n_acc"], r[("logical", "switch", "anti")]["n_acc"])
    se_l = 1 / np.sqrt(max(na, 1))
    se_db = se * np.sqrt(2); se_dl = se_l * np.sqrt(2)
    acc = np.mean([r[("logical", "switch", p)]["acceptance"] for p in PAIRS])
    z_w1 = (dl_s - 0.5 * db_s) / np.sqrt(se_dl ** 2 + 0.25 * se_db ** 2)
    z_w2 = (dl_s - 1.0) / se_dl
    print(f"Exp208 THE SHIELDED SWITCH decode | job {man['job_id']}")
    print(f"  bare:    switch DISC={db_s:+.4f} (se {se_db:.3f})  definite DISC={db_d:+.4f}")
    print(f"  logical: switch DISC={dl_s:+.4f} (se {se_dl:.3f})  definite DISC={dl_d:+.4f}  "
          f"acceptance={acc:.3f}")
    w1 = dl_s >= 0.5 * db_s and z_w1 >= 5
    w2 = dl_s > 1.0 and z_w2 >= 5
    w3 = abs(db_d) <= 0.15 and abs(dl_d) <= 0.15
    gacc = acc >= 0.55
    print(f"\nW1 SHIELD PRESERVES: DISC_log {dl_s:.3f} vs 0.5*DISC_bare {0.5*db_s:.3f} "
          f"({z_w1:.1f} sigma) {'OK' if w1 else 'MISS'}")
    print(f"W2 WITNESS ALIVE: DISC_log {dl_s:.3f} > 1.0 ({z_w2:.1f} sigma) {'OK' if w2 else 'MISS'}")
    print(f"W3 NULLS: bare-def {db_d:+.3f}, log-def {dl_d:+.3f} {'OK' if w3 else 'MISS'}")
    print(f"W4 REFERENCE: shield/bare = {dl_s/db_s if db_s else 0:.3f} "
          f"(gap {dl_s-db_s:+.3f}, descriptive)")
    print(f"G_ACC: target acceptance {acc:.3f} {'OK' if gacc else 'MISS'}")
    ok = w1 and w2 and w3 and gacc
    win = ("THE SHIELDED SWITCH — indefinite causal order survives error detection: the causal "
           "witness fires with the target encoded in a [[4,2,2]] shield and post-selected on its "
           "stabilizer. Fault-tolerant causal order, first flight")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    print("  (scope: coherence-of-causal-order witness, half-shielded target, single-syndrome "
          "partial shield)")
    json.dump({"job_id": man["job_id"],
               "DISC_bare_switch": float(db_s), "DISC_bare_definite": float(db_d),
               "DISC_logical_switch": float(dl_s), "DISC_logical_definite": float(dl_d),
               "acceptance": float(acc), "sigma_w1": float(z_w1), "sigma_w2": float(z_w2),
               "shield_over_bare": float(dl_s / db_s) if db_s else None,
               "w1": bool(w1), "w2": bool(w2), "w3": bool(w3), "g_acc": bool(gacc),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp208_shielded_switch_decode.json"), "w"), indent=1)
    print("-> results/exp208_shielded_switch_decode.json")


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
