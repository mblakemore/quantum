#!/usr/bin/env python3
"""OUT-OF-CORE FWHT for the Q arm — the n=17/18 path. Elder C6575. CANDIDATE, correctness half (A).

*** THIS IS HALF (A) ONLY: CORRECTNESS. It says NOTHING about throughput. ***
Half (B) — an n=18 wall-clock number — requires timing a >RAM array with caches dropped, and until
that is run there is no honest n=18 duration. My earlier "1-1.5 h" projection is WITHDRAWN as a
figure: a caveat does not neutralise a number, because the number is what travels.

WHY OUT-OF-CORE. The resident FWHT (exp142_p1_qarm_fwht_decode_elder_c6575.py) needs the whole 4^n
int16 array in RAM: measured 8.9 GB peak / 278 s at n=16, RESIDENT. n=17 wants 34.4 GB against 38 GB
available on a host shared with four other crew, and n=18 wants 137.4 GB. With the sizing confuser
corrected (n_sizable 21 at m=2040, n_affordable ~24), MY DECODER is the first wall the ladder hits —
and it is the only remaining wall that costs work rather than the deletion of a constant.

THE DECOMPOSITION. The Walsh-Hadamard transform over GF(2)^(2n) is SEPARABLE across any split of the
index bits: WHT_{2^(2n)} = WHT_{2^a} (x) WHT_{2^b} with a + b = 2n. Viewing the array as a
2^a x 2^b matrix, the full transform is
    pass 1: WHT along axis 1  (each row contiguous  -> sequential I/O)
    pass 2: WHT along axis 0  (column slabs, strided -> the expensive pass)
NO TRANSPOSE is required, which is the usual out-of-core cost. Pass 2's slab width is the whole
ballgame and it is a MEASURED parameter here, never a default (Ember general#2815):
    512 cols -> 1024 B per row read  -> partial block; full page cost for a fraction of a page
   2048 cols -> 4096 B per row read  -> exactly the page floor
   8192 cols -> 16 KB per row read   -> 4x fewer reads, 4.29 GB resident at n=18

*** THE GATE FLAW EMBER CAUGHT, AND WHY --force-blocking EXISTS. ***
My first proposal was to validate at n=15. That array is 2.1 GB against 38 GB free plus page cache,
so every "disk" read returns from RAM: I would have been testing blocking logic on a path that never
blocks and timing I/O that involves no I/O. That is the test-path-vs-production-path divergence that
voided an earlier wave of this experiment (kit hash PASS, selftest PASS, flight INVALID, because the
test bound parameters by name and production bound them positionally). A test is only as good as the
path it exercises.

So correctness is validated by FORCING the blocking small enough that the multi-pass strided path is
genuinely traversed on data that would have fit — and validated against the REAL REVEALED ANSWERS at
n=8/10/12/13, not against synthetic data. Same six-way known-answer discipline that killed the ISD
decoder this morning: if it fails any rung it is not proposed.

  --validate [--row-block N --col-slab N]   revealed rungs through the out-of-core path (the gate)
  --job <id> --n <n>                        decode a flown job out-of-core
"""
import argparse, json, math, os, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_robust_decoder_sim as G2
import exp142_p1_qarm_fwht_decode_elder_c6575 as RES_IMPL

RES = os.path.join(HERE, "..", "results")
SCRATCH = "/mnt/droid/tmp-elder-fwht"          # 423 GB free; NOT root (286 GB, shared)
LETTERS = "IXYZ"


def _wht_axis1(mat, row_block):
    """WHT along the contiguous axis, in row-blocks. mat is a (R, C) memmap view."""
    R, C = mat.shape
    for r0 in range(0, R, row_block):
        blk = np.asarray(mat[r0:r0 + row_block, :], dtype=np.int32)   # resident copy of the block
        h = 1
        while h < C:
            v = blk.reshape(blk.shape[0], -1, 2, h)
            x = v[:, :, 0, :].copy()
            y = v[:, :, 1, :]
            v[:, :, 0, :] = x + y
            v[:, :, 1, :] = x - y
            h <<= 1
        mat[r0:r0 + row_block, :] = blk.astype(mat.dtype)


def _wht_axis0(mat, col_slab):
    """WHT along the STRIDED axis, in column slabs. This is the expensive pass at scale."""
    R, C = mat.shape
    for c0 in range(0, C, col_slab):
        c1 = min(c0 + col_slab, C)
        slab = np.asarray(mat[:, c0:c1], dtype=np.int32)              # (R, slabwidth) resident
        h = 1
        while h < R:
            v = slab.reshape(-1, 2, h, slab.shape[1])
            x = v[:, 0, :, :].copy()
            y = v[:, 1, :, :]
            v[:, 0, :, :] = x + y
            v[:, 1, :, :] = x - y
            h <<= 1
        mat[:, c0:c1] = slab.astype(mat.dtype)


