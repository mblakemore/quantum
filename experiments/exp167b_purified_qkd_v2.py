#!/usr/bin/env python3
"""Exp167b — PURIFY -> QKD v2: give the input a fighting chance. C4858.
v1 (job d9du8gphtsac739di1q0) was an honest null: the mechanism worked (S 0.714->1.306, QBER_x
0.593->0.218) but the faded input was already DEAD (S=0.714, 10us degraded far past the 164
curve + unpinned layout), so distilling a corpse stayed below the key threshold.
v2 fix: tau=4us (marginal, not dead) + PINNED layout (163's characterized qubits) so the faded
arm is a live-but-thin channel and distillation can carry the purified arm across into a key.

Same two arms (faded / purified), same bases, same-job delta. Reuses the v1 circuit at a
shorter tau with an initial_layout. Usage: --selftest | --submit | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp167_purified_qkd import circuit, analyze, ARMS, MESSAGE, selftest as _v1_selftest
from exp166_qkd import _otp, KEY_BASES, CHSH_BASES

TAU_US = 4.0


def selftest():
    _v1_selftest()   # algebra + injected-dephasing gate are tau-independent; reuse v1's


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    layout4 = json.load(open(os.path.join(HERE, "..", "results",
                        "exp163_memory_manifest.json")))["layout"]   # [127,137,147,146]
    print(f"pinned qubits: {layout4}")
    circuits, order = [], []
    for arm in ARMS:
        n = 2 if arm == "faded" else 4
        for a, b in KEY_BASES + CHSH_BASES:
            qc = circuit(arm, a, b, tau_us=TAU_US)
            circuits.append(transpile(qc, backend=backend, optimization_level=1,
                                      initial_layout=layout4[:n]))
            order.append([arm, a, b])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": "167b", "slug": "purified_qkd_v2", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order, "tau_us": TAU_US, "layout": layout4,
                "message": MESSAGE,
                "prereg": {"primary": "SF_purified > SF_faded AND SF_purified > 0 (positive key); "
                                      "faded S ~ 2 (marginal, not dead this time)",
                           "prediction": "faded S 1.8-2.3 SF 0-0.10; purified S 2.2-2.6 SF 0.15-0.45"}}
    out = os.path.join(HERE, "..", "results", "exp167b_purified_qkd_v2_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, tau={TAU_US}us, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp167b_purified_qkd_v2_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (arm, a, b) in enumerate(man["order"]):
        r = res[idx]; reg = list(r.data.keys())[0]
        raw[(arm, a, b)] = getattr(r.data, reg).get_counts()
    r = analyze(lambda arm, a, b: raw[(arm, a, b)], shots)
    f, p = r["faded"], r["purified"]
    se_S = 2.0 / np.sqrt(shots)
    print(f"Exp167b PURIFY->QKD v2 decode | job {man['job_id']} | tau={man['tau_us']}us | qubits {man['layout']}")
    print(f"  FADED    : S={f['S']:.3f}  QBER z/x={f['qber_z']:.3f}/{f['qber_x']:.3f}  SF={f['secret_fraction']:.3f}")
    print(f"  PURIFIED : S={p['S']:.3f}  QBER z/x={p['qber_z']:.3f}/{p['qber_x']:.3f}  SF={p['secret_fraction']:.3f}  (p={p['p_success']:.2f})")
    dSF = p["secret_fraction"] - f["secret_fraction"]
    fatter = p["secret_fraction"] > f["secret_fraction"] and p["secret_fraction"] > 0.02 and (p["S"] - 2) / se_S > 3
    print(f"\nKEY DELTA: SF {f['secret_fraction']:.3f} -> {p['secret_fraction']:.3f} ({dSF:+.3f}) | "
          f"S {f['S']:.2f} -> {p['S']:.2f} | QBER_x {f['qber_x']:.2f} -> {p['qber_x']:.2f}")
    msg = man["message"]
    if p["secret_fraction"] > 0.02 and len(p["alice_key"]) >= len(msg) * 8:
        enc = _otp(msg, p["alice_key"]); dec = _otp(enc, p["bob_key"]).decode(errors="replace")
        good = sum(1 for x, y in zip(dec, msg) if x == y) / len(msg)
        fkey = f["secret_fraction"] > 0.02 and len(f["alice_key"]) >= len(msg) * 8
        fdec = _otp(_otp(msg, f["alice_key"]), f["bob_key"]).decode(errors="replace") if fkey else "(no key — channel too thin)"
        print(f"PURIFIED CHANNEL: '{msg}' -> '{dec}' ({100*good:.0f}% chars)")
        print(f"FADED CHANNEL:    '{msg}' -> '{fdec}'")
    tag = ("PURIFICATION FATTENS THE KEY — distilling first carries the channel across the key threshold"
           if fatter else "NULL — distillation did not net a usable key at this input (honest accounting)")
    print(f"VERDICT: {tag}")
    out = {"job_id": man["job_id"], "tau_us": man["tau_us"],
           "faded": {k: v for k, v in f.items() if "key" not in k},
           "purified": {k: v for k, v in p.items() if "key" not in k},
           "delta_secret_fraction": float(dSF), "fatter": bool(fatter), "verdict": tag}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp167b_purified_qkd_v2_decode.json"), "w"), indent=1)
    print("-> results/exp167b_purified_qkd_v2_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=4096)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
