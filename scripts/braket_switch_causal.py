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
    last = arn.split("/")[-1]
    variants = {last, last.replace("-", " "), last.replace(" ", "-")}  # "Forte-1" vs "Forte 1"
    backends = BraketProvider().backends()
    for b in backends:
        if b.name in variants:
            return b
    raise SystemExit(f"backend {last} not found; available: {[b.name for b in backends]}")


def best_pair(backend):
    """Frozen protocol = re-derive site selection live on the device map. Pick the
    lowest-CZ-error connected edge (mirrors the IBM bench's pick_pair). Returns (None, None)
    for devices with no CZ in the native set (e.g. IonQ = GPI/GPI2/MS, all-to-all)."""
    tgt = backend.target
    if "cz" not in getattr(tgt, "operation_names", []):
        return None, None
    edges = [(p.error, tuple(qs)) for qs, p in tgt["cz"].items()
             if p is not None and getattr(p, "error", None) is not None]
    if not edges:
        return None, None
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
            c = result.get_counts(i) if len(labels) > 1 else result.get_counts()
            if is_qpu and len(labels) > 1:
                c = _programset_key_fix(c)
            counts[lab] = c
    return counts


def _programset_key_fix(counts):
    """C4946 certified decode correction: qiskit-braket-provider's PROGRAM-SET result branch
    returns counts keyed in RAW braket qubit order — it omits the [::-1] little-endian reversal
    that the single-task path applies (braket_quantum_task.py: the branch's own `memory` field
    reverses, `counts` does not). Certified by known-input program-set calibration on IonQ
    Forte-1 (task 675bf4b2, C4946: entangled known '01' read '10' @0.99; gate-free known '10'
    read '01' @1.00). Multi-circuit QPU jobs (len>1 -> program set) need the reversal restored.
    Pinned to certified provider versions — on upgrade, RE-CERTIFY with
    `ionq_bitorder_cal.py --program-set` before trusting either orientation."""
    from importlib.metadata import version
    v = version("qiskit_braket_provider")
    if v not in {"0.18.1"}:
        raise SystemExit(f"program-set key fix certified only for qiskit-braket-provider 0.18.1; "
                         f"found {v} — re-certify with ionq_bitorder_cal.py --program-set first")
    return {k[::-1]: n for k, n in counts.items()}


def build_matched_null(prep, a, b):
    """Exp212: copy the WITNESS circuit (definite=False) VERBATIM, replacing ONLY the initial
    control prep h(0) with |0> (removed, prep=0) or |1> (x(0), prep=1). Everything downstream —
    the 4 controlled-unitaries (4 CZ) and the final h(0) + measurements — is instruction-identical
    to the witness, so it belongs to the witness's compilation class (the Exp211b lesson: the
    gate-free definite=True control compiled in a different class and its counts bookkeeping
    failed). A 50/50 classical mixture of these two definite orders is causally separable ->
    W_matched = 0 by theorem."""
    from qiskit import QuantumCircuit
    from exp106_capacity_activation import build_circuit
    w = build_circuit(a, b, 0, definite=False)
    qc = QuantumCircuit(2, 2)
    if prep == 1:
        qc.x(0)
    skipped = False
    for inst in w.data:
        if not skipped and inst.operation.name == "h" and w.find_bit(inst.qubits[0]).index == 0:
            skipped = True
            continue
        qc.append(inst.operation, inst.qubits, inst.clbits)
    assert skipped, "witness initial h(0) not found — matched-null construction invalid"
    # STRUCTURE ASSERT (Exp212 G1): identical 2q-op count vs the witness — the whole point.
    n2q = lambda c: sum(1 for i in c.data if len(i.qubits) == 2)
    assert n2q(qc) == n2q(w), f"matched-null 2q count {n2q(qc)} != witness {n2q(w)}"
    return qc


