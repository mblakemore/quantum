#!/usr/bin/env python3
"""H15 R1-EXT — ALT-arm probe EXTENSION (Whisper C5075). Diagnostic, no seal, no claim.

WHY: the first probe put ALT-TOFFOLI at 28/32 = 88% [72, 95]. The FLIGHT prediction
(flyable arm + Elder's exact NULL 17/32) is 43/64 = 0.6719, which clears the frozen 0.6040
by 3.63 SD at the point estimate but falls to 0.5944 — BELOW threshold — at the ALT CI-low.
So a 14.5-QPU-s SEALED flight, consuming a single-use Creator GO and a fresh seal, currently
rides on a 32-row estimate. Required ALT floor for the flight to clear from its CI-low: 0.7393.

At the observed 0.875: n=64 -> CI-low 0.772; n=128 -> 0.807. This kit flies 128 ALT-TOFFOLI
rows (~2.7 QPU-s) plus the ablation contract, on a FRESH public seed so the draw is independent
of the first probe rather than a re-run of the same A's.

POOLING RULE, pre-registered: the extension is pooled with the original 28/32 ONLY IF the
ablation contract holds exactly (never 0/N, always N/N) — otherwise the epochs are not
comparable and the extension stands alone as the later, larger estimate.

$0 in this file. Submission path is the -fly sibling, gated identically.
"""
import sys
import numpy as np
sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_n1_synapse_incircuit_whisper_c5074 import build, classical_rule, SIM

EXT_SEED = 50751           # fresh, independent of the first probe's 5075
N_ALT, N_NEVER, N_ALWAYS = 128, 8, 8
N = 4

def draw_A(rng):
    A = [[0]*N for _ in range(N)]
    for i in range(N):
        for j in range(i, N):
            A[i][j] = int(rng.integers(2))
    return A

def ext_rows():
    rng = np.random.default_rng(EXT_SEED)
    rows = [("ALT_TOFFOLI", draw_A(rng), "auto") for _ in range(N_ALT)]
    rows += [("NEVER", draw_A(rng), "never") for _ in range(N_NEVER)]
    rows += [("ALWAYS", draw_A(rng), "always") for _ in range(N_ALWAYS)]
    return rows

def build_ext():
    return [build(A=p, arm=a) for _, p, a in ext_rows()]

def decode_ext(mems):
    out = {"ALT_TOFFOLI": {"n": 0, "accept": 0}, "NEVER": {"n": 0, "act1": 0},
           "ALWAYS": {"n": 0, "act1": 0}}
    for (kind, _, _), mem in zip(ext_rows(), mems):
        act, _, _ = classical_rule(mem)
        s = out[kind]; s["n"] += 1
        if kind == "ALT_TOFFOLI": s["accept"] += act
        else: s["act1"] += act
    return out

def selftest():
    circs = build_ext()
    res = SIM.run(circs, shots=1, memory=True).result()
    mems = [res.get_memory(i)[0] for i in range(len(circs))]
    d = decode_ext(mems)
    ok = (d["ALT_TOFFOLI"]["accept"] == N_ALT and d["NEVER"]["act1"] == 0
          and d["ALWAYS"]["act1"] == N_ALWAYS)
    return ok, d

if __name__ == "__main__":
    import json
    ok, d = selftest()
    print(f"selftest ok={ok}: {json.dumps(d)}")
    print(f"rows={N_ALT+N_NEVER+N_ALWAYS}  est QPU-s ~{(N_ALT+N_NEVER+N_ALWAYS)*0.021:.1f}")
    assert ok, "EXT SELFTEST FAILED"
