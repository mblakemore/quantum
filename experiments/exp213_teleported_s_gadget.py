#!/usr/bin/env python3
"""Exp213 — THE TELEPORTED-S GADGET on silicon: reaching the unreachable logical gate. C4905.

Horizons-5 P2 flight 1, on the standing go ("fly it!"). The C4901 audit proved single-logical-S
is UNREACHABLE in the [[4,2,2]] in-block transversal set (12/720). This flies the gadget that
reaches it — derived and statevector-verified in docs/teleported-s-gadget-derivation-whisper-
c4905.md (Gottesman-Chuang Bell-resource teleportation; naive one-bit constructions ruled out
as non-gates).

Construction (3 blocks, 12 qubits):
  A (data, q0-3) = |+bar> ;  B,C (q4-11) = resource (I (x) Sbar)|Phi+>bar
  logical Bell measurement A-B (transversal CNOT A->B, A in X-basis, B in Z-basis) -> bits bx,bz
  block C = Sbar|psi> up to logical Pauli frame Xbar^bx Zbar^bz (software, found-by-search)
  VERIFY: input |+bar> -> C in the logical Y-eigenstate (Sbar|+bar>); measure C in Ybar
     (Ybar1 = Y0 X1 Z2), frame-correct, expect <Ybar1_C> = +1. Identity (no-S resource) -> 0.

Arms:
  gadget  : resource (I (x) Sbar)|Phi+>  -> C = Sbar|+bar>, Ybar_corrected -> +1
  noS     : resource plain |Phi+>bar      -> C = |+bar> (identity teleport), Ybar -> 0 (the
            S-necessary null: the Ybar signal comes from the S in the resource, not teleportation)

FROZEN GATES:
  W1_GADGET_APPLIES_S: frame-corrected <Ybar1_C>(gadget) >= 0.40 at >=5 sigma (Sbar was applied
     through the gadget; ideal +1, hardware-hairut on a 12-qubit ~25 CX circuit).
  W2_S_NECESSARY: |<Ybar1_C>(noS)| <= 0.15 (identity teleport carries no Ybar; the signal is
     the S, not the teleportation).
  W3_FRAME_NECESSARY: uncorrected <Ybar1_C>(gadget) (frame ignored) <= 0.15 (the frame is
     load-bearing; without it the Bell outcomes average the signal to zero).
  G_ACC: Bell-measurement acceptance (A XXXX & B ZZZZ) >= 0.40.
Registered verdict = W1 and W2 and W3 and G_acc.
SCOPE: the resource + Bell measurement are stabilizer-checked; the C output Ybar readout is
mixed-basis (half-shielded, 208 pattern) — error detection on the gadget's inputs, not its
output. Textbook gate-teleportation + [[4,2,2]] priors; contribution = the logical S reached
on silicon, frozen-graded.
BUDGET CHECK (C4887): 12 qubits ~25 CX; postselected. Filed: Ybar_corrected in [0.40,0.80];
noS |Ybar| < 0.12; acceptance in [0.45,0.75].
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

_RES_CACHE = {}


def _resource(with_s):
    """(I (x) Sbar)|Phi+>bar (with_s) or plain |Phi+>bar on 8 qubits (block B=0-3, C=4-7)."""
    from qiskit.quantum_info import Pauli
    from qiskit.synthesis import synth_circuit_from_stabilizers
    key = with_s
    if key in _RES_CACHE:
        return _RES_CACHE[key]

    def mk8(bop, cop):
        s = ["I"] * 8
        for op, o in ((bop, 0), (cop, 4)):
            if op == "X": s[o] = "X"; s[o + 1] = "X"
            elif op == "Z": s[o] = "Z"; s[o + 2] = "Z"
            elif op == "Y": s[o] = "Y"; s[o + 1] = "X"; s[o + 2] = "Z"
        return "".join(s)
    c_op = "Y" if with_s else "X"                      # S conjugates Xbar_C -> Ybar_C
    stabs = [mk8("X", c_op), mk8("Z", "Z"), "ZZIIIIII", "IIIIZZII",
             "XXXXIIII", "ZZZZIIII", "IIIIXXXX", "IIIIZZZZ"]
    circ = synth_circuit_from_stabilizers([str(Pauli(s[::-1])) for s in stabs],
                                          allow_underconstrained=True)
    _RES_CACHE[key] = circ
    return circ


def circuit(arm):
    """arm in {gadget, noS}. A=q0-3 data, B=q4-7, C=q8-11 resource."""
    qc = QuantumCircuit(12, 12)
    qc.h(0); qc.cx(0, 1); qc.cx(0, 2); qc.cx(0, 3)       # data |0bar0bar>
    for q in range(4): qc.h(q)                            # -> |+bar+bar> (L1 data = |+bar>)
    qc.compose(_resource(arm == "gadget"), qubits=list(range(4, 12)), inplace=True)
    qc.barrier()
    for i in range(4): qc.cx(i, 4 + i)                    # transversal CNOT A->B
    qc.barrier()
    for q in range(4): qc.h(q)                            # A in X-basis (bx)
    # B in Z-basis (bz) — measured directly
    # C in Ybar basis: Ybar1_C = Y8 X9 Z10
    qc.sdg(8); qc.h(8)                                    # q8 -> Y basis
    qc.h(9)                                               # q9 -> X basis
    for q in range(12): qc.measure(q, q)
    return qc


def _decode_shot(v, frame):
    """v: 12 physical bits (index=qubit). Returns (accept, bx, bz, Ybar_C, Ybar_corrected)."""
    # A (q0-3) X-basis: accept XXXX (parity), Xbar1_A = x0^x1
    pA = v[0] ^ v[1] ^ v[2] ^ v[3]
    bx = v[0] ^ v[1]
    # B (q4-7) Z-basis: accept ZZZZ, Zbar1_B = z4^z6
    pB = v[4] ^ v[5] ^ v[6] ^ v[7]
    bz = v[4] ^ v[6]
    accept = (pA == 0 and pB == 0)
    # C (q8-11): Ybar1_C = Y8 X9 Z10 -> parity y8^x9^z10
    yC = v[8] ^ v[9] ^ v[10]
    Ybar_C = 1 - 2 * yC
    # frame: X^bx Z^bz on C both anticommute Ybar -> sign (-1)^(bx*fx + bz*fz)
    corr = ((bx * frame[0]) ^ (bz * frame[1]))
    Ybar_corr = Ybar_C * (1 - 2 * corr)
    return accept, bx, bz, Ybar_C, Ybar_corr


def analyze(counts, frame=(1, 1)):
    acc = nrej = ysum_c = ysum_u = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(12)]
        accept, bx, bz, yC, ycorr = _decode_shot(v, frame)
        if not accept:
            nrej += n; continue
        acc += n; ysum_c += ycorr * n; ysum_u += yC * n
    tot = acc + nrej
    return {"Ybar_corrected": ysum_c / acc if acc else 0.0,
            "Ybar_uncorrected": ysum_u / acc if acc else 0.0,
            "acceptance": acc / tot if tot else 0.0, "n_acc": acc}


def find_frame(counts_gadget):
    """Search the 4 Pauli frames for the one giving max |Ybar_corrected| on the gadget arm."""
    best = None
    for fx in (0, 1):
        for fz in (0, 1):
            r = analyze(counts_gadget, (fx, fz))
            if best is None or abs(r["Ybar_corrected"]) > abs(best[1]):
                best = ((fx, fz), r["Ybar_corrected"])
    return best[0]


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000
    cg = sim.run(circuit("gadget"), shots=shots).result().get_counts()
    cn = sim.run(circuit("noS"), shots=shots).result().get_counts()
    frame = find_frame(cg)
    rg = analyze(cg, frame); rn = analyze(cn, frame)
    print(f"Exp213 selftest (noiseless) | frame found: Xbar^bx Zbar^bz mask = {frame}")
    print(f"  gadget: Ybar_corrected={rg['Ybar_corrected']:+.4f} "
          f"(uncorrected {rg['Ybar_uncorrected']:+.4f})  acc={rg['acceptance']:.3f}")
    print(f"  noS:    Ybar_corrected={rn['Ybar_corrected']:+.4f}  acc={rn['acceptance']:.3f}")
    assert rg["Ybar_corrected"] > 0.95, "gadget must apply Sbar: frame-corrected Ybar_C ~ +1"
    assert abs(rg["Ybar_uncorrected"]) < 0.1, "uncorrected must be ~0 (frame is load-bearing)"
    assert abs(rn["Ybar_corrected"]) < 0.1, "no-S resource must give identity (Ybar ~ 0)"
    print("SELFTEST PASS: the teleported-S gadget applies logical Sbar (|+bar> -> Y-eigenstate, "
          "frame-corrected Ybar_C=+1); the no-S resource gives identity (Ybar=0); the frame is "
          "load-bearing (uncorrected=0). The unreachable logical gate, reached. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = ["gadget", "noS"]
    circuits = [transpile(circuit(a), backend=backend, optimization_level=3, seed_transpiler=0)
                for a in names]
    n2s = [sum(1 for inst in c.data if inst.operation.num_qubits == 2) for c in circuits]
    print(f"  2q counts: {dict(zip(names, n2s))}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp213_teleported_s_manifest.json")
    man = {"exp": 213, "slug": "teleported_s_gadget", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names, "n2": dict(zip(names, n2s))}
    json.dump(man, open(out, "w"), indent=1)
    man["prereg"] = {
        "W1_gadget_applies_s": "frame-corrected <Ybar1_C>(gadget) >= 0.40 at >=5 sigma",
        "W2_s_necessary": "|<Ybar1_C>(noS)| <= 0.15",
        "W3_frame_necessary": "uncorrected <Ybar1_C>(gadget) <= 0.15",
        "G_acc": "Bell-measurement acceptance >= 0.40",
        "registered_verdict": "W1 and W2 and W3 and G_acc",
        "scope": "resource+Bell-measurement stabilizer-checked; C Ybar output mixed-basis "
                 "(half-shielded, 208 pattern); frame found-by-search on the gadget arm",
        "budget_predictions": "Ybar_corrected in [0.40,0.80]; noS |Ybar| < 0.12; "
                              "acceptance in [0.45,0.75]"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp213_teleported_s_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    frame = find_frame(raw["gadget"])
    rg = analyze(raw["gadget"], frame); rn = analyze(raw["noS"], frame)
    shots = man["shots"]
    se_g = np.sqrt(max(1 - rg["Ybar_corrected"] ** 2, 1e-6) / max(rg["n_acc"], 1))
    se_n = np.sqrt(max(1 - rn["Ybar_corrected"] ** 2, 1e-6) / max(rn["n_acc"], 1))
    z1 = (rg["Ybar_corrected"] - 0.40) / se_g
    print(f"Exp213 THE TELEPORTED-S GADGET decode | job {man['job_id']} | frame {frame}")
    print(f"  gadget: Ybar_corrected={rg['Ybar_corrected']:+.4f} (se {se_g:.4f}, "
          f"uncorrected {rg['Ybar_uncorrected']:+.4f})  acc={rg['acceptance']:.3f}")
    print(f"  noS:    Ybar_corrected={rn['Ybar_corrected']:+.4f} (se {se_n:.4f})  "
          f"acc={rn['acceptance']:.3f}")
    w1 = rg["Ybar_corrected"] >= 0.40 and z1 >= 5
    w2 = abs(rn["Ybar_corrected"]) <= 0.15
    w3 = abs(rg["Ybar_uncorrected"]) <= 0.15
    gacc = rg["acceptance"] >= 0.40
    print(f"\nW1 GADGET APPLIES S: Ybar_C {rg['Ybar_corrected']:.3f} ({z1:.1f} sigma over 0.40) "
          f"{'OK' if w1 else 'MISS'}")
    print(f"W2 S NECESSARY: noS Ybar {rn['Ybar_corrected']:+.3f} {'OK' if w2 else 'MISS'}")
    print(f"W3 FRAME NECESSARY: uncorrected {rg['Ybar_uncorrected']:+.3f} {'OK' if w3 else 'MISS'}")
    print(f"G_ACC: {rg['acceptance']:.3f} {'OK' if gacc else 'MISS'}")
    ok = w1 and w2 and w3 and gacc
    win = ("THE TELEPORTED-S GADGET — the logical Sbar gate that is UNREACHABLE in the [[4,2,2]] "
           "transversal set (C4901) is reached on silicon by Bell-resource teleportation: "
           "|+bar> -> Sbar|+bar> (Y-eigenstate) with the S-necessary and frame-necessary nulls "
           "dead. The b!=0 HLF family is unlocked")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "frame": list(frame),
               "Ybar_gadget": float(rg["Ybar_corrected"]),
               "Ybar_gadget_uncorrected": float(rg["Ybar_uncorrected"]),
               "Ybar_noS": float(rn["Ybar_corrected"]), "acceptance": float(rg["acceptance"]),
               "sigma_w1": float(z1),
               "w1": bool(w1), "w2": bool(w2), "w3": bool(w3), "g_acc": bool(gacc),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp213_teleported_s_decode.json"), "w"), indent=1)
    print("-> results/exp213_teleported_s_decode.json")


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
