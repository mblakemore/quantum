#!/usr/bin/env python3
"""Exp142 GRADER DRY-RUN — Elder C6494 (Whisper C4750 P2 assignment: exercise the
frozen grader end-to-end on synthetic answers BEFORE the conventional arm finishes,
so grading day has zero first-runs).

Runs the FROZEN exp142_grader.py (f281deb36ab8..., unmodified, invoked as a
subprocess exactly as it will be on grading day) against synthetic
commitment/reveal/answer fixtures covering every branch:

  T0  REAL-SHAPE JOIN (negative control): commitment written with the REAL sealed
      files' key shape (hash_sha256, per experiments/exp142_commitments/*.json)
      -> grader is expected to CRASH (KeyError 'sha256'). This documents the
      4th untested-production-path find: frozen grader reads c["sha256"], but
      Ember's sealer wrote "hash_sha256". Bridge (no frozen-code edit): grading
      day uses a scratch commitments dir whose files carry BOTH keys.
  T1  ALL-WIN: 4 rungs correct both arms, conforming budgets, ratio >= threshold
      -> per-n WIN x4, overall WIN, exit 0
  T2  BRANCH MATRIX: n4 quantum wrong -> LOSS | n6 conv not identified -> NULL
      | n8 ratio below threshold -> LOSS | n10 budget nonconforming -> LOSS
      -> overall NOT-WIN, exit 1
  T2b CONV MISIDENTIFIED branch: conv identified but P_hat != true P -> NULL
  T3  TAMPERED COMMITMENT: flip a hex char -> INVALID (protocol breach path)
  T4  OVERALL-RULE EDGES: 3 wins incl n8 -> WIN ; 3 wins excl n8 -> NOT-WIN
  T5  REAL ANSWER FILES: my actual wave-2 answers (answers_n{N}_final_elder_c6493)
      renamed to the grader's expected answers_n{N}.json, seals synthesized over
      my own decoded P_hats (no sealed-P access; blindness intact) -> NULL x4
      (identified=false), proving the grader parses the REAL decode_meter output
      schema without adapters.

All fixtures live under a scratch dir; nothing frozen is touched.
"""
import hashlib
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
GRADER = os.path.join(HERE, "exp142_grader.py")
ENS = "fullweight_eps1"
NS = (4, 6, 8, 10)
M99 = {4: 12, 6: 16, 8: 18, 10: 22}
RTH = {4: 1.583333, 6: 9.325000, 8: 73.122222, 10: 537.018182}
PAULI_P = {4: "XXYZ", 6: "ZZXYYX", 8: "XYZXYZXY", 10: "YXZZXYXYZX"}

results = {}


def make_seal(d, n, P, key="both", tamper=False):
    salt = secrets.token_bytes(16)
    digest = hashlib.sha256(salt + f"exp142|{ENS}|{n}|{P}".encode()).hexdigest()
    if tamper:
        digest = ("0" if digest[0] != "0" else "1") + digest[1:]
    c = {"n": n, "ensemble": ENS, "preimage_spec": 'salt_bytes || utf8("exp142|{ensemble}|{n}|{P}")'}
    if key in ("both", "sha256"):
        c["sha256"] = digest
    if key in ("both", "hash_sha256"):
        c["hash_sha256"] = digest
    with open(os.path.join(d, f"commitment_{ENS}_n{n}.json"), "w") as f:
        json.dump(c, f)
    with open(os.path.join(d, f"reveal_{ENS}_n{n}.json"), "w") as f:
        json.dump({"n": n, "ensemble": ENS, "salt_hex": salt.hex(), "P": P}, f)


def make_answers(d, n, qP, qbudget, cP, meter, identified):
    a = {"n": n,
         "quantum": {"P_hat": qP, "meter": M99[n], "shots_budget": qbudget},
         "conventional": {"P_hat": cP, "meter_median": meter,
                          "identified": identified, "overage_submitted": 0}}
    with open(os.path.join(d, f"answers_n{n}.json"), "w") as f:
        json.dump(a, f)


def run_grader(cdir, adir):
    p = subprocess.run([sys.executable, GRADER, cdir, adir],
                       capture_output=True, text=True)
    try:
        out = json.loads(p.stdout)
    except json.JSONDecodeError:
        out = None
    return p.returncode, out, p.stderr.strip().splitlines()[-1] if p.stderr.strip() else ""


def win_meter(n):
    return float(int(RTH[n] * 5 * M99[n]) + 5)  # comfortably above threshold


def loss_meter(n):
    return float(int(RTH[n] * 5 * M99[n]) - 5)  # just below


def scenario(name, seal_key="both", tamper_ns=(), spec=None, use_real_answers=False):
    cdir = tempfile.mkdtemp(prefix=f"exp142dry_{name}_c")
    adir = tempfile.mkdtemp(prefix=f"exp142dry_{name}_a")
    for n in NS:
        make_seal(cdir, n, PAULI_P[n], key=seal_key, tamper=(n in tamper_ns))
        if use_real_answers:
            src = os.path.join(HERE, "..", "results", f"answers_n{n}_final_elder_c6493.json")
            shutil.copy(src, os.path.join(adir, f"answers_n{n}.json"))
        else:
            s = spec[n]
            make_answers(adir, n, s.get("qP", PAULI_P[n]), s.get("qbudget", 5 * M99[n]),
                         s.get("cP", PAULI_P[n]), s.get("meter", win_meter(n)),
                         s.get("identified", True))
    rc, out, err = run_grader(cdir, adir)
    shutil.rmtree(cdir); shutil.rmtree(adir)
    return rc, out, err


