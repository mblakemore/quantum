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


def run_grouped(backend, pubs, is_qpu, manifest_path):
    """Run pubs (label, qc, shots) grouped by shot-count. Returns {label: counts}.
    On a real device, task handles are persisted to manifest_path BEFORE blocking on
    results, so a long queue / client death never loses the paid-for tasks.

    QPU path uses native=True: the provider compiles the abstract circuit to the device's
    Target-native, angle-restricted gate set (Rigetti: Rx/Rz/CZ) and wraps it in a verbatim
    box. This is the ONLY path that avoids BOTH failure modes hit earlier — the non-standard
    basis_gates parse crash (native uses target, basis_gates=None) AND verbatim gate-name
    strictness (native compiles to the RIGHT natives, so the verbatim box validates). The
    verbatim box also pins placement (no Braket rewiring)."""
    by_shots = defaultdict(list)
    for lab, qc, shots in pubs:
        by_shots[shots].append((lab, qc))  # pass abstract; native=True compiles it

    # Phase 1: submit every group, capture handles, persist immediately.
    submitted = []  # (labels, job)
    handles = []
    for shots, items in by_shots.items():
        labels = [lab for lab, _ in items]
        circuits = [c for _, c in items]
        print(f"  submitting {len(circuits)} circuits @ {shots} shots "
              f"({'native-verbatim QPU' if is_qpu else 'local'}) ...", flush=True)
        job = backend.run(circuits, shots=shots, native=True) if is_qpu else backend.run(circuits, shots=shots)
        submitted.append((labels, job))
        try:
            handles.append({"shots": shots, "labels": labels, "job_id": str(job.job_id())})
        except Exception as e:  # noqa: BLE001 — never let handle-capture failure lose the job
            handles.append({"shots": shots, "labels": labels, "job_id": f"<unknown:{e}>"})
        # Persist INCREMENTALLY (after each group) so a later group's failure can never
        # orphan an already-charged group's task handles.
        if manifest_path:
            json.dump({"handles": handles}, open(manifest_path, "w"), indent=1)
            print(f"  task handles persisted ({len(handles)} group(s)) -> {manifest_path}")

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
    ap.add_argument("--canary", action="store_true",
                    help="cheap format-validation: 4 witness pubs @ 500 shots only (~$2), not the frozen run")
    args = ap.parse_args()

    pubs = build_causal()
    if args.canary:
        pubs = [(lab, qc, 500) for lab, qc, s in pubs if lab.startswith("w_")]
        print("CANARY MODE — 4 witness circuits @ 500 shots (format check + prelim W; NOT the frozen axis)")
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
    tag = (args.device + ("_canary" if args.canary else "")) if args.submit else "localscan"
    manifest_path = os.path.join(QROOT, "results", f"braket_causal_{tag}_manifest.json") if args.submit else None
    if which != "local":
        layout, cz_err = best_pair(backend)
        print(f"device best CZ edge (informational): {layout} err={cz_err:.5f}. "
              f"native=True verbatim-boxes on the default label map (phys [0,1], a top-5 CZ edge) — "
              f"placement pinned, not Braket-rewired.")

    counts = run_grouped(backend, pubs, is_qpu=(which != "local"), manifest_path=manifest_path)

    out = {"backend": backend.name, "mode": ("submit:" + args.device) if args.submit else "scan:local",
           "pinned_pair": layout}
    print("=" * 62)
    print(f"SWITCH-BENCH CAUSAL AXIS — {backend.name}")
    print("=" * 62)
    if args.canary:
        print("CANARY — raw counts (verify 2-bit keys, sensible distribution):")
        for lab in ("w_start_c", "w_start_a", "w_end_c", "w_end_a"):
            print(f"  {lab}: {counts[lab]}")
        # prelim W (witness only): <X_c> read on 2nd bit, comm - anti
        x = {}
        for rep in ("start", "end"):
            for kind in ("c", "a"):
                c = counts[f"w_{rep}_{kind}"]; n = sum(c.values())
                x[(rep, kind)] = (sum(v for k, v in c.items() if k[1] == "0")
                                  - sum(v for k, v in c.items() if k[1] == "1")) / n
        Wprelim = sum(x[(r, "c")] - x[(r, "a")] for r in ("start", "end")) / 2
        keys_ok = all(len(k) == 2 for lab in counts for k in counts[lab])
        print(f"  2-bit-key format OK: {keys_ok}")
        print(f"  PRELIM W (noisy, 500 shots): {Wprelim:+.3f}  (ideal 2.0, causal-mix 0; full run uses 4000)")
        verdict = f"CANARY(format_ok={keys_ok}, Wprelim={Wprelim:+.3f})"
        out["verdict"] = verdict
    else:
        verdict = grade_causal(counts, {}, out)
        out["verdict"] = verdict

    outpath = os.path.join(QROOT, "results", f"braket_causal_{tag}.json")
    json.dump({"card": out, "counts": counts}, open(outpath, "w"), indent=1, default=float)
    print(f"card -> {outpath}")
    return 0 if verdict == "PASS-CAUSAL" else 1


if __name__ == "__main__":
    sys.exit(main())
