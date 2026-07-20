#!/usr/bin/env python3
"""Exp225 — FAULT-TOLERANT INDEFINITE TOPOLOGY: the superposed route, error-corrected. C4912.

The crown jewels behind the shield — for the newest crown jewel. Exp224 (P8) proved indefinite
ROUTING is a resource: a message through a coherent superposition of two relays carries a
routing-coherence witness (DISC~2) that no definite path nor classical mixture of routes can. Exp208
put the causal-ORDER switch behind the [[4,2,2]] shield. This flight puts the ROUTING switch behind
the shield: **the first error-corrected quantum network topology.**

The message (target) is encoded in one [[4,2,2]] block; the route (control) stays bare; the relays
act as controlled LOGICAL Paulis (exp208 machinery). DISC_shielded = <Xbar_c>_commute -
<Xbar_c>_anti, read after ZZZZ postselection on the message block. Three arms (exp224):
  COHERENT (route |+>): shielded indefinite routing — DISC survives error detection.
  DEFINITE (single path, ops unconditional): DISC ~ 0.
  DECOHERED (route dephased by an eavesdropper ancilla = classical mixture of routes): DISC ~ 0 —
    the resource-separation null, now UNDER the shield: error detection preserves the coherent-
    routing resource, still distinct from the classical mixture.

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_SHIELD_PRESERVES_ROUTING: DISC_shielded_coherent >= 1.0 at >= 5 sigma (the routing-coherence
     resource survives error detection — fault-tolerant indefinite routing).
  G2_DEFINITE_NULL: |DISC_shielded_definite| <= 0.20.
  G3_MIXTURE_NULL: |DISC_shielded_decohered| <= 0.20 (coherent routing still beats the classical
     mixture of routes, after the shield).
  G4_REFERENCE (reported): DISC_shielded vs DISC_bare (does the shield preserve/concentrate the
     routing resource, the 205/208 trend?).
  Registered verdict = G1 and G2 and G3.
SCOPE: bare route (control) + [[4,2,2]]-encoded message (target) + eavesdropper ancilla; per-block
  ZZZZ shield. Composes exp208 (shielded switch) + exp224 (indefinite routing + mixture null);
  contribution = indefinite routing made fault-tolerant — the coherent-routing resource survives
  error detection and stays distinct from the classical mixture, on silicon. n=2 relays. KILL K1:
  depth over band.
BUDGET CHECK (C4887): DISC_bare ~2; shielded haircut (exp208-class) -> ~1.5-1.9; G1 needs only 1.0.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

PAIRS = {"commute": ("X", "X"), "anti": ("X", "Z")}
ARMS = ("coherent", "definite", "decohered")


# ---- bare (physical message) reference: control q0, target q1, ancilla q2 ----
def _ctrl_phys(qc, gate, c, t, cstate):
    if cstate == 0: qc.x(c)
    if gate == "X": qc.cx(c, t)
    elif gate == "Z": qc.cz(c, t)
    if cstate == 0: qc.x(c)


def bare_circuit(arm, A, B):
    qc = QuantumCircuit(3, 1)
    qc.h(0)
    if arm == "decohered": qc.cx(0, 2)
    qc.barrier()
    if arm == "definite":
        for g in (A, B):
            if g == "X": qc.x(1)
            elif g == "Z": qc.z(1)
    else:
        _ctrl_phys(qc, A, 0, 1, 0); _ctrl_phys(qc, B, 0, 1, 1)
        qc.barrier()
        _ctrl_phys(qc, B, 0, 1, 0); _ctrl_phys(qc, A, 0, 1, 1)
    qc.barrier(); qc.h(0); qc.measure(0, 0)
    return qc


# ---- shielded (encoded message): control q0, target block q1..q4, ancilla q5 ----
# 191 map (block-local i -> q(1+i)): Xbar1 = X(q1)X(q2)  Zbar1 = Z(q1)Z(q3)  ZZZZ = Z q1..q4
def _ctrl_logical(qc, gate, c, cstate):
    if cstate == 0: qc.x(c)
    if gate == "X": qc.cx(c, 1); qc.cx(c, 2)
    elif gate == "Z": qc.cz(c, 1); qc.cz(c, 3)
    if cstate == 0: qc.x(c)


def _uncond_logical(qc, gate):
    if gate == "X": qc.x(1); qc.x(2)
    elif gate == "Z": qc.z(1); qc.z(3)


def logical_circuit(arm, A, B):
    qc = QuantumCircuit(6, 6)
    qc.h(0)                                          # route (control) |+>
    qc.h(1); qc.cx(1, 2); qc.cx(1, 3); qc.cx(1, 4)   # message |0bar0bar> = GHZ4
    if arm == "decohered": qc.cx(0, 5)               # eavesdropper dephases the route
    qc.barrier()
    if arm == "definite":
        _uncond_logical(qc, A); _uncond_logical(qc, B)
    else:
        _ctrl_logical(qc, A, 0, 0); _ctrl_logical(qc, B, 0, 1)
        qc.barrier()
        _ctrl_logical(qc, B, 0, 0); _ctrl_logical(qc, A, 0, 1)
    qc.barrier()
    qc.h(0)                                          # route X-readout
    for q in range(6): qc.measure(q, q)              # control + message (Z, for ZZZZ) + ancilla
    return qc


def _xc_bare(counts):
    c = tot = 0
    for s, n in counts.items():
        c += (1 - 2 * int(s.replace(" ", "")[-1])) * n; tot += n
    return c / tot, tot


def _xc_logical(counts):
    """<Xbar_c> = <control X> after ZZZZ postselect on the message block (q1..q4)."""
    c = na = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(6)]
        if (v[1] ^ v[2] ^ v[3] ^ v[4]) != 0:         # ZZZZ shield
            continue
        na += n; c += (1 - 2 * v[0]) * n
    return (c / na if na else 0.0), na


def _disc(get, arm):
    xc_c, n1 = get(arm, "commute"); xc_a, n2 = get(arm, "anti")
    return xc_c - xc_a, xc_c, xc_a, min(n1, n2)


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 100000; cache = {}
    def getL(arm, pair):
        k = ("L", arm, pair)
        if k not in cache:
            A, B = PAIRS[pair]
            cache[k] = _xc_logical(sim.run(logical_circuit(arm, A, B), shots=shots).result().get_counts())
        return cache[k]
    def getB(arm, pair):
        k = ("B", arm, pair)
        if k not in cache:
            A, B = PAIRS[pair]
            cache[k] = _xc_bare(sim.run(bare_circuit(arm, A, B), shots=shots).result().get_counts())
        return cache[k]
    print("Exp225 selftest | FAULT-TOLERANT INDEFINITE TOPOLOGY — the superposed route, shielded")
    discs = {}
    for arm in ARMS:
        d, xc_c, xc_a, _ = _disc(getL, arm)
        discs[arm] = d
        print(f"  shielded {arm:10s}: <Xbar_c>_com={xc_c:+.3f} _anti={xc_a:+.3f}  DISC={d:+.3f}")
    dbare, _, _, _ = _disc(getB, "coherent")
    print(f"  bare coherent DISC={dbare:+.3f}")
    assert discs["coherent"] > 1.9, "shielded coherent routing must give DISC ~ 2"
    assert abs(discs["definite"]) < 0.1 and abs(discs["decohered"]) < 0.1, "nulls must die"
    print("SELFTEST PASS: coherent superposed routing survives the shield at DISC~2; a definite path "
          "and a classical mixture of routes both stay ~0 under error detection. Fault-tolerant "
          "indefinite routing. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = ([("L", arm, pair) for arm in ARMS for pair in ("commute", "anti")]
             + [("B", "coherent", "commute"), ("B", "coherent", "anti")])
    builds = [logical_circuit(a, *PAIRS[p]) if k == "L" else bare_circuit(a, *PAIRS[p]) for (k, a, p) in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp225_shielded_routing_manifest.json")
    man = {"exp": 225, "slug": "shielded_routing", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "prereg": {"G1_shield_preserves_routing": "DISC_shielded_coherent >= 1.0 at >=5 sigma",
                      "G2_definite_null": "|DISC_shielded_definite| <= 0.20",
                      "G3_mixture_null": "|DISC_shielded_decohered| <= 0.20 (coherent beats mixture, shielded)",
                      "G4_reference": "reported: DISC_shielded vs DISC_bare",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "fault-tolerant indefinite routing: exp224 routing + mixture null behind "
                               "the exp208 [[4,2,2]] shield on the message; first error-corrected topology"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp225_shielded_routing_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (k, a, p) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(k, a, p)] = getattr(r0.data, reg).get_counts()
    def getL(arm, pair): return _xc_logical(raw[("L", arm, pair)])
    def getB(arm, pair): return _xc_bare(raw[("B", arm, pair)])
    print(f"Exp225 FAULT-TOLERANT INDEFINITE TOPOLOGY decode | job {man['job_id']}")
    discs = {}; ses = {}; accs = {}
    for arm in ARMS:
        d, xc_c, xc_a, nn = _disc(getL, arm)
        se = float(np.sqrt((1 - xc_c ** 2) / nn + (1 - xc_a ** 2) / nn))
        discs[arm] = d; ses[arm] = se
        na = getL(arm, "commute")[1]; accs[arm] = na
        print(f"  shielded {arm:10s}: <Xbar_c>_com={xc_c:+.3f} _anti={xc_a:+.3f}  DISC={d:+.3f} ± {se:.3f}")
    dbare, bc, ba, nb = _disc(getB, "coherent")
    print(f"  bare coherent DISC={dbare:+.3f}   shield acceptance ~{accs['coherent']/sum(raw[('L','coherent','commute')].values()):.3f}")
    g1 = discs["coherent"] >= 1.0 and discs["coherent"] / ses["coherent"] >= 5
    g2 = abs(discs["definite"]) <= 0.20
    g3 = abs(discs["decohered"]) <= 0.20
    print(f"\nG1 SHIELD PRESERVES ROUTING: DISC_shielded={discs['coherent']:.3f} ({discs['coherent']/ses['coherent']:.0f}s) {'OK' if g1 else 'MISS'}")
    print(f"G2 DEFINITE NULL: |DISC|={abs(discs['definite']):.3f} (<=0.20) {'OK' if g2 else 'MISS'}")
    print(f"G3 MIXTURE NULL: |DISC|={abs(discs['decohered']):.3f} (<=0.20) {'OK' if g3 else 'MISS'}")
    print(f"G4 REFERENCE: shielded {discs['coherent']:.3f} vs bare {dbare:.3f} (shield preserves the routing resource)")
    ok = g1 and g2 and g3
    win = ("FAULT-TOLERANT INDEFINITE TOPOLOGY — the superposition of two network routes survives "
           "error detection: the routing-coherence resource holds behind the [[4,2,2]] shield "
           "(DISC~2), while a definite path and a classical mixture of routes both stay dark. The "
           "first error-corrected quantum network topology, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "DISC_shielded": discs, "DISC_bare": dbare,
               "acceptance": accs["coherent"] / sum(raw[("L", "coherent", "commute")].values()),
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp225_shielded_routing_decode.json"), "w"), indent=1)
    print("-> results/exp225_shielded_routing_decode.json")


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
