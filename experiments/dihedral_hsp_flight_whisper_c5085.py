#!/usr/bin/env python3
"""
Dihedral-HSP hardware DEMONSTRATION FLIGHT — FROZEN (Whisper C5085, board pending).
Submit ONE job to ibm_fez (free open-instance, #151 spend gate) under a Creator GO citing this
file's digest. --dry-run = $0 from_backend; --submit = hardware (run in BACKGROUND, never foreground/timeout).

FRAME: labeled ENGINEERING demonstration. The dihedral-HSP procedure (coset-state prep + Kuperberg
sieve) recovers the hidden shift s on real qubits. NO quantum-vs-classical advantage (small-N brute
force is trivial), NO scaling/crypto claim. The non-abelian coset counterpart to F113's abelian solver.

PAYLOAD (frozen): N=8 recover ALL 8 shifts x 3 bits (24 circuits) + N=16 recover ALL 16 shifts x low
bit (16 circuits) = 40 circuits, 2 qubits each, 20,000 shots each. Backend PINNED ibm_fez, exit pair
PINNED [141,144] (AVOIDS q142 — the coflow-caveat high-population error qubit). Physical qubits recorded
so any miss is mappable to a qubit (the coflow-caveat diagnostic lesson).
"""
import os, sys, json
import numpy as np
from qiskit import QuantumCircuit, transpile

BACKEND_NAME = "ibm_fez"
SHOTS = 20000
LAYOUT = [141, 144]                  # [control, target] — quiet connected pair, avoids q142
N8, N16 = 8, 16

# ---- FROZEN builders (self-contained; no external import so the digest is complete) ----
def coset(qc, q, k, s, N):
    qc.h(q); qc.p(2*np.pi*k*s/N, q)

def find_pair(k, N):
    for a in range(1, N):
        for b in range(1, N):
            if a == k or b == k: continue
            if (a+b) % N == k % N: return a, b, 0
            if (a-b) % N == k % N: return a, b, 1
    return k, None, None

def known_phase(N, m, low_bits):
    th = 0.0
    for j, sj in enumerate(low_bits):
        th += np.pi * sj / (2**(m-j))
    return th

def recover_bit_circuit(N, s, m, low_bits):
    n = int(np.log2(N)); k = 2**(n-1-m)
    a, b, herald = find_pair(k, N)
    qc = QuantumCircuit(2, 2)         # every frozen target needs one combination round (2 qubits)
    coset(qc, 0, a, s, N)             # control
    coset(qc, 1, b, s, N)            # target
    qc.cx(0, 1)                      # Kuperberg combination
    qc.measure(1, 1)                # herald clbit1: 0->|psi_{a+b}>, 1->|psi_{a-b}>
    qc.p(-known_phase(N, m, low_bits), 0)   # correct known LOWER-bit phase (not the bit being read)
    qc.h(0); qc.measure(0, 0)       # X-read control = s_m -> clbit0
    return qc, herald

# ---- FROZEN payload: ordered list of (N, s, m). low_bits from the TRUE shift (sequential feedback,
#      pre-computed for a batch job; the bit m being recovered is never in its own correction). ----
PAYLOAD = []
for s in range(N8):
    for m in range(int(np.log2(N8))):
        PAYLOAD.append((N8, s, m))
for s in range(N16):
    PAYLOAD.append((N16, s, 0))          # low bit only = the scaling datapoint

def build_all():
    circ = []; heralds = []
    for (N, s, m) in PAYLOAD:
        low = [(s >> j) & 1 for j in range(m)]
        qc, h = recover_bit_circuit(N, s, m, low)
        circ.append(qc); heralds.append(h)
    return circ, heralds

def _counts_of(pubres):
    d = pubres.data
    reg = list(d.keys())[0]
    return getattr(d, reg).get_counts()

