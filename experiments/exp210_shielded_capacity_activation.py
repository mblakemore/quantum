#!/usr/bin/env python3
"""Exp210 — SHIELDED CAPACITY ACTIVATION: information through impossible channels, error-detected. C4905.

Horizons-5 P1, flight 3 (the "useful resource" successor to 208/209), on the standing go. Takes
fault-tolerant indefinite causal order from a WITNESS (does the quantumness survive? — 208/209)
to a WORKING RESOURCE: transmit information through two channels that are EACH individually
zero-capacity, with the target error-detected.

Theory (Ebler-Salek-Chiribella, PRL 120, 120502; F83 certified it bare at R_bar=0.5034, 55.6σ):
a completely depolarizing qubit channel transmits ZERO information; so does any definite-order
(or classically-mixed) composition of two of them. In the quantum switch with control |+>,
information survives — living ONLY in the control-target correlation. Exact: target|control=+ ->
(rho+2I)/5, target|control=- -> (2I-rho)/3; R_bar = 0.5333 ideal.

SHIELDED version (this flight): the TARGET is a [[4,2,2]] logical qubit (control bare). The two
depolarizing channels = full Pauli twirl over logical {Ibar, Xbar1, Ybar1, Zbar1} (Ybar1 =
Y0 X1 Z2, derived + stabilizer-verified). Post-select on the target ZZZZ stabilizer. Does the
capacity still activate with the target error-detected?

Twirl = pool the 16 (i,j) logical-Pauli-pair circuits at equal shots (the exact channel twirl).
In-window control = the DEFINITE-order null (same 64 circuits, order fixed -> R_bar = 0). F83's
bare R_bar=0.5034 is the cited reference (not re-flown; the null is the in-window control).

Estimator (F83 verbatim, logical): per input bit, R = <Zbar1>_{c=+} - <Zbar1>_{c=-}
(conditioned on ZZZZ-accept); R_bar = (R_b0 - R_b1)/2. Logical Zbar1 = Z0Z2 -> z(q1)^z(q3).

Arms x pairs x inputs (64 circuits): {switch, null} x 16 Pauli pairs x {input 0,1}.
FROZEN GATES:
  W1_CAPACITY_ACTIVATED: R_bar_switch(logical) > 0.10 (F83 WIN floor) at >=5 sigma — information
     survives two zero-capacity channels, error-detected.
  W2_NULL_DEAD: |R_bar_null(logical)| <= 0.10 (definite order transmits nothing — the in-window
     causal-separability control).
  W3_UNCONDITIONED_DEAD: |D_switch| <= 0.08 (the info lives ONLY in the control-target
     correlation, not the marginal target — F83's dual-role signature).
  G_ACC: ZZZZ acceptance >= 0.55.
Registered verdict = W1 and W2 and W3 and G_acc.
SCOPE: device-characterized capacity activation (F83 scope), half-shielded (target only),
single-syndrome ZZZZ partial shield. Textbook ICO-capacity + [[4,2,2]] priors credited; the
contribution is the composition — capacity activation with the target error-detected.
BUDGET CHECK (C4887): F83 bare 0.5034; logical postselected should recover most (196/205/208
recovered fragile quantities at >0.85 contrast). Filed: R_bar_switch in [0.30,0.52];
|R_bar_null| < 0.08; acceptance in [0.70,0.92].
Usage: --selftest | --submit [--backend ibm_fez --shots 2000] | --decode
"""
import argparse, itertools, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PAULIS = ["1", "X", "Y", "Z"]


def _ctrl_logical(qc, gate, c, cstate):
    """controlled logical Pauli on the target block (q1-4), controlled by c==cstate.
    Xbar1=X0X1, Zbar1=Z0Z2, Ybar1=Y0X1Z2 (block-local 0,1,2 -> q1,q2,q3)."""
    if gate == "1":
        return
    if cstate == 0: qc.x(c)
    if gate == "X":
        qc.cx(c, 1); qc.cx(c, 2)
    elif gate == "Z":
        qc.cz(c, 1); qc.cz(c, 3)
    elif gate == "Y":
        qc.cy(c, 1); qc.cx(c, 2); qc.cz(c, 3)     # controlled Ybar1 = c-(Y0 X1 Z2)
    if cstate == 0: qc.x(c)


