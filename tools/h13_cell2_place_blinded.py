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
dump=json.load(open(sys.argv[1])); assign=json.load(open(sys.argv[2]))["assignments"]; outdir=sys.argv[3]
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
    json.dump({"encoding":"pm1","records":recs}, open(pth,"w"))
    os.utime(pth,(FIXED_MTIME,FIXED_MTIME))
mapping={a["set_id"]: a["arm"] for a in assign}
print(f"[place] {len(assign)} sets -> {outdir}; all mtimes normalized")
print(f"[place] mapping digest (SEALER's to publish): {hashlib.sha256(json.dumps(mapping,sort_keys=True).encode()).hexdigest()}")
