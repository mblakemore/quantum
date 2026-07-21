## Title
Program-set results: `counts` keys are not reversed to little-endian (single-task path reverses; program-set path does not)

## Bug description
When a multi-circuit job is submitted (dispatched as a Braket **program set**), `Result.get_counts()`
returns bitstring keys in **raw Braket qubit order**, i.e. it omits the `[::-1]` little-endian reversal
that the single-circuit path applies. Counts for the same circuit therefore come back with the classical
bits in the opposite order depending only on whether it was submitted alone or in a batch.

This is almost certainly an oversight rather than intended behavior: **within the same program-set
result branch, the `memory` field IS reversed (`shot_result[::-1]`) while `counts` is not** — an internal
inconsistency.

## Version
- qiskit-braket-provider **0.18.1** (please confirm on latest before triage)
- Path of the two branches: `providers/braket_quantum_task.py`
  - single-task: `_result_from_circuit_task()` → `counts = {k[::-1]: v for k, v in dict(result.measurement_counts).items()}  # convert to little-endian`
  - program-set: `BraketQuantumTask.result()` program-set branch → `counts=executable_result.counts` (raw, **not reversed**), while the same branch's `memory=[hex(int("".join(shot_result[::-1]...)))]` **is** reversed.

## Minimal reproducer
Two known-input circuits with asymmetric, deterministic outcomes; submit as a batch (program set) so the
provider takes the program-set path. Truth in qiskit little-endian convention: cal_A → `'01'`, cal_B → `'10'`.

```python
from qiskit import QuantumCircuit
from qiskit_braket_provider import BraketProvider

# cal_A: |q0=1, q1=0>  -> qiskit '01'
a = QuantumCircuit(2, 2); a.x(0); a.x(1); a.cx(0, 1); a.measure([0, 1], [0, 1])
# cal_B: |q0=0, q1=1>  -> qiskit '10'
b = QuantumCircuit(2, 2); b.x(0); b.x(0); b.x(1); b.measure([0, 1], [0, 1])

backend = BraketProvider().get_backend("...")          # any device; verbatim/native as needed
res = backend.run([a, b], shots=100).result()          # >1 circuit -> program set
print(res.get_counts(0), res.get_counts(1))
# EXPECTED: {'01': ~100} {'10': ~100}
# ACTUAL  : {'10': ~100} {'01': ~100}   <-- keys reversed vs the single-task path
```

Submitting each circuit alone (`backend.run([a])`, `backend.run([b])`) returns the **correct** keys —
the discrepancy is exactly the program-set vs single-task path.

## Hardware confirmation
Verified on IonQ Forte-1 (Amazon Braket) with the reproducer above: cal_A read `'10'` at 0.99, cal_B
read `'01'` at 1.00 — i.e. the recorded keys are unreversed raw-Braket order. (This surfaced as a
spurious "failed" experiment result that was traced to the decode, then confirmed with this known-input
calibration.)

## Impact
Any analysis that reads multi-circuit results through `get_counts()` and assumes qiskit little-endian
order will silently mis-decode the classical register. Outcome-symmetric distributions (e.g. GHZ-type
`'00'`/`'11'`) are invisible to the swap, so the bug can hide inside passing pipelines and only manifest
on circuits with asymmetric deterministic outcomes.

## Suggested fix
Reverse the program-set `counts` keys to match the single-task path (and, ideally, add a known-input
regression test that submits an asymmetric circuit both alone and in a batch and asserts identical keys):

```python
counts={k[::-1]: v for k, v in executable_result.counts.items()},   # match _result_from_circuit_task
```