def grade_matched(counts, shots, out):
    """Exp212 grader — frozen BEFORE flight (see pre-registration).
    Grades ALL classical bits (the C4943 lesson: an ungraded deterministic marginal hid the
    Exp211b artifact): per-pub target marginal (comm t=0, anti t=1, deterministic ideally),
    control marginal (~50/50 ideally), per-prep bands, mixture band, and the three-branch
    reading rule (restore / null-fail / witness-no-refire)."""
    import numpy as np

    def xc_se(lab):
        c = counts[lab]; n = sum(c.values())
        m = (sum(v for k, v in c.items() if k[1] == "0")
             - sum(v for k, v in c.items() if k[1] == "1")) / n
        return m, float(np.sqrt(max(1e-12, 1.0 - m * m) / n))

    print("  MATCHED-NULL (structurally-identical definite-order control, D0/D1)")
    marg, marg_ok = {}, True
    for p in (0, 1):
        for kind, t_expect in (("c", "0"), ("a", "1")):
            lab = f"mnull_d{p}_{kind}"
            c = counts[lab]; n = sum(c.values())
            pt = sum(v for k, v in c.items() if k[0] == t_expect) / n
            pc0 = sum(v for k, v in c.items() if k[1] == "0") / n
            ok = (pt >= 0.85) and (0.30 <= pc0 <= 0.70)
            marg[lab] = {"P_target_expected": pt, "P_c0": pc0, "ok": ok}
            marg_ok &= ok
            print(f"    {lab}: {dict(c)}  P(t={t_expect})={pt:.3f} (>=0.85)  "
                  f"P(c=0)={pc0:.3f} (in [0.30,0.70])  {'OK' if ok else 'MARGINAL-FAIL'}")
    W_prep, se_prep = {}, {}
    for p in (0, 1):
        mc, sec = xc_se(f"mnull_d{p}_c"); ma, sea = xc_se(f"mnull_d{p}_a")
        W_prep[p], se_prep[p] = mc - ma, float(np.hypot(sec, sea))
        print(f"    W_D{p} = {W_prep[p]:+.4f} ± {se_prep[p]:.4f}   (band |W| <= 0.3)")
    W_m = 0.5 * (W_prep[0] + W_prep[1])
    se_m = 0.5 * float(np.hypot(se_prep[0], se_prep[1]))
    null_ok = (abs(W_m) <= 0.3 and abs(W_prep[0]) <= 0.3 and abs(W_prep[1]) <= 0.3 and marg_ok)
    print(f"    W_matched = {W_m:+.4f} ± {se_m:.4f}   (causally-separable theorem: 0; band <= 0.3)")
    print(f"    null_ok = {null_ok}  (mixture band + per-prep bands + all-bit marginals)")
    # same-window witness re-certification under the ORIGINAL Exp211 rule
    witness_recert = (out["W"] >= 1.3) and (out["W"] - 5 * out["seW"] > 0)
    sep = out["W"] - W_m
    se_sep = float(np.hypot(out["seW"], se_m))
    print(f"    separation W_witness - W_matched = {sep:+.4f} ± {se_sep:.4f} "
          f"({sep / se_sep:.1f} sigma; rule: > 1.0)")
    if null_ok and witness_recert and sep > 1.0:
        verdict = "LOOPHOLE-CLOSED(restore)"
    elif not null_ok:
        verdict = "NULL-FAIL(stays-withdrawn)"
    else:
        verdict = "WITNESS-NO-REFIRE(stays-withdrawn)"
    print(f"    verdict: {verdict}")
    out.update({"W_matched": W_m, "se_matched": se_m, "W_D0": W_prep[0], "W_D1": W_prep[1],
                "marginals": marg, "null_ok": null_ok, "witness_recert": witness_recert,
                "separation": sep, "se_separation": se_sep, "matched_verdict": verdict})
    return verdict


