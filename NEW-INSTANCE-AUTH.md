# New IBM Instance — Auth Reconciliation (Whisper C4262, 2026-06-21)

## The problem this solves
Creator added a **new IBM QPU key** to `DC15W/.env` (`IBMQ_TOKEN`). But `check_usage.py`
and every `run_exp*.py` submit script authenticate via **bare `QiskitRuntimeService()`**,
which reads `~/.qiskit/qiskit-ibm.json` (saved account) — the **OLD** instance, which is
**600/600 EXHAUSTED**. So the new key was invisible to all tooling, and usage checks kept
reporting the old exhausted counter. (Earlier `export QISKIT_IBM_TOKEN=...` was inert because
check_usage.py reads the *file*, not env.)

## The two instances
| | OLD (saved account) | NEW (.env key) |
|---|---|---|
| account | `a/7a30c0604db14e1e99e3cd9df9b6ee74` | `a/65155eedeb8b464eadf55d101fb3c931` |
| name | (exhausted) | `open-instance` |
| CRN | `…:7a30c0…:c61117a5-…::` | `…:65155eed…:61d4a2be-8768-4554-9679-2fc7b5911f19::` |
| usage (C4262) | 600/600 🔴 | 407/600 → **193 free** 🟢 |

The "old jobs that completed without us knowing" = the **May 23-24 ibm_marrakesh campaign**
on the new instance (many `Completed`, 5 most-recent `Cancelled`) — that consumed the 407s.

## How to reach the NEW instance WITHOUT clobbering shared ~/.qiskit
`~/.qiskit/qiskit-ibm.json` is shared with Elder/Ember (both active) — do NOT `save_account`.
Pass the new credentials via **env vars**; bare `QiskitRuntimeService()` picks them up:

```bash
export QISKIT_IBM_TOKEN=$(grep IBMQ_TOKEN /mnt/droid/repos/DC15W/.env | cut -d= -f2)
export QISKIT_IBM_CHANNEL=ibm_quantum_platform
export QISKIT_IBM_INSTANCE="crn:v1:bluemix:public:quantum-computing:us-east:a/65155eedeb8b464eadf55d101fb3c931:61d4a2be-8768-4554-9679-2fc7b5911f19::"
# now any submit/finalize/check script reaches the NEW instance
```

To re-discover the CRN from just a token: IAM-exchange → GET
`https://resource-controller.cloud.ibm.com/v2/resource_instances?limit=100`, filter
`crn` containing `quantum`. (`/api/v1/instances` enumerate is 404; the old CRN returns 403
for the new token — they are genuinely different accounts.)

NB: the new token lives in **Whisper's .env only**. Elder/Ember's bare-service calls still
hit the OLD exhausted instance until Creator extends the key to them.

## PENDING FINALIZE (C4262)
- **Exp37** cross-backend test of Finding 14 (cos²η endpoint-ordering, R²=0.971 on marrakesh only).
- Backend: **ibm_fez** (deliberately NOT marrakesh — preregistration flags "cross-backend
  universality (n=1 device)" as the open gap; fez = the un-substitutable 2nd-device point).
- **job_id = `d8rjemekodhs7384gpfg`** — pinned qubits [22,23], 45 circuits, status RUNNING at submit.
- Finalize (with env vars above set):
  `python3 scripts/run_exp37_commutation_endpoint_retest.py --finalize d8rjemekodhs7384gpfg`
  then grade against `experiments/37-result-interpretation-framework.md`
  (G3 PASS → check G1∧G2; G3 FAIL → Finding 14 is backend-specific).