def logical_circuit(A, B, input_bit, definite):
    qc = QuantumCircuit(5, 5)
    qc.h(0)                                        # bare control |+>
    qc.h(1); qc.cx(1, 2); qc.cx(1, 3); qc.cx(1, 4) # target |0bar0bar>
    if input_bit == 1:
        qc.x(1); qc.x(2)                           # Xbar1 -> input |1bar>
    qc.barrier()
    if not definite:
        _ctrl_logical(qc, A, 0, 0); _ctrl_logical(qc, B, 0, 1)
        qc.barrier()
        _ctrl_logical(qc, B, 0, 0); _ctrl_logical(qc, A, 0, 1)
    else:
        _uncond_logical(qc, A); _uncond_logical(qc, B)
    qc.barrier(); qc.h(0)
    for q in range(5): qc.measure(q, q)            # control(X)=clbit0, target(Z)=clbits1-4
    return qc


def _uncond_logical(qc, gate):
    if gate == "X": qc.x(1); qc.x(2)
    elif gate == "Z": qc.z(1); qc.z(3)
    elif gate == "Y": qc.y(1); qc.x(2); qc.z(3)


def _pool(counts_list):
    tot = {}
    for c in counts_list:
        for k, v in c.items():
            tot[k] = tot.get(k, 0) + v
    return tot


