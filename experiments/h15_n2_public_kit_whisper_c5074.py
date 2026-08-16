#!/usr/bin/env python3
"""H15 N2 — PUBLIC FLIGHT KIT (Whisper C5074). Everything about the flight that
is NOT a secret, frozen in one file: row schedule, cal/ablation row design,
decode convention, thresholds, and the circuit constructors (imported verbatim
from the G0-pinned N1 module). Ember's frozen binder (coordination#12443
mitigation: zero pilot degrees of freedom) feeds the SEALED labels through
build_flight(); nothing here varies per run.

FROZEN CONSTANTS (any change = a new kit hash = a new GO):
  TOTAL=696 rows = M=632 graded (sealed order) + C=64 cal rows.
  SCHEDULE: cal row j sits at position floor((j+0.5)*TOTAL/C), j=0..63 — the
    door(a) interleave precedent; graded rows fill the rest in sealed order.
  CAL DESIGN (public seed CAL_SEED=5074): 16 known-ALT auto (convention/τ pin)
    + 16 known-NULL auto + 16 known-ALT never + 16 known-ALT always (the
    ablation arms ride the cal rows; graded rows are ALL arm=auto).
  DECODE: Bell map (a,b)->(b,a) on measured bits (G0-calibrated,
    pair-preserving); accept = XOR_i(a_i AND b_i)==0; actuator polarity:
    1 = "respond ALT". Response read from c_act ONLY.
  CRITERION: accuracy over the 632 graded rows > 0.6040
    (= 143/256 + 2.3*sqrt(p_C(1-p_C)/632), FROZEN, Elder #12427).
  COMMITMENT: 98b799c9912a3853 (public on origin, quantum@90e640f).
  BINDER RULES (Ember): transpile optimization_level=1 deterministic seed 5074,
    single job, S=1 shot per row, layout-gated register (safe-score doctrine).

$0 in this file. No submission path. No account import. Secrets never touch
this module — build_flight() takes them as an argument at bind time.
"""
import hashlib
import json
import sys

import numpy as np

sys.path.insert(0, "/droid/repos/quantum/experiments")
from h15_n1_synapse_incircuit_whisper_c5074 import build, classical_rule, SIM

TOTAL, M, C = 696, 632, 64
CAL_SEED = 5074
THRESHOLD = 0.6040
COMMITMENT = "98b799c9912a3853"
N = 4


def cal_positions():
    pos = sorted(set(int((j + 0.5) * TOTAL / C) for j in range(C)))
    assert len(pos) == C, "schedule collision"
    return pos


def draw_known_A(rng):
    A = [[0] * N for _ in range(N)]
    for i in range(N):
        for j in range(i, N):
            A[i][j] = int(rng.integers(2))
    return A


def cal_rows():
    """64 public cal rows from CAL_SEED: (kind, payload, arm)."""
    rng = np.random.default_rng(CAL_SEED)
    rows = []
    for arm, kind, count in (("auto", "ALT", 16), ("auto", "NULL", 16),
                             ("never", "ALT", 16), ("always", "ALT", 16)):
        for _ in range(count):
            if kind == "ALT":
                rows.append(("cal_ALT", draw_known_A(rng), arm))
            else:
                rows.append(("cal_NULL",
                             (int(rng.integers(16)), int(rng.integers(16))),
                             arm))
    return rows


def build_flight(sealed_rows):
    """sealed_rows: list of M dicts {label: 'ALT'|'NULL', A: [[..]] | xu: [x,u]}
    in SEALED ORDER (Ember's binder supplies this; labels never leave her).
    Returns the 696 circuits in flight order + the public row map."""
    assert len(sealed_rows) == M
    cpos = set(cal_positions())
    cals = cal_rows()
    circs, rowmap, ci, gi = [], [], 0, 0
    for p in range(TOTAL):
        if p in cpos:
            kind, payload, arm = cals[ci]
            if kind == "cal_ALT":
                circs.append(build(A=payload, arm=arm))
            else:
                circs.append(build(xu=payload, arm=arm))
            rowmap.append({"pos": p, "row": f"{kind}:{arm}", "cal_index": ci})
            ci += 1
        else:
            r = sealed_rows[gi]
            if r["label"] == "ALT":
                circs.append(build(A=r["A"], arm="auto"))
            else:
                circs.append(build(xu=tuple(r["xu"]), arm="auto"))
            rowmap.append({"pos": p, "row": "graded", "graded_index": gi})
            gi += 1
    assert ci == C and gi == M
    return circs, rowmap