def decode_and_grade(cts, heralds):
    b1 = lambda k: k.replace(' ', '')[-2]; b0 = lambda k: k.replace(' ', '')[-1]
    per = []
    for i, (N, s, m) in enumerate(PAYLOAD):
        c = cts[i]; h = heralds[i]
        kept = {k: v for k, v in c.items() if b1(k) == str(h)}
        tot = sum(kept.values()); ones = sum(v for k, v in kept.items() if b0(k) == '1')
        vote = ones/tot if tot else float('nan')
        rec = 1 if tot and vote > 0.5 else 0
        true = (s >> m) & 1
        per.append({"N": N, "s": s, "bit": m, "true": true, "recovered": rec,
                    "vote": round(vote, 4), "herald_kept": tot, "ok": rec == true})
    # full-string recovery per (N,s)
    def full(N):
        n = int(np.log2(N)); ok = 0; tot = 0
        for s in range(N):
            bits = [p for p in per if p["N"] == N and p["s"] == s]
            if N == N8:
                rs = sum(p["recovered"] << p["bit"] for p in bits)
                ok += (rs == s); tot += 1
            else:
                ok += all(p["ok"] for p in bits); tot += 1
        return ok, tot
    n8_ok, n8_tot = full(N8); n16_ok, n16_tot = full(N16)
    min_herald = min(p["herald_kept"] for p in per)
    checks = {
        "P1_N8_full_string": f"{n8_ok}/{n8_tot}",
        "P2_N16_lowbit": f"{n16_ok}/{n16_tot}",
        "F1_machinery_survived": n8_ok >= 6,          # falsifier: N8 full-string < 6/8 -> FAIL
        "F2_sieve_intact": min_herald >= 0.20*SHOTS,  # falsifier: any herald-kept < 20% -> corrupted
        "min_herald_kept": min_herald,
    }
    verdict = ("DEMONSTRATED" if (n8_ok == n8_tot and n16_ok == n16_tot)
               else "QUALIFIED" if (checks["F1_machinery_survived"] and checks["F2_sieve_intact"])
               else "NOT SURVIVED")
    return per, checks, verdict

def main():
    mode = "--submit" if "--submit" in sys.argv else "--dry-run"
    circ, heralds = build_all()
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
    import ibm_multi_account as m
    svc = m.service_for_submission("IBMQ_TOKEN")
    backend = svc.backend(BACKEND_NAME)
    isa = [transpile(c, backend, optimization_level=3, initial_layout=LAYOUT) for c in circ]
    if mode == "--dry-run":
        from qiskit_aer import AerSimulator
        sim = AerSimulator.from_backend(backend)
        cts = [sim.run(c, shots=SHOTS).result().get_counts() for c in isa]
        src = "Aer from_backend(ibm_fez) — $0 dry-run (real noise snapshot + real routing)"; job_id = None
        snap = None
    else:
        from qiskit_ibm_runtime import SamplerV2
        snap = m.submit_snapshot(backend)              # queue provenance AT submit (C5075 gap)
        job = SamplerV2(mode=backend).run(isa, shots=SHOTS)
        job_id = job.job_id()
        print(f"SUBMITTED job_id={job_id} backend={backend.name} circuits={len(circ)} shots={SHOTS}", flush=True)
        r = job.result(); cts = [_counts_of(r[i]) for i in range(len(circ))]
        src = f"ibm hardware {backend.name} job {job_id}"
    per, checks, verdict = decode_and_grade(cts, heralds)
    out = {"card": "dihedral_hsp_demo", "cycle": "C5085", "frame": "engineering demonstration, no advantage",
           "source": src, "job_id": job_id, "backend": BACKEND_NAME, "layout": LAYOUT, "shots": SHOTS,
           "payload_size": len(PAYLOAD), "submit_snapshot": snap, "per_bit": per, "checks": checks,
           "verdict": verdict, "prereg": "dihedral-hsp-flight-preregistration-whisper-c5085.md"}
    print(json.dumps({"checks": checks, "verdict": verdict}, indent=2))
    tag = "dryrun" if mode == "--dry-run" else f"hw_{job_id}"
    resdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "results")
    os.makedirs(resdir, exist_ok=True)
    with open(os.path.join(resdir, f"dihedral_hsp_demo_{tag}_c5085.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