def grade_witness(counts, shots, out):
    """Witness-only W (the 4 w_ pubs) graded vs the causal-mixture bound 0. For cost-frugal
    flights where the full 68-pub / 112k-shot axis is unaffordable (IonQ at $0.08/shot). The
    BOUND is the same theory constant (0); only the shot count (hence seW) differs from the
    frozen bench — fewer shots widen the error bar, they do NOT retune the bound."""
    import numpy as np
    x = {}
    for rep in ("start", "end"):
        for kind in ("c", "a"):
            c = counts[f"w_{rep}_{kind}"]; n = sum(c.values())
            x[(rep, kind)] = (sum(v for k, v in c.items() if k[1] == "0")
                              - sum(v for k, v in c.items() if k[1] == "1")) / n
    W = float(np.mean([x[(r, "c")] - x[(r, "a")] for r in ("start", "end")]))
    seW = float(np.sqrt(2 * 2 / (2 * shots)))   # switch_bench formula, actual shots
    verdict = "WITNESS-FIRED" if (W - 5 * seW > 0) else "WITNESS-FAIL"
    print("  CAUSAL WITNESS (W only)")
    print(f"  W (witness DISC)   {W:+.4f} ± {seW:.4f}   ideal 2.0 | causal-mixture bound 0")
    print(f"  W - 5*seW = {W - 5*seW:+.4f}   ({W/seW:.1f} sigma over 0)   verdict: {verdict}")
    out.update({"W": W, "seW": seW, "shots": shots, "witness_verdict": verdict})
    return verdict


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true", help="FREE local-sim validation")
    ap.add_argument("--submit", action="store_true", help="SPEND on a real QPU")
    ap.add_argument("--device", choices=list(DEVICE), default="rigetti")
    ap.add_argument("--canary", action="store_true",
                    help="cheap format-validation: 4 witness pubs @ 500 shots only, not the frozen run")
    ap.add_argument("--witness-only", action="store_true",
                    help="run only the 4 witness pubs; grade W vs the causal-mixture bound 0 (cost-frugal)")
    ap.add_argument("--smoke", action="store_true",
                    help="1 witness circuit @ 100 shots — cheapest QPU format/port check")
    ap.add_argument("--null-witness", action="store_true",
                    help="definite-order control (definite=True): expect W~0, closes the compiler-mapping loophole")
    ap.add_argument("--matched-null", action="store_true",
                    help="Exp212: witness 4 pubs + structurally-matched definite-order null 4 pubs "
                         "(D0/D1 x comm/anti), ONE submission batch = same-window; frozen 3-branch reading rule")
    ap.add_argument("--shots", type=int, default=None, help="override shots per pub")
    args = ap.parse_args()

    pubs = build_causal()
    if args.matched_null:
        sh = args.shots if args.shots else 100
        pubs = [(lab, qc, sh) for lab, qc, s in pubs if lab.startswith("w_")]
        for p in (0, 1):
            for pair, kind in ((("X", "X"), "c"), (("X", "Z"), "a")):
                pubs.append((f"mnull_d{p}_{kind}", build_matched_null(p, *pair), sh))
        print(f"EXP212 MATCHED-NULL — witness 4 + matched null 4 (D0/D1 x comm/anti) @ {sh} shots, "
              f"one submission batch (same-window)")
    elif args.null_witness:
        from exp106_capacity_activation import build_circuit
        sh = args.shots if args.shots else 100
        pubs = [("wnull_c", build_circuit("X", "X", 0, definite=True), sh),
                ("wnull_a", build_circuit("X", "Z", 0, definite=True), sh)]
        print(f"NULL-WITNESS — 2 DEFINITE-ORDER circuits (comm+anti) @ {sh} shots — causal-mixture control, expect W~0")
    elif args.smoke:
        pubs = [(lab, qc, 100) for lab, qc, s in pubs if lab in ("w_start_c", "w_start_a")]
        print("SMOKE — 2 witness circuits (comm+anti) @ 100 shots — SEMANTIC port check (~$16.60 on IonQ)")
    elif args.witness_only or args.canary:
        sh = args.shots if args.shots else 500
        pubs = [(lab, qc, sh) for lab, qc, s in pubs if lab.startswith("w_")]
        print(f"WITNESS-ONLY — 4 witness circuits @ {sh} shots (W vs causal-mixture bound; not the full frozen axis)")
    elif args.shots:
        pubs = [(lab, qc, args.shots) for lab, qc, s in pubs]
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
    suffix = ("_matched" if args.matched_null else "_null" if args.null_witness
              else "_smoke" if args.smoke
              else "_witness" if (args.witness_only or args.canary) else "")
    tag = (args.device + suffix) if args.submit else "localscan"
    manifest_path = os.path.join(QROOT, "results", f"braket_causal_{tag}_manifest.json") if args.submit else None
    if which != "local":
        layout, cz_err = best_pair(backend)
        if layout is not None:
            print(f"device best CZ edge (informational): {layout} err={cz_err:.5f}. "
                  f"native=True verbatim-boxes on the default label map — placement pinned.")
        else:
            print(f"{backend.name}: no CZ in native set (all-to-all / non-CZ device) — "
                  f"native=True compiles to the device's own natives + verbatim box.")

    counts = run_grouped(backend, pubs, is_qpu=(which != "local"), manifest_path=manifest_path)

    out = {"backend": backend.name, "mode": ("submit:" + args.device) if args.submit else "scan:local",
           "pinned_pair": layout}
    print("=" * 62)
    print(f"SWITCH-BENCH CAUSAL AXIS — {backend.name}")
    print("=" * 62)
    if args.matched_null:
        shots = pubs[0][2]
        print("  raw witness counts:", {lab: counts[lab] for lab in ("w_start_c", "w_start_a", "w_end_c", "w_end_a")})
        grade_witness(counts, shots, out)
        verdict = grade_matched(counts, shots, out)
    elif args.null_witness:
        import numpy as np
        def xc(lab):
            c = counts[lab]; n = sum(c.values())
            return (sum(v for k, v in c.items() if k[1] == "0")
                    - sum(v for k, v in c.items() if k[1] == "1")) / n
        W_def = xc("wnull_c") - xc("wnull_a")
        shots = pubs[0][2]
        seW = float(np.sqrt(2.0 / shots))   # 2 arms, var<=1 each, 1 rep
        # closes the compiler-mapping loophole: a faithful compilation MUST give W~0 for a
        # definite-order (causally-separable) process. Pre-registered band |W_def| < 0.3.
        closed = abs(W_def) < 0.3
        sep_sigma = (1.894 - W_def) / float(np.sqrt(seW**2 + 0.0632**2))
        print(f"NULL-WITNESS (definite-order control)")
        print(f"  wnull_c: {counts['wnull_c']}")
        print(f"  wnull_a: {counts['wnull_a']}")
        print(f"  W_definite = {W_def:+.4f} ± {seW:.4f}   (expect ~0; switch W was +1.894)")
        print(f"  |W_def| < 0.3 band: {closed}   |   separation from switch: {sep_sigma:.1f} sigma")
        verdict = "NULL-CLOSED" if closed else "NULL-FAIL(artifact?)"
        print(f"  verdict: {verdict}")
        out.update({"W_definite": W_def, "seW": seW, "shots": shots, "verdict": verdict})
    elif args.smoke:
        def xc(lab):
            c = counts[lab]; n = sum(c.values())
            return (sum(v for k, v in c.items() if k[1] == "0")
                    - sum(v for k, v in c.items() if k[1] == "1")) / n
        comm = xc("w_start_c"); anti = xc("w_start_a")
        keys_ok = all(len(k) == 2 for lab in ("w_start_c", "w_start_a") for k in counts[lab])
        # SEMANTIC check (the null arm's job, done cheaply up front — witness-only has no null
        # downstream): comm must read strongly + (00-dominated), anti strongly - (11-dominated).
        # A wrong qubit mapping / flipped bit convention from native compilation fails this.
        sem_ok = keys_ok and comm > 0.5 and anti < -0.5
        print(f"SMOKE — w_start_c: {counts['w_start_c']}")
        print(f"        w_start_a: {counts['w_start_a']}")
        print(f"  <X_c>_comm = {comm:+.3f} (expect strongly +, 00-dominated)")
        print(f"  <X_c>_anti = {anti:+.3f} (expect strongly -, 11-dominated)")
        print(f"  format_ok={keys_ok}  SEMANTIC_ok={sem_ok}  (mapping+convention survived native compile)")
        verdict = f"SMOKE(semantic_ok={sem_ok})"
        out.update({"comm": comm, "anti": anti, "verdict": verdict})
    elif args.witness_only or args.canary:
        shots = pubs[0][2]
        print("  raw witness counts:", {lab: counts[lab] for lab in ("w_start_c", "w_start_a", "w_end_c", "w_end_a")})
        verdict = grade_witness(counts, shots, out)
        out["verdict"] = verdict
    else:
        verdict = grade_causal(counts, {}, out)
        out["verdict"] = verdict

    outpath = os.path.join(QROOT, "results", f"braket_causal_{tag}.json")
    json.dump({"card": out, "counts": counts}, open(outpath, "w"), indent=1, default=float)
    print(f"card -> {outpath}")
    return 0 if (verdict == "PASS-CAUSAL" or "FIRED" in verdict or "CLOSED" in verdict or "semantic_ok=True" in verdict) else 1


if __name__ == "__main__":
    sys.exit(main())