def fake_secrets(seed=424242):
    """Self-test secrets — NOT the sealed ones (public seed, test only)."""
    rng = np.random.default_rng(seed)
    rows = []
    labels = ["ALT"] * (M // 2) + ["NULL"] * (M // 2)
    rng.shuffle(labels)
    for lab in labels:
        if lab == "ALT":
            rows.append({"label": "ALT", "A": draw_known_A(rng)})
        else:
            rows.append({"label": "NULL",
                         "xu": [int(rng.integers(16)), int(rng.integers(16))]})
    return rows


def selftest():
    """Assemble the full 696 on FAKE secrets, simulate a stratified subsample,
    verify every frozen property the flight will be graded on."""
    secrets = fake_secrets()
    circs, rowmap = build_flight(secrets)
    assert len(circs) == TOTAL
    idx = {"cal_ALT:auto": [], "cal_NULL:auto": [], "cal_ALT:never": [],
           "cal_ALT:always": [], "graded": []}
    for i, r in enumerate(rowmap):
        key = r["row"] if r["row"] != "graded" else "graded"
        idx[key].append(i)
    picks = (idx["cal_ALT:auto"] + idx["cal_ALT:never"][:8]
             + idx["cal_ALT:always"][:8] + idx["cal_NULL:auto"][:8]
             + idx["graded"][::8])
    res = SIM.run([circs[i] for i in picks], shots=1, memory=True).result()
    out = {"n_tested": len(picks)}
    fails = []
    graded_resp = {}
    for k, i in enumerate(picks):
        line = res.get_memory(k)[0]
        r, accept, dec = classical_rule(line)
        row = rowmap[i]["row"]
        if row == "cal_ALT:auto" and r != 1:
            fails.append(f"cal_ALT:auto pos{i} responded {r}")
        if row == "cal_ALT:never" and r != 0:
            fails.append(f"never pos{i} responded {r}")
        if row == "cal_ALT:always" and r != 1:
            fails.append(f"always pos{i} responded {r}")
        if row == "graded":
            if r != accept:
                fails.append(f"graded pos{i} pin mismatch")
            graded_resp[rowmap[i]["graded_index"]] = r
    # graded accuracy on the fake truth (subsample):
    correct = sum(1 for gi_, r in graded_resp.items()
                  if r == (1 if secrets[gi_]["label"] == "ALT" else 0))
    out["graded_subsample_accuracy"] = correct / len(graded_resp)
    out["fails"] = fails
    out["ok"] = not fails
    return out


if __name__ == "__main__":
    st = selftest()
    print(f"selftest: ok={st['ok']} n={st['n_tested']} "
          f"graded_acc={st['graded_subsample_accuracy']:.3f} "
          f"fails={st['fails'][:3]}", flush=True)
    kit_src = open(__file__, "rb").read()
    manifest = {
        "card": "h15_n2_public_kit", "cycle": "C5074",
        "TOTAL": TOTAL, "M": M, "C": C, "cal_seed": CAL_SEED,
        "schedule_rule": "cal j at floor((j+0.5)*TOTAL/C); graded fill sealed order",
        "cal_design": "16 known-ALT auto + 16 known-NULL auto + 16 known-ALT never + 16 known-ALT always",
        "decode": "Bell map (a,b)->(b,a); accept=XOR_i(a_i AND b_i)==0; actuator 1=ALT; read c_act only",
        "threshold_frozen": THRESHOLD, "commitment": COMMITMENT,
        "binder_rules": "transpile opt1 seed 5074, single job, S=1/row, layout-gated register",
        "selftest": st,
        "kit_sha256": hashlib.sha256(kit_src).hexdigest(),
        "n1_module_sha256": hashlib.sha256(open(
            "/droid/repos/quantum/experiments/"
            "h15_n1_synapse_incircuit_whisper_c5074.py", "rb").read()).hexdigest(),
    }
    with open("/droid/repos/quantum/results/h15_n2_public_kit_manifest_c5074.json",
              "w") as f:
        json.dump(manifest, f, indent=1)
    print(f"kit_sha256 {manifest['kit_sha256'][:16]}  "
          f"n1_sha256 {manifest['n1_module_sha256'][:16]}", flush=True)
    print("WROTE results/h15_n2_public_kit_manifest_c5074.json")
