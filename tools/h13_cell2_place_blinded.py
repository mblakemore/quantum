#!/usr/bin/env python3
"""STEP 2 of 2 — THE SEALER RUNS THIS. No IBM credentials needed, no network.

Takes Whisper's raw dump + a permutation the SEALER generates from her own off-git secret, and
emits the blinded directory. The secret never leaves the sealer's seat; Whisper never sees a
set_id. Contains NO RNG for the assignment — the sealer supplies it — but DOES normalise mtimes
so write order leaks nothing (Ember's filesystem channel).

Usage: python3 tools/h13_cell2_place_blinded.py <dump.json> <sealer_permutation.json> <outdir>
  sealer file: {"assignments":[{"set_id":"<opaque>","unit":<int>,"arm":"CE"|"CC"}, ...]}
"""
import json, os, sys, hashlib
FIXED_MTIME=1000000000
if len(sys.argv)<4: sys.exit("usage: place_blinded.py <dump.json> <sealer_permutation.json> <outdir>")
dump=json.load(open(sys.argv[1])); _payloads=[]
assign=json.load(open(sys.argv[2]))["assignments"]; outdir=sys.argv[3]
sets=dump["sets"]
if len(assign)!=len(sets): sys.exit(f"REFUSING: {len(assign)} assignments vs {len(sets)} sets")
os.makedirs(outdir,exist_ok=True)
for a in assign:
    k=f"{a['unit']}|{a['arm']}"
    if k not in sets: sys.exit(f"REFUSING: assignment references unknown set {k}")
    recs=[]
    for b in ("X","Y","Z"):
        # ENCODING DECLARED AT PLACEMENT: bit 0 -> +1, bit 1 -> -1 (Ember Option C)
        recs += [{"basis":b+b,"a":1 if x==0 else -1,"b":1 if y==0 else -1} for x,y in sets[k][b]]
    pth=os.path.join(outdir,f"{a['set_id']}.json")
    # ══ CONSTANT-WIDTH PAD — LEAK 11 (Ember general#9874, Elder ruling #9881) ═══════════════
    # `-1` is TWO characters and `1` is ONE, so JSON file size was EXACTLY LINEAR in the -1
    # count (2 bytes per negative, reproduced from scratch) — hence linear in the correlator,
    # hence a perfect arm discriminator. Ember measured 72 distinct sizes across 80 files with
    # CE and CC ranges NOT OVERLAPPING: a single size threshold classified all 80 at 100%.
    # `ls -l` WAS A COMPLETE DECODER, and she caught it only by re-running the FULL v1 custody
    # sweep rather than checking only what v2 changed.
    #
    # THE FIX IS SERIALISATION, NOT SEMANTICS (Elder's ruling): his decoder is FROZEN at
    # sha256 321abc99 and its _pm() REFUSES anything not in (1,-1) — Ember's "+1"/"-1" strings
    # would make every record REFUSED, fail-closed but undecodable. So values stay INTEGERS and
    # records stay EXACTLY {"basis","a","b"}; the pad goes at the TOP LEVEL, where it cannot
    # touch a record his decoder reads. Re-freezing was available and declined: a decoder
    # re-frozen after the producer's format is known is a decoder FITTED to a format, and every
    # re-freeze spends the pre-commitment the whole claim rests on.
    body={"encoding":"pm1","records":recs}
    _payloads.append((pth, body))
    os.utime(pth,(FIXED_MTIME,FIXED_MTIME)) if False else None
# SECOND PASS: equalise every file to a common length. Done AFTER all bodies are known,
# because the pad width depends on the LARGEST set — a per-file pad computed in isolation
# cannot know the target. Written here, not in the loop, so the invariant is visible.
_raw = {p: json.dumps(b) for p, b in _payloads}
_target = max(len(v) for v in _raw.values()) + 16          # +16 leaves room for the pad key itself
for pth, body in _payloads:
    need = _target - len(json.dumps(body)) - len(',"pad":""')
    body["pad"] = "." * max(0, need)
    out = json.dumps(body)
    if len(out) != _target:                                 # exact, or refuse — no near-enough
        body["pad"] = "." * max(0, len(body["pad"]) + (_target - len(out)))
        out = json.dumps(body)
    open(pth, "w").write(out)
    os.utime(pth, (FIXED_MTIME, FIXED_MTIME))
_sizes = {os.path.getsize(p) for p, _ in _payloads}
if len(_sizes) != 1:
    sys.exit(f"🔴 REFUSING: file sizes are not constant ({len(_sizes)} distinct) — the leak-11 "
             f"channel is OPEN. Sizes: {sorted(_sizes)[:5]}")
print(f"[place] all {len(_payloads)} files byte-identical in length: {_sizes.pop():,} B (leak-11 channel closed)")

mapping={a["set_id"]: a["arm"] for a in assign}
print(f"[place] {len(assign)} sets -> {outdir}; all mtimes normalized")
print(f"[place] mapping digest (SEALER's to publish): {hashlib.sha256(json.dumps(mapping,sort_keys=True).encode()).hexdigest()}")