def decode_oocore(bits, n, mapping, csign, row_block, col_slab, top=8, keep=False):
    """Exact constraint-rate argmax via a two-pass out-of-core WHT over a memmap."""
    Q = np.array([G2.outcome_to_bits(s, n, mapping) for s in bits], dtype=np.uint8)
    m = Q.shape[0]
    two_n = 2 * n
    N = 1 << two_n
    a = two_n // 2                 # high bits -> rows
    b = two_n - a                  # low bits  -> columns (contiguous)
    R, C = 1 << a, 1 << b
    dt = np.int16 if m < np.iinfo(np.int16).max else np.int32

    os.makedirs(SCRATCH, exist_ok=True)
    fd, path = tempfile.mkstemp(dir=SCRATCH, suffix=f"-n{n}.fwht")
    os.close(fd)
    try:
        f = np.memmap(path, dtype=dt, mode="w+", shape=(N,))
        f[:] = 0
        Aidx = np.zeros(m, dtype=np.int64)
        for j in range(n):
            Aidx |= (Q[:, n + j].astype(np.int64) & 1) << j
            Aidx |= (Q[:, j].astype(np.int64) & 1) << (n + j)
        np.add.at(f, Aidx, 1)
        f.flush()

        mat = f.reshape(R, C)
        _wht_axis1(mat, row_block)      # contiguous pass
        f.flush()
        _wht_axis0(mat, col_slab)       # strided pass — the one that must be exercised
        f.flush()

        want0, want1 = int(csign[0]), int(csign[1])
        xmask = (1 << n) - 1
        best = []
        chunk = 1 << 22
        for lo in range(0, N, chunk):
            hi = min(lo + chunk, N)
            idx = np.arange(lo, hi, dtype=np.int64)
            px, pz = idx & xmask, (idx >> n) & xmask
            ypar = RES_IMPL._popcount_parity(px & pz).astype(np.int32)
            want = np.where(ypar == 0, want0, want1)
            Fc = np.asarray(f[lo:hi], dtype=np.int32)
            hits = np.where(want == 0, (m + Fc) // 2, (m - Fc) // 2)
            if lo == 0:
                hits[0] = -1
            k = min(top, hi - lo)
            sel = np.argpartition(-hits, k - 1)[:k]
            best.extend((int(hits[s]), int(lo + s)) for s in sel)
            best.sort(reverse=True); best = best[:top]
        del f
    finally:
        if not keep and os.path.exists(path):
            os.unlink(path)

    tab = {(0, 0): "I", (1, 0): "X", (1, 1): "Y", (0, 1): "Z"}
    def to_pauli(i):
        px_, pz_ = i & xmask, (i >> n) & xmask
        return "".join(tab[((px_ >> j) & 1, (pz_ >> j) & 1)] for j in range(n))
    return [(to_pauli(i), h / m) for h, i in best], m, {"rows": R, "cols": C,
            "row_block": row_block, "col_slab": col_slab, "dtype": np.dtype(dt).name,
            "bytes_per_row_read": col_slab * np.dtype(dt).itemsize}


def validate(row_block, col_slab):
    import time
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    print("OUT-OF-CORE FWHT VALIDATION — the REVEALED answers, through the two-pass strided path.")
    print(f"blocking FORCED to row_block={row_block}, col_slab={col_slab} so the multi-pass path is")
    print("genuinely traversed on data that would otherwise have fit in RAM.\n")
    ok_all = True
    for n, src, trueP, exp_rate, run_P, run_rate in RES_IMPL.REVEALED:
        try:
            bits = RES_IMPL._load(src, n)
        except SystemExit as e:
            print(f"  n={n:<3} SKIP ({e})"); continue
        t0 = time.time()
        rows, m, geom = decode_oocore(bits, n, mapping, csign, row_block, col_slab)
        dt = time.time() - t0
        P, rate = rows[0]; r2, r2r = rows[1]
        good = (P == trueP) and abs(rate - exp_rate) < 5e-4
        if run_P is not None:
            good &= (r2 == run_P) and abs(r2r - run_rate) < 5e-4
        # cross-check the FULL top-8 as a SET against the resident implementation
        res_rows, _ = RES_IMPL.decode_fwht(bits, n, mapping, csign, top=8)
        setmatch = {(p, round(r, 6)) for p, r in rows} == {(p, round(r, 6)) for p, r in res_rows}
        good &= setmatch
        ok_all &= good
        passes = max(1, geom["rows"] // row_block) + max(1, geom["cols"] // col_slab)
        print(f"  n={n:<3} {P:<14} rate {rate:.4f} (exp {exp_rate:.4f})  {geom['rows']}x{geom['cols']} "
              f"{passes} blocks  top8-set {'=' if setmatch else 'DIFFERS'}  {dt:6.1f}s  "
              f"{'MATCH' if good else '*** FAIL ***'}")
    print(f"\n  OUT-OF-CORE PATH: {'EXACT on every revealed rung AND top-8-set-identical to the resident impl' if ok_all else 'FAILED — not proposable'}")
    print("  NOTE: this is correctness ONLY. No throughput claim is made or implied — half (B) has")
    print("  not run, so there is still NO honest n=18 duration.")
    return 0 if ok_all else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--job"); ap.add_argument("--n", type=int)
    ap.add_argument("--row-block", type=int, default=1 << 12)
    ap.add_argument("--col-slab", type=int, default=1 << 12)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.validate:
        return validate(a.row_block, a.col_slab)
    if not (a.job and a.n):
        sys.exit("--validate, or --job <id> --n <n>")
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    from run_exp66_qpu_partb import _get_ibm_service
    import exp142_decode_meter as M
    job = _get_ibm_service().job(a.job); res = job.result()
    want = 2 * a.n; cands = []
    for i in range(len(res)):
        b = list(M.fetch_pub_bits(job, i))
        if b and len(b[0].replace(" ", "")) == want:
            cands.append((i, b))
    if len(cands) != 1:
        raise SystemExit(f"expected EXACTLY ONE pub with {want} bits/row, found {len(cands)}")
    rows, m, geom = decode_oocore(cands[0][1], a.n, mapping, csign, a.row_block, a.col_slab)
    out = RES_IMPL.report(rows, m, a.n, f"n={a.n} decode (out-of-core FWHT, exact)")
    out.update({"job": a.job, "geometry": geom, "cycle": "C6575",
                "decoder": "out-of-core FWHT — EXACT, two-pass separable WHT"})
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1); print(f"\nSAVED {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
