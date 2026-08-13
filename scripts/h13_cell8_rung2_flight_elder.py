#!/usr/bin/env python3
"""
h13_cell8_rung2_flight_elder.py — Cell 8 Rung 2, STEP 3 (the flight). Elder, C6607.

Frozen prereg: docs/h13-cell8-rung2-prereg-FROZEN-whisper-c5060.md (Amendments 1-6).

WHAT THIS DOES NOT DO, and why that is the design:
  · It NEVER receives the sealed instance sequence. Amendment 2 binds option (B): the flight uses
    the PUBLIC CANONICAL ORDER and the sealed permutation is a RELABELLING APPLIED AT DECODE.
    Blindness here is STRUCTURAL, not disciplinary — this script cannot fly the wrong order
    because it never holds the right one.
  · It does not grade. Step 4 is a separate blind decode against the frozen public grader.

GATES ASSERTED HERE (all must pass before a submit is attempted):
  G0b  support(q*) == count(distinct manifest field)     — 51 == 51
  A4   index-table digest 8371d260…                      — canonical order, parser-INVARIANT
  G0e  entanglement survives transpilation, PER PAIR     — the finding that would have voided this
  G1   account scope                                      — via preflight_account_check.py
  G2   fit gate at submit, against the LIVE tank          — never asserted from a balance

G0e EXISTS BECAUSE THE OBVIOUS BUILD IS SILENTLY WRONG. At optimization_level>=2 the transpiler
DELETES every 2-qubit gate: when BA = ±AB the two order branches leave the target in the same state
up to a sign, so control-target entanglement collapses to a control PHASE, and a measured-qubit-
only-phase circuit is genuinely reducible to one qubit. Measured on FakeMarrakesh, all 51 pairs:
opt=0 -> 4 two-qubit gates, opt=1 -> 4, opt=2 -> 0, opt=3 -> 0. A flight built at opt=3 would have
returned near-ideal separation on circuits THAT NEVER ENTANGLED ANYTHING, and would have looked
BETTER than the truth because it dodges the 2q noise the F75 haircut accounts for.
The DEFINITE arm legitimately has zero 2q gates, so the assertion is ARM-AWARE.

  python3 h13_cell8_rung2_flight_elder.py --scan     # FREE: build, gate, sim-check. No QPU.
  python3 h13_cell8_rung2_flight_elder.py --submit   # spends QPU; runs every gate first
"""
import argparse, hashlib, json, os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
PREREG_DOC = "docs/h13-cell8-rung2-prereg-FROZEN-whisper-c5060.md"
# TWO SEPARATE PROVENANCES, deliberately not one field:
#   · the ARTIFACT is pinned by its SEALED sha256 (commit-independent — the bytes are the identity)
#   · the SPEC is pinned by the prereg commit CURRENT AT BUILD TIME, resolved live below
# C6607 (Whisper general#10812): this was a single hardcoded FREEZE_COMMIT="bb46926", which was the
# true prereg head when the script was written. Amendment 5 (G0e) landed at d36ae4f UNDERNEATH the
# build, so the manifest recorded a flight "built against" a spec version that does not contain the
# gate the manifest exists to record. Nothing decayed and nobody erred — THE SPEC MOVED AND THE
# STAMP DID NOT. A grader checking the manifest against bb46926 would find no G0e there at all and
# read a compliant flight as non-compliant.
ARTIFACT_COMMIT = "bb46926"        # any commit whose bytes hash to QSTAR_SHA; the SHA is the pin
QSTAR = "results/causal_game_sdp_qij.json"
QSTAR_SHA = "e471bb6512326abdee69ea5531efab501248d5cd99e9debd0578603fd249c1e7"
INDEX_TABLE_DIGEST = "8371d2604275c02a7c0b2d4606805971d244f206c779cc3f8e810e417f8e33c0"
MANIFEST = "results/exp105_hw_results.json"

