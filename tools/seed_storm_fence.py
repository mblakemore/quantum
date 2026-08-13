#!/usr/bin/env python3
"""
seed_storm_fence.py — K-seed transpile-stability linter (H14 Deck B cell B3, Whisper C5066).

THE DEATH THIS ENCODES (H13 Cell 6, RETIRED $0): a premise gate cleared 0.95 by 0.0007 at one
transpiler seed and failed at another (7 vs 9 2q gates). *A gate that flips on a transpiler seed
is not a gate.* Sibling lesson (Cells 6+6b NO-TEST, C5058): price 2q counts from the TRANSPILED
circuit on the candidate layout, never from the textbook decomposition.

This is the compilation-side sibling of tools/gate_feasibility_lint.py (the statistics side).
Run it at DESIGN time on any registered gate whose bar depends on compiled properties
(2q count, depth): transpile at K seeds, report the distribution, and rule each bar

    STABLE         pass/fail verdict identical at every sampled seed
    SEED-UNSTABLE  the verdict flips across sampled seeds -> NO-TEST at design time;
                   re-derive the bar or pin the seed AND record that the gate is
                   seed-conditional (a weaker object, said out loud)

SCOPE, stated as the charter requires: the claim is "unstable under the sampled seeds",
never "stable under all compilation" — K seeds sample compiler nondeterminism, they do not
exhaust it. A STABLE ruling is a floor for confidence, not a certificate.

MEASURED WHILE BUILDING (C5066): seed-instability is SETTINGS-DEPENDENT — the Cell 6 circuit
is seed-constant at optimization_level=1 on both a line and a heavy-hex map, and spreads
10-12 2q at levels 2-3 (stochastic layout/routing engages). Therefore the fence MUST be run
at the exact optimization_level / layout mode the flight will use; a STABLE ruling at other
settings certifies nothing about the flight's compilation path.

Usage:
    python3 tools/seed_storm_fence.py --selftest      # positive controls (fence can block)
Library:
    from seed_storm_fence import seed_storm
    report = seed_storm(circuit, coupling_map=cmap, bars=[
        {"name": "premise_2q_budget", "property": "2q", "threshold": 8, "direction": "below"}],
        k=25, optimization_level=1, initial_layout=None, basis_gates=None)
"""
import argparse
import os
import sys

from qiskit import transpile
from qiskit.transpiler import CouplingMap

DEFAULT_K = 25
TWOQ_NAMES = {"cx", "cz", "ecr", "swap", "iswap", "cp", "rzz"}


def compiled_props(tc):
    ops = tc.count_ops()
    twoq = sum(n for name, n in ops.items() if name in TWOQ_NAMES)
    return {"2q": twoq, "depth": tc.depth()}


def seed_storm(circuit, coupling_map=None, backend=None, bars=(), k=DEFAULT_K,
               optimization_level=1, initial_layout=None, basis_gates=None):
    """Transpile at k seeds; rule every bar STABLE or SEED-UNSTABLE. Returns full report dict."""
    samples = []
    for seed in range(1, k + 1):
        kw = dict(optimization_level=optimization_level, seed_transpiler=seed)
        if backend is not None:
            kw["backend"] = backend
        if coupling_map is not None:
            kw["coupling_map"] = coupling_map
        if basis_gates is not None:
            kw["basis_gates"] = basis_gates
        if initial_layout is not None:
            kw["initial_layout"] = initial_layout
        samples.append(compiled_props(transpile(circuit, **kw)))
    report = {"k": k, "optimization_level": optimization_level, "samples": samples, "bars": []}
    for prop in ("2q", "depth"):
        vals = [s[prop] for s in samples]
        report[prop] = {"min": min(vals), "max": max(vals), "spread": max(vals) - min(vals)}
    for bar in bars:
        vals = [s[bar["property"]] for s in samples]
        if bar["direction"] == "below":
            verdicts = [v <= bar["threshold"] for v in vals]
        else:
            verdicts = [v >= bar["threshold"] for v in vals]
        flips = len(set(verdicts)) > 1
        report["bars"].append({
            "name": bar["name"], "property": bar["property"], "threshold": bar["threshold"],
            "direction": bar["direction"], "values": {"min": min(vals), "max": max(vals)},
            "pass_fraction": sum(verdicts) / len(verdicts),
            "ruling": "SEED-UNSTABLE (NO-TEST at design time)" if flips else "STABLE (under the sampled seeds)",
        })
    return report


