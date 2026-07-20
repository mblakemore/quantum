#!/usr/bin/env python3
"""
Switch-bench CAUSAL axis, ported to Amazon Braket — the cross-PLATFORM causal-order exam.

Reuses the FROZEN circuit builder `build_causal()` and the FROZEN grader `grade_causal()`
from tools/switch_bench.py VERBATIM — no retuning, no re-derived bounds. Only the submit
path changes (IBM Runtime SamplerV2 -> qiskit-braket-provider). The bit-ordering convention
is preserved because both paths read counts through qiskit's get_counts().

Frozen theory bounds (identical to every Heron flight):
  W    (witness DISC)  ideal 2.0  | causal-mixture 0   ; PASS if W - 5*seW > 0
  Rbar (capacity)      ideal 0.5333 | causal 0         ; PASS if R - 5*seR > 0.10
  D    (null integrity)                                 ; NO-TEST unless |D| + 5*seD < 0.10
  PASS-CAUSAL requires all three.

Usage:
  python3 braket_switch_causal.py --scan                     # FREE: run on Braket LOCAL sim -> expect ideal PASS-CAUSAL
  python3 braket_switch_causal.py --submit --device rigetti  # SPEND (~$68): Rigetti Cepheus-1-108Q
  python3 braket_switch_causal.py --submit --device ionq     # SPEND (headline): IonQ Forte-1
"""
import os, sys, json, argparse
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
QROOT = os.path.join(HERE, "..")
for p in ("experiments", "scripts", "tools"):
    sys.path.insert(0, os.path.join(QROOT, p))

from switch_bench import build_causal, grade_causal  # FROZEN builder + grader

DEVICE = {
    "rigetti": ("arn:aws:braket:us-west-1::device/qpu/rigetti/Cepheus-1-108Q", 0.000425),
    "ionq":    ("arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1",           0.08),
}
TASK_FEE = 0.30


def get_backend(which):
    if which == "local":
        from qiskit_braket_provider import BraketLocalBackend
        return BraketLocalBackend()
    from qiskit_braket_provider import BraketProvider
    arn = DEVICE[which][0]
    name = arn.split("/")[-1]
    for b in BraketProvider().backends():
        if b.name == name:
            return b
    raise SystemExit(f"backend {name} not found; available: {[b.name for b in BraketProvider().backends()]}")


def best_pair(backend):
    """Frozen protocol = re-derive site selection live on the device map. Pick the
    lowest-CZ-error connected edge (mirrors the IBM bench's pick_pair)."""
    cz = backend.target["cz"]
    edges = [(p.error, tuple(qs)) for qs, p in cz.items()
             if p is not None and getattr(p, "error", None) is not None]
    edges.sort()
    return list(edges[0][1]), edges[0][0]


def run_grouped(backend, pubs, do_transpile, layout, manifest_path):
    """Run pubs (label, qc, shots) grouped by shot-count. Returns {label: counts}.
    On a real device, task handles are persisted to manifest_path BEFORE blocking on
    results, so a long queue / client death never loses the paid-for tasks."""
    from qiskit import transpile
    by_shots = defaultdict(list)
    for lab, qc, shots in pubs:
        tqc = (transpile(qc, backend, initial_layout=layout, seed_transpiler=4619,
                         optimization_level=1) if do_transpile else qc)
        by_shots[shots].append((lab, tqc))

    # Phase 1: submit every group, capture handles, persist immediately.
    submitted = []  # (labels, job)
    handles = []
    for shots, items in by_shots.items():
        labels = [lab for lab, _ in items]
        circuits = [c for _, c in items]
        print(f"  submitting {len(circuits)} circuits @ {shots} shots ...", flush=True)
        job = backend.run(circuits, shots=shots)
        submitted.append((labels, job))
        try:
            handles.append({"shots": shots, "labels": labels, "job_id": str(job.job_id())})
        except Exception as e:  # noqa: BLE001 — never let handle-capture failure lose the job
            handles.append({"shots": shots, "labels": labels, "job_id": f"<unknown:{e}>"})
    if manifest_path:
        json.dump({"handles": handles}, open(manifest_path, "w"), indent=1)
        print(f"  task handles persisted -> {manifest_path}")

    # Phase 2: block on results (may be a long queue — no timeout wrapper on this call).
    counts = {}
    for labels, job in submitted:
        result = job.result()
        for i, lab in enumerate(labels):
            counts[lab] = result.get_counts(i) if len(labels) > 1 else result.get_counts()
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true", help="FREE local-sim validation")
    ap.add_argument("--submit", action="store_true", help="SPEND on a real QPU")
    ap.add_argument("--device", choices=list(DEVICE), default="rigetti")
    args = ap.parse_args()

    pubs = build_causal()
    total_shots = sum(s for _, _, s in pubs)
    if args.submit:
        per_shot = DEVICE[args.device][1]
        cost = len(pubs) * TASK_FEE + total_shots * per_shot
        print(f"COST ESTIMATE on {args.device}: {len(pubs)} tasks x ${TASK_FEE} + "
              f"{total_shots} shots x ${per_shot} = ${cost:.2f}")

    which = args.device if args.submit else "local"
    backend = get_backend(which)
    print(f"backend: {backend.name}  ({'LOCAL — FREE' if which=='local' else 'QPU — SPEND'})")

    layout = None
    tag = args.device if args.submit else "localscan"
    manifest_path = os.path.join(QROOT, "results", f"braket_causal_{tag}_manifest.json") if args.submit else None
    if which != "local":
        layout, cz_err = best_pair(backend)
        print(f"pinned pair (frozen protocol: best live CZ edge): {layout}  CZ_err={cz_err:.5f}")

    counts = run_grouped(backend, pubs, do_transpile=(which != "local"),
                         layout=layout, manifest_path=manifest_path)

    out = {"backend": backend.name, "mode": ("submit:" + args.device) if args.submit else "scan:local",
           "pinned_pair": layout}
    print("=" * 62)
    print(f"SWITCH-BENCH CAUSAL AXIS — {backend.name}")
    print("=" * 62)
    verdict = grade_causal(counts, {}, out)
    out["verdict"] = verdict

    outpath = os.path.join(QROOT, "results", f"braket_causal_{tag}.json")
    json.dump({"card": out, "counts": counts}, open(outpath, "w"), indent=1, default=float)
    print(f"card -> {outpath}")
    return 0 if verdict == "PASS-CAUSAL" else 1


if __name__ == "__main__":
    sys.exit(main())