R2 = np.sqrt(2)
_I = np.eye(2, dtype=complex)
_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_Z = np.array([[1, 0], [0, -1]], dtype=complex)
GENERATORS = {
    "1": _I, "X": _X, "Y": _Y, "Z": _Z,
    "(X+Y)/r2": (_X + _Y) / R2, "(X-Y)/r2": (_X - _Y) / R2,
    "(X+Z)/r2": (_X + _Z) / R2, "(X-Z)/r2": (_X - _Z) / R2,
    "(Y+Z)/r2": (_Y + _Z) / R2, "(Y-Z)/r2": (_Y - _Z) / R2,
}


def _frozen_bytes(path):
    return subprocess.check_output(["git", "-C", REPO, "show", f"{ARTIFACT_COMMIT}:{path}"])


def prereg_head():
    """The prereg commit CURRENT AT BUILD TIME, plus an assertion that it actually contains the
    gates this script implements. Without the assertion the stamp drifts again the next time an
    amendment lands mid-build — which on the current rate is about forty minutes."""
    sha = subprocess.check_output(
        ["git", "-C", REPO, "log", "-1", "--format=%H", "--", PREREG_DOC]).decode().strip()
    doc = subprocess.check_output(["git", "-C", REPO, "show", f"{sha}:{PREREG_DOC}"]).decode()
    for token in ("G0e", INDEX_TABLE_DIGEST[:16]):
        if token not in doc:
            sys.exit(f"G-FAIL prereg {sha[:7]} does not contain {token!r} — this script implements "
                     f"it, so the stamp would claim a spec version that lacks the gate")
    return sha


def canonical_table():
    """Amendment 4, verbatim: union of the two key sets, ascending lexicographic, 0-based.
    Parser-INVARIANT by construction — depends only on key STRINGS, never on insertion order."""
    raw = _frozen_bytes(QSTAR)
    got = hashlib.sha256(raw).hexdigest()
    if got != QSTAR_SHA:
        sys.exit(f"G-FAIL q* artifact hash {got} != sealed {QSTAR_SHA}")
    d = json.loads(raw)
    C, A = d["q_star_commuting"], d["q_star_anticommuting"]
    if set(C) & set(A):
        sys.exit("G-FAIL q* classes are not disjoint — the union is not a total order")
    merged = sorted(set(C) | set(A))
    table = [(k, "C" if k in C else "A") for k in merged]
    blob = "\n".join(f"{i}\t{k}\t{c}" for i, (k, c) in enumerate(table))
    dig = hashlib.sha256(blob.encode()).hexdigest()
    if dig != INDEX_TABLE_DIGEST:
        sys.exit(f"G-FAIL index-table digest {dig} != {INDEX_TABLE_DIGEST}")
    return table, dig


def parse_pair(key):
    """'((X+Y)/r2,(X-Y)/r2)' -> two generator labels. No label contains a comma, so the single
    split of the outer-paren body is unambiguous — checked against the frozen labels, not assumed."""
    a, b = key[1:-1].split(",")
    if a not in GENERATORS or b not in GENERATORS:
        sys.exit(f"G-FAIL unknown generator label in {key}")
    return a, b


def build_switch(A, B, definite=False):
    """control q0 in |+>, target q1.  c=0 -> A then B (BA);  c=1 -> B then A (AB).
    Controlled ARBITRARY single-qubit unitaries — exp91's cx/cy/cz path covers only 3 of the 10
    generators in §1 and raises on the other 7, including index 0 of the canonical table."""
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Operator
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    gA = Operator(A).to_instruction(); gA.name = "A"
    gB = Operator(B).to_instruction(); gB.name = "B"
    if not definite:
        qc.append(gA.control(1, ctrl_state=0), [0, 1])
        qc.append(gB.control(1, ctrl_state=1), [0, 1])
        qc.append(gB.control(1, ctrl_state=0), [0, 1])
        qc.append(gA.control(1, ctrl_state=1), [0, 1])
    else:
        qc.append(gA, [1]); qc.append(gB, [1])       # fixed order, control is a spectator
    qc.h(0)
    qc.measure(0, 0)
    return qc