def print_report(report, title=""):
    print(f"SEED-STORM FENCE {title} | K={report['k']} seeds, opt_level={report['optimization_level']}")
    for prop in ("2q", "depth"):
        r = report[prop]
        print(f"  {prop:5s}: min {r['min']}  max {r['max']}  spread {r['spread']}")
    for b in report["bars"]:
        print(f"  BAR {b['name']} ({b['property']} {b['direction']} {b['threshold']}): "
              f"values [{b['values']['min']}, {b['values']['max']}], "
              f"pass fraction {b['pass_fraction']:.2f} -> {b['ruling']}")


def selftest():
    """Both positive controls: the fence must BLOCK on the known-flip and CLEAR on the robust circuit."""
    # P1 — the banked Cell 6 circuit itself (Tier A tripwire, N=1), the flight that died on seeds.
    sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts"))
    from h13_cell6_6b_submit_c5058 import build
    c6 = build("A", 1, (1, 1), "cell6_A_N1_marked")
    cmap = CouplingMap.from_line(12)
    basis = ["cz", "rz", "sx", "x", "id"]
    # optimization_level=2: stochastic layout/routing engages (at level 1 this circuit is
    # seed-constant on toy maps — see MEASURED WHILE BUILDING in the docstring).
    rep = seed_storm(c6, coupling_map=cmap, basis_gates=basis, bars=[], k=DEFAULT_K,
                     optimization_level=2)
    lo, hi = rep["2q"]["min"], rep["2q"]["max"]
    assert rep["2q"]["spread"] > 0, (
        f"P1: Cell 6 circuit shows no 2q spread across {DEFAULT_K} seeds on a line map "
        f"(got constant {lo}) — the known-flip control failed to flip")
    mid = (lo + hi) / 2.0
    rep = seed_storm(c6, coupling_map=cmap, basis_gates=basis, k=DEFAULT_K,
                     optimization_level=2,
                     bars=[{"name": "cell6_premise_budget", "property": "2q",
                            "threshold": mid, "direction": "below"}])
    print_report(rep, "P1 (Cell 6 known-flip)")
    assert "SEED-UNSTABLE" in rep["bars"][0]["ruling"], "P1: bar inside the spread must rule SEED-UNSTABLE"
    # P2 — a routing-free circuit on its natural layout must be STABLE with the bar above it.
    from qiskit import QuantumCircuit
    ghz = QuantumCircuit(3)
    ghz.h(0); ghz.cx(0, 1); ghz.cx(1, 2); ghz.measure_all()
    rep2 = seed_storm(ghz, coupling_map=CouplingMap.from_line(3), basis_gates=basis,
                      initial_layout=[0, 1, 2], k=DEFAULT_K,
                      bars=[{"name": "ghz_2q_budget", "property": "2q",
                             "threshold": 3, "direction": "below"}])
    print_report(rep2, "P2 (GHZ robust control)")
    assert "STABLE" in rep2["bars"][0]["ruling"] and rep2["2q"]["spread"] == 0, \
        "P2: routing-free pinned GHZ must be seed-stable"
    print(f"\nSELFTEST PASS: Cell 6 circuit spreads [{lo}, {hi}] 2q across {DEFAULT_K} seeds on a line map "
          f"and a bar at {mid:.1f} is ruled SEED-UNSTABLE (the fence blocks); pinned GHZ is STABLE "
          f"(the fence clears). Wire into the prereg checklist beside gate_feasibility_lint.py.")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        selftest()
    else:
        ap.print_help()
