#!/usr/bin/env python3
"""Exp224 — INDEFINITE NETWORK TOPOLOGY: the subspace relay in superposition. C4911.

Horizons-5 P8 (a "boldly-go" leap). F89 proved indefinite operation ORDER is a resource beating
any definite order. The network routes messages through DEFINITE paths. This flight puts the ROUTE
itself in superposition — a message processed by a coherent superposition of two relay stations —
and asks the F89 question one level up: does indefinite ROUTING beat any definite path AND any
classical mixture of paths?

A control qubit c decides which of two relays processes the message target t; superposing c
(the switch machinery, F75/exp208) makes the routing indefinite. The order-coherence witness DISC
= <Xbar_c>_commute - <Xbar_c>_anticommute (~+2 for coherent indefinite routing, ~0 for definite)
reads whether the routing carries a genuine coherence resource. THREE arms:
  COHERENT (c=|+>): indefinite routing — DISC ~ 2 (the resource is live).
  DEFINITE (route fixed, ops applied unconditionally, c spectator): DISC ~ 0 (a single path).
  DECOHERED (c dephased by an eavesdropping ancilla BEFORE routing = a CLASSICAL MIXTURE of the
    two routes): DISC ~ 0 — the NEW resource-separation null. Using both relays incoherently buys
    nothing; the resource is the routing COHERENCE, not the two-relay-ness (F89 move on topology).

Relays A,B are logical-algebra Paulis: commute (A=B=X) vs anticommute (A=X,B=Z), the same algebra
that drives the switch. Bare (physical target) — the point is the routing resource, not the shield.

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_ROUTING_COHERENCE: DISC_coherent >= 1.0 at >= 5 sigma (a real fraction of the noiseless 2) —
     indefinite routing is a coherent resource.
  G2_DEFINITE_NULL: |DISC_definite| <= 0.20 — a definite path carries no routing-coherence signal.
  G3_MIXTURE_NULL: |DISC_decohered| <= 0.20 — a classical mixture of routes carries no signal
     either; coherent routing BEATS the mixture. (The resource is coherence, not using two relays.)
  G4_SEPARATION (reported): DISC_coherent - max(|DISC_definite|,|DISC_decohered|) — the routing
     advantage over both definite AND mixed paths.
  Registered verdict = G1 and G2 and G3.
SCOPE: bare (physical) control + target + one eavesdropper ancilla for the decohered arm; the
  switch/DISC machinery (F75/F77/exp208) reframed from indefinite ORDER to indefinite ROUTING, plus
  the classical-mixture-of-paths null (new — the F89 resource separation applied to network
  topology). Textbook coherently-controlled channels (Abbott/Wechs/Branciard; Chiribella-
  Kristjansson superposition-of-paths) + the campaign's switch; contribution = indefinite routing
  witnessed as a resource over definite AND mixed routing, on silicon. KILL K1: depth over band.
BUDGET CHECK (C4887): DISC_bare ~2 ideal, hardware haircut -> ~1.5-1.9; G1 needs only 1.0.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

PAIRS = {"commute": ("X", "X"), "anti": ("X", "Z")}
ARMS = ("coherent", "definite", "decohered")


def _ctrl(qc, gate, c, t, cstate):
    """apply relay operation `gate` to target t, controlled on c == cstate (exp208 _ctrl_phys)."""
    if cstate == 0: qc.x(c)
    if gate == "X": qc.cx(c, t)
    elif gate == "Z": qc.cz(c, t)
    if cstate == 0: qc.x(c)


def circuit(arm, A, B):
    """control c=q0 (route), target/message t=q1, eavesdropper ancilla=q2 (decohered arm only)."""
    qc = QuantumCircuit(3, 1)
    qc.h(0)                                          # control |+> — superposed route
    if arm == "decohered":
        qc.cx(0, 2)                                  # ancilla eavesdrops the route -> c dephased
    qc.barrier()
    if arm == "definite":
        for g in (A, B):                             # ops applied unconditionally (single path)
            if g == "X": qc.x(1)
            elif g == "Z": qc.z(1)
    else:                                            # coherent OR decohered: routed by c
        _ctrl(qc, A, 0, 1, 0); _ctrl(qc, B, 0, 1, 1)
        qc.barrier()
        _ctrl(qc, B, 0, 1, 0); _ctrl(qc, A, 0, 1, 1)
    qc.barrier()
    qc.h(0); qc.measure(0, 0)                         # control X-readout
    return qc


def _xc(counts):
    c = tot = 0
    for s, n in counts.items():
        c += (1 - 2 * int(s.replace(" ", "")[-1])) * n; tot += n
    return c / tot, tot


def _disc(get, arm):
    xc_c, n1 = get(arm, "commute"); xc_a, n2 = get(arm, "anti")
    return xc_c - xc_a, (xc_c, xc_a), min(n1, n2)


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 100000; cache = {}
    def get(arm, pair):
        k = (arm, pair)
        if k not in cache:
            A, B = PAIRS[pair]
            cache[k] = _xc(sim.run(circuit(arm, A, B), shots=shots).result().get_counts())
        return cache[k]
    print("Exp224 selftest | INDEFINITE NETWORK TOPOLOGY — the subspace relay in superposition")
    discs = {}
    for arm in ARMS:
        d, (xc_c, xc_a), _ = _disc(get, arm)
        discs[arm] = d
        print(f"  {arm:10s}: <Xc>_commute={xc_c:+.3f} <Xc>_anti={xc_a:+.3f}  DISC={d:+.3f}")
    assert discs["coherent"] > 1.9, "coherent indefinite routing must give DISC ~ 2"
    assert abs(discs["definite"]) < 0.1, "definite route null"
    assert abs(discs["decohered"]) < 0.1, "classical-mixture-of-routes null"
    sep = discs["coherent"] - max(abs(discs["definite"]), abs(discs["decohered"]))
    print(f"  SEPARATION: DISC_coherent - max(nulls) = {sep:+.3f}")
    print("SELFTEST PASS: coherent superposed routing carries DISC~2; a definite path AND a classical "
          "mixture of paths both carry ~0. Indefinite routing is a resource beyond definite and mixed "
          "topology. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [(arm, pair) for arm in ARMS for pair in ("commute", "anti")]
    builds = [circuit(arm, *PAIRS[pair]) for (arm, pair) in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp224_indefinite_routing_manifest.json")
    man = {"exp": 224, "slug": "indefinite_routing", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "prereg": {"G1_routing_coherence": "DISC_coherent >= 1.0 at >=5 sigma",
                      "G2_definite_null": "|DISC_definite| <= 0.20",
                      "G3_mixture_null": "|DISC_decohered| <= 0.20 (coherent beats classical mixture of routes)",
                      "G4_separation": "reported: DISC_coherent - max(nulls)",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "indefinite routing (switch/DISC reframed to topology) + classical-"
                               "mixture-of-paths null (F89 resource separation); bare physical target"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp224_indefinite_routing_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (arm, pair) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, pair)] = getattr(r0.data, reg).get_counts()
    def get(arm, pair): return _xc(raw[(arm, pair)])
    print(f"Exp224 INDEFINITE NETWORK TOPOLOGY decode | job {man['job_id']}")
    discs = {}; ses = {}
    for arm in ARMS:
        d, (xc_c, xc_a), nn = _disc(get, arm)
        se = float(np.sqrt((1 - xc_c ** 2) / nn + (1 - xc_a ** 2) / nn))
        discs[arm] = d; ses[arm] = se
        print(f"  {arm:10s}: <Xc>_commute={xc_c:+.3f} <Xc>_anti={xc_a:+.3f}  DISC={d:+.3f} ± {se:.3f}")
    g1 = discs["coherent"] >= 1.0 and discs["coherent"] / ses["coherent"] >= 5
    g2 = abs(discs["definite"]) <= 0.20
    g3 = abs(discs["decohered"]) <= 0.20
    sep = discs["coherent"] - max(abs(discs["definite"]), abs(discs["decohered"]))
    print(f"\nG1 ROUTING COHERENCE: DISC_coherent={discs['coherent']:.3f} ({discs['coherent']/ses['coherent']:.0f}s) {'OK' if g1 else 'MISS'}")
    print(f"G2 DEFINITE NULL: |DISC_definite|={abs(discs['definite']):.3f} (<=0.20) {'OK' if g2 else 'MISS'}")
    print(f"G3 MIXTURE NULL: |DISC_decohered|={abs(discs['decohered']):.3f} (<=0.20) {'OK' if g3 else 'MISS'}")
    print(f"G4 SEPARATION: DISC_coherent - max(nulls) = {sep:+.3f} (routing beats definite AND mixed)")
    ok = g1 and g2 and g3
    win = ("INDEFINITE NETWORK TOPOLOGY — a message processed by a coherent superposition of two "
           "relay stations carries a routing-coherence resource (DISC~2) that neither a definite "
           "path nor a classical mixture of paths can carry (~0). Indefinite routing beats definite "
           "AND mixed topology — the first superposed network route, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "DISC": discs, "separation": sep,
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp224_indefinite_routing_decode.json"), "w"), indent=1)
    print("-> results/exp224_indefinite_routing_decode.json")


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