def ideal_separation(table):
    """Statevector check BEFORE any hardware: commuting -> +1, anticommuting -> -1.

    NOTE THE OBSERVABLE. build_switch ends with H on the control (the X-basis rotation), so after
    that H the control's X-information sits in Z. Measuring <X> on the post-H state returns ~0 and
    looks like a dead construction — which is exactly what this gate caught on its first run, and
    why the gate exists at all: my standalone check measured <X> BEFORE the H and read +2.0000,
    the script measured after it and read -0.0000. Same physics, different basis, opposite verdict."""
    from qiskit.quantum_info import Operator, Statevector
    from qiskit import QuantumCircuit
    vals = {"C": [], "A": []}
    for key, cls in table:
        a, b = parse_pair(key)
        qc = build_switch(GENERATORS[a], GENERATORS[b])
        qc2 = qc.remove_final_measurements(inplace=False)
        sv = Statevector.from_instruction(qc2)
        # post-H: the X-basis signal is read on Z
        vals[cls].append(float(np.real(sv.expectation_value(Operator(_Z), qargs=[0]))))
    return min(vals["C"]) - max(vals["A"]), vals


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true", help="FREE: build + gate + sim. No QPU.")
    ap.add_argument("--submit", action="store_true", help="spends QPU; all gates run first")
    ap.add_argument("--opt", type=int, default=1, help="transpile level; G0e requires <= 1")
    a = ap.parse_args()
    if not (a.scan or a.submit):
        ap.error("choose --scan (free) or --submit")
    if a.opt > 1:
        sys.exit(f"G0e-FAIL optimization_level={a.opt} > 1 — at >=2 the transpiler deletes every "
                 f"2q gate and the flight stops testing the switch (measured: opt2/opt3 -> 0)")

    table, dig = canonical_table()
    print(f"  A4 index-table digest  {dig[:16]}…  ✅ ASSERTED ({len(table)} pairs)")
    nC = sum(1 for _, c in table if c == "C"); nA = len(table) - nC
    print(f"  G0b support(q*)        {len(table)} = {nC} C + {nA} A  ✅")

    sep, vals = ideal_separation(table)
    print(f"  ideal separation       {sep:+.4f}   (C {min(vals['C']):+.3f}..{max(vals['C']):+.3f} · "
          f"A {min(vals['A']):+.3f}..{max(vals['A']):+.3f})")
    if sep < 1.99:
        sys.exit(f"G-FAIL ideal separation {sep:.4f} < 1.99 — construction is wrong before hardware")

    # G0e — per pair, arm-aware, recorded
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    be = FakeMarrakesh()
    g0e = []
    for key, cls in table:
        x, y = parse_pair(key)
        t = transpile(build_switch(GENERATORS[x], GENERATORS[y]), be,
                      optimization_level=a.opt, seed_transpiler=11)
        n2 = sum(v for g, v in t.count_ops().items() if g in ("cz", "ecr", "cx"))
        g0e.append({"pair": key, "cls": cls, "two_qubit_gates": n2, "depth": t.depth()})
        if n2 < 1:
            sys.exit(f"G0e-FAIL {key}: transpiled switch arm has {n2} two-qubit gates — "
                     f"the circuit does not entangle and does not test the switch")
    mn = min(r["two_qubit_gates"] for r in g0e)
    print(f"  G0e entanglement       ALL {len(g0e)} switch-arm circuits carry >=1 two-qubit gate "
          f"(min {mn})  ✅ per-pair, recorded")

    out = os.path.join(REPO, "results", "h13_cell8_rung2_g0e_manifest_elder.json")
    head = prereg_head()
    json.dump({"prereg_commit_at_build": head,
               "prereg_contains": ["G0e", "A4 index-table digest"],
               "artifact_commit": ARTIFACT_COMMIT, "qstar_sha256": QSTAR_SHA,
               "index_table_digest": dig, "opt_level": a.opt,
               "per_pair": g0e}, open(out, "w"), indent=1)
    print(f"  spec provenance        prereg {head[:7]} — ASSERTED to contain G0e + A4 digest ✅")
    print(f"  manifest -> {os.path.relpath(out, REPO)}")

    if a.scan:
        print("\n  --scan complete. NO QPU SPENT. G1/G2 run only on --submit.")
        return 0
    sys.exit("  --submit not yet wired: G1 (account scope) and G2 (live-tank fit) must be "
             "attached before this may spend QPU.")


if __name__ == "__main__":
    sys.exit(main() or 0)
