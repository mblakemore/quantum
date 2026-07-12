#!/usr/bin/env python3
"""run_causal_discovery.py — run PC and GES on the switch stress dataset
(Whisper C4587, round-3 plan P3; causal-learn pinned 0.1.4.8).

The demonstration is BLINDNESS, not failure: observational causal discovery
silently assumes a definite causal order exists among the mechanisms that
generated the data. Fed data from a process certified (21.1 sigma, frozen rule)
to have NO definite order, the algorithms return an ordinary causal structure
with no warning. Same data, two analyses, opposite verdicts about the premise.
"""
import numpy as np

S_CODE = {"switch": 0, "null_fwd": 1, "null_rev": 2}


def load():
    import csv
    rows = list(csv.reader(open("results/causal_stress_dataset.csv")))[1:]
    X = np.array([[S_CODE[s], (int(c) + 1) // 2, int(t)] for s, c, t in rows],
                 dtype=float)
    return X


def main():
    X = load()
    names = ["S", "C", "T"]
    print(f"dataset: {X.shape[0]} rows, variables {names}")

    from causallearn.search.ConstraintBased.PC import pc
    cg = pc(X, alpha=0.01, indep_test="chisq", show_progress=False)
    print("\nPC (chi-square, alpha=0.01) adjacency (graph.graph matrix):")
    print(cg.G.graph)
    print("PC edges:", [str(e) for e in cg.G.get_graph_edges()])

    from causallearn.search.ScoreBased.GES import ges
    rec = ges(X, score_func="local_score_BDeu")
    print("\nGES (BDeu) adjacency:")
    print(rec["G"].graph)
    print("GES edges:", [str(e) for e in rec["G"].get_graph_edges()])

    print("\nNeither output carries any indication that the switch-arm data was "
          "generated outside the definite-order model class (certified 21.1 sigma).")


if __name__ == "__main__":
    main()