def analyze(get):
    """get(kind, a, b, bit) -> counts. Returns R_bar, null-dead D, acceptance per kind."""
    out = {}
    for kind in ("switch", "null"):
        stats = {}; dsig = []
        acc_tot = tot_tot = 0
        for bit in (0, 1):
            pool = _pool([get(kind, a, b, bit) for a in PAULIS for b in PAULIS])
            zc = {"plus": [0, 0], "minus": [0, 0]}   # [n_z+, n_z-] conditioned on accept
            n_un = [0, 0]                            # unconditioned target Zbar (for D)
            n_all = acc = 0
            for s, cnt in pool.items():
                b5 = s.replace(" ", "")
                v = [int(b5[-1 - i]) for i in range(5)]   # v[0]=control, v[1..4]=target q1-4
                n_all += cnt
                zbar = v[1] ^ v[3]                    # Zbar1 = Z0Z2 -> q1^q3
                n_un[zbar] += cnt
                if (v[1] ^ v[2] ^ v[3] ^ v[4]) != 0:  # ZZZZ reject
                    continue
                acc += cnt
                lab = "plus" if v[0] == 0 else "minus"
                zc[lab][zbar] += cnt
            acc_tot += acc; tot_tot += n_all
            mz = {}
            varc = {}
            for lab in ("plus", "minus"):
                nn = zc[lab][0] + zc[lab][1]
                z = (zc[lab][0] - zc[lab][1]) / max(nn, 1)
                mz[lab] = z; varc[lab] = (1 - z * z) / max(nn, 1)
            R = mz["plus"] - mz["minus"]
            varR = varc["plus"] + varc["minus"]
            # unconditioned target signal (accept-agnostic marginal)
            du = (n_un[0] - n_un[1]) / max(n_all, 1)
            stats[bit] = {"R": R, "varR": varR, "du": du,
                          "dvar": (1 - du * du) / max(n_all, 1)}
            dsig.append(du)
        Rbar = (stats[0]["R"] - stats[1]["R"]) / 2
        seR = float(np.sqrt((stats[0]["varR"] + stats[1]["varR"]) / 4))
        D = (stats[0]["du"] - stats[1]["du"]) / 2
        seD = float(np.sqrt((stats[0]["dvar"] + stats[1]["dvar"]) / 4))
        out[kind] = {"Rbar": Rbar, "seR": seR, "D": D, "seD": seD,
                     "acceptance": acc_tot / tot_tot if tot_tot else 0.0}
    return out


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000; cache = {}
    def get(kind, a, b, bit):
        k = (kind, a, b, bit)
        if k not in cache:
            qc = logical_circuit(a, b, bit, kind == "null")
            cache[k] = sim.run(qc, shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    print("Exp210 selftest (noiseless) | switch R_bar ~ +0.533, null R_bar ~ 0, D ~ 0 both")
    print(f"  switch: R_bar={r['switch']['Rbar']:+.4f}  D={r['switch']['D']:+.4f}  "
          f"acc={r['switch']['acceptance']:.3f}")
    print(f"  null:   R_bar={r['null']['Rbar']:+.4f}  D={r['null']['D']:+.4f}  "
          f"acc={r['null']['acceptance']:.3f}")
    assert abs(r["switch"]["Rbar"] - 0.5333) < 0.03, "shielded switch must activate capacity ~0.533"
    assert abs(r["null"]["Rbar"]) < 0.03, "definite-order null must transmit nothing"
    assert abs(r["switch"]["D"]) < 0.03 and abs(r["null"]["D"]) < 0.03, "unconditioned signal ~0"
    assert abs(r["switch"]["acceptance"] - 1) < 0.02, "noiseless acceptance ~1"
    print("SELFTEST PASS: information survives two zero-capacity depolarizing channels with the "
          "target encoded in [[4,2,2]] and post-selected — R_bar ~ 0.533 (switch) vs 0 (definite "
          "order), signal only in the control-target correlation (D~0). Cleared to fly.")


def _entries():
    return [(kind, a, b, bit) for kind in ("switch", "null")
            for a in PAULIS for b in PAULIS for bit in (0, 1)]


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    ent = _entries()
    circuits = [transpile(logical_circuit(a, b, bit, kind == "null"),
                          backend=backend, optimization_level=3, seed_transpiler=0)
                for (kind, a, b, bit) in ent]
    n2s = [sum(1 for inst in c.data if inst.operation.num_qubits == 2) for c in circuits]
    print(f"  {len(circuits)} circuits, 2q range {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp210_shielded_capacity_manifest.json")
    man = {"exp": 210, "slug": "shielded_capacity_activation", "backend": backend_name,
           "shots": shots, "job_id": job.job_id(),
           "order": [[k, a, b, bit] for (k, a, b, bit) in ent], "n2_range": [min(n2s), max(n2s)]}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "W1_capacity_activated": "R_bar_switch(logical) > 0.10 at >=5 sigma",
        "W2_null_dead": "|R_bar_null(logical)| <= 0.10 (in-window causal-separability control)",
        "W3_unconditioned_dead": "|D_switch| <= 0.08 (signal only in control-target correlation)",
        "G_acc": "ZZZZ acceptance >= 0.55",
        "registered_verdict": "W1 and W2 and W3 and G_acc",
        "scope": "device-characterized (F83), half-shielded target, single-syndrome ZZZZ; "
                 "F83 bare R_bar=0.5034 cited as reference (null is the in-window control)",
        "budget_predictions": "R_bar_switch in [0.30,0.52]; |R_bar_null| < 0.08; "
                              "acceptance in [0.70,0.92]"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp210_shielded_capacity_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (kind, a, b, bit) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(kind, a, b, int(bit))] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda k, a, b, bit: raw[(k, a, b, bit)])
    sw, nu = r["switch"], r["null"]
    z_w1 = (sw["Rbar"] - 0.10) / sw["seR"]
    print(f"Exp210 SHIELDED CAPACITY ACTIVATION decode | job {man['job_id']} | "
          f"F83 bare ref R_bar=0.5034")
    print(f"  switch: R_bar={sw['Rbar']:+.4f} (se {sw['seR']:.4f})  D={sw['D']:+.4f} "
          f"(se {sw['seD']:.4f})  acceptance={sw['acceptance']:.3f}")
    print(f"  null:   R_bar={nu['Rbar']:+.4f} (se {nu['seR']:.4f})  D={nu['D']:+.4f}")
    w1 = sw["Rbar"] > 0.10 and z_w1 >= 5
    w2 = abs(nu["Rbar"]) <= 0.10
    w3 = abs(sw["D"]) <= 0.08
    gacc = sw["acceptance"] >= 0.55
    print(f"\nW1 CAPACITY ACTIVATED: R_bar_switch {sw['Rbar']:.4f} > 0.10 ({z_w1:.1f} sigma) "
          f"{'OK' if w1 else 'MISS'}")
    print(f"W2 NULL DEAD: R_bar_null {nu['Rbar']:+.4f} {'OK' if w2 else 'MISS'}")
    print(f"W3 UNCONDITIONED DEAD: D_switch {sw['D']:+.4f} {'OK' if w3 else 'MISS'}")
    print(f"G_ACC: acceptance {sw['acceptance']:.3f} {'OK' if gacc else 'MISS'}")
    print(f"REFERENCE: shielded/bare = {sw['Rbar']/0.5034:.3f} (F83 bare 0.5034, descriptive)")
    ok = w1 and w2 and w3 and gacc
    win = ("SHIELDED CAPACITY ACTIVATION — information survives two individually-zero-capacity "
           "depolarizing channels with the target error-detected: fault-tolerant indefinite "
           "causal order as a WORKING resource, not just a witness")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "Rbar_switch": float(sw["Rbar"]),
               "seR_switch": float(sw["seR"]), "Rbar_null": float(nu["Rbar"]),
               "D_switch": float(sw["D"]), "acceptance": float(sw["acceptance"]),
               "sigma_w1": float(z_w1), "shielded_over_bare": float(sw["Rbar"] / 0.5034),
               "w1": bool(w1), "w2": bool(w2), "w3": bool(w3), "g_acc": bool(gacc),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp210_shielded_capacity_decode.json"), "w"), indent=1)
    print("-> results/exp210_shielded_capacity_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=2000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