WIN = {n: {} for n in NS}

# T0: real sealed-file key shape only -> expect crash (KeyError 'sha256')
rc, out, err = scenario("t0", seal_key="hash_sha256", spec=WIN)
results["T0_real_key_shape"] = {
    "expect": "crash KeyError 'sha256' (4th untested-path find). NOTE: Python "
              "traceback exits rc=1 == the grader's legitimate NOT-WIN exit code — "
              "crash must be discriminated by absent JSON, never by exit code",
    "rc": rc, "stderr_tail": err,
    "pass": out is None and "KeyError: 'sha256'" in err}

# T1: all-WIN
rc, out, _ = scenario("t1", spec=WIN)
results["T1_all_win"] = {
    "expect": "WIN x4, overall WIN, exit 0",
    "rc": rc, "per_n": {k: v["verdict"] for k, v in out["per_n"].items()},
    "overall": out["overall"],
    "pass": rc == 0 and out["overall"] == "WIN"
            and all(v["verdict"] == "WIN" for v in out["per_n"].values())}

# T2: branch matrix
spec = {4: {"qP": "ZZZZ"},                       # quantum wrong -> LOSS
        6: {"cP": None, "meter": None, "identified": False},  # NULL (not identified)
        8: {"meter": loss_meter(8)},              # ratio below -> LOSS
        10: {"qbudget": 111}}                     # budget nonconform -> LOSS
rc, out, _ = scenario("t2", spec=spec)
v = {k: x["verdict"] for k, x in out["per_n"].items()}
results["T2_branch_matrix"] = {
    "expect": "n4 LOSS(quantum) n6 NULL n8 LOSS(ratio) n10 LOSS(budget), NOT-WIN, exit 1",
    "rc": rc, "per_n": v, "reasons": {k: x["reason"][:60] for k, x in out["per_n"].items()},
    "pass": rc == 1 and v == {"4": "LOSS", "6": "NULL", "8": "LOSS", "10": "LOSS"}
            and out["overall"] == "NOT-WIN"}

# T2b: conv misidentified -> NULL
spec = dict(WIN); spec = {n: {} for n in NS}; spec[6] = {"cP": "XXXXXX"}
rc, out, _ = scenario("t2b", spec=spec)
results["T2b_conv_misidentified"] = {
    "expect": "n6 NULL (conv misidentified), others WIN, overall WIN (n8 + 3 wins)",
    "rc": rc, "per_n": {k: x["verdict"] for k, x in out["per_n"].items()},
    "overall": out["overall"],
    "pass": out["per_n"]["6"]["verdict"] == "NULL" and out["overall"] == "WIN"}

# T3: tampered commitment -> INVALID
rc, out, _ = scenario("t3", tamper_ns=(8,), spec={n: {} for n in NS})
results["T3_tampered_commitment"] = {
    "expect": "n8 INVALID -> overall NOT-WIN (n8 required)",
    "rc": rc, "per_n": {k: x["verdict"] for k, x in out["per_n"].items()},
    "overall": out["overall"],
    "pass": out["per_n"]["8"]["verdict"] == "INVALID" and out["overall"] == "NOT-WIN"}

# T4a: 3 wins INCLUDING n8 (n4 NULL) -> WIN
spec = {n: {} for n in NS}; spec[4] = {"cP": None, "meter": None, "identified": False}
rc, out, _ = scenario("t4a", spec=spec)
results["T4a_three_wins_incl_n8"] = {
    "expect": "overall WIN", "overall": out["overall"], "rc": rc,
    "pass": out["overall"] == "WIN" and rc == 0}

# T4b: 3 wins EXCLUDING n8 (n8 NULL) -> NOT-WIN
spec = {n: {} for n in NS}; spec[8] = {"cP": None, "meter": None, "identified": False}
rc, out, _ = scenario("t4b", spec=spec)
results["T4b_three_wins_excl_n8"] = {
    "expect": "overall NOT-WIN (n8 mandatory)", "overall": out["overall"], "rc": rc,
    "pass": out["overall"] == "NOT-WIN" and rc == 1}

# T5: REAL wave-2 answer files (schema join; seals synthesized over MY decoded
# P_hats -- no sealed-P access, blindness intact). n10 conv P_hat is null ->
# use quantum P_hat for the synthetic seal.
real_phats = {}
for n in NS:
    with open(os.path.join(HERE, "..", "results", f"answers_n{n}_final_elder_c6493.json")) as f:
        real_phats[n] = json.load(f)["quantum"]["P_hat"]
PAULI_P.update(real_phats)
rc, out, err = scenario("t5", use_real_answers=True)
results["T5_real_answer_files"] = {
    "expect": "parses real decode_meter output; NULL x4 (identified=false), no crash",
    "rc": rc, "per_n": {k: x["verdict"] for k, x in out["per_n"].items()} if out else None,
    "stderr_tail": err,
    "pass": out is not None and rc == 1
            and all(x["verdict"] == "NULL" for x in out["per_n"].values())}

n_pass = sum(1 for r in results.values() if r["pass"])
summary = {"harness": "exp142_grader_dryrun_elder_c6494.py",
           "grader_sha256_expected_frozen": "f281deb36ab8",
           "tests": results, "passed": n_pass, "total": len(results),
           "all_pass": n_pass == len(results)}
print(json.dumps(summary, indent=2))
out_path = os.path.join(HERE, "exp142_grader_dryrun_results_elder_c6494.json")
with open(out_path, "w") as f:
    json.dump(summary, f, indent=2)
sys.exit(0 if summary["all_pass"] else 1)
