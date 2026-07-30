"""int16 FWHT feasibility probe (Ember C4216) — SYNTHETIC DATA ONLY.

Blindness note: this touches NO flight results and NO decoder code. It tests one
narrow question — can the Walsh-Hadamard transform that Elder's FWHT decoder needs
run in int16, and what does that do to the memory wall. Synthetic histograms only.
"""
import numpy as np, time, math

def fwht(a):
    """In-place FWHT, dtype-preserving. a is 1-D, len = power of 2."""
    h = 1
    n = a.shape[0]
    while h < n:
        a = a.reshape(-1, 2, h)
        x = a[:, 0, :].copy()
        y = a[:, 1, :]
        a[:, 0, :] = x + y
        a[:, 1, :] = x - y
        a = a.reshape(n)
        h *= 2
    return a

print("[1] CORRECTNESS — int16 vs float64 reference, synthetic count histograms")
rng = np.random.default_rng(11)
ok = True
for nn in (6, 8, 10):
    N = 4**nn if nn <= 8 else 2**16
    m = 3000
    idx = rng.integers(0, N, size=m)
    h64 = np.bincount(idx, minlength=N).astype(np.float64)
    h16 = h64.astype(np.int16)
    f64 = fwht(h64.copy())
    f16 = fwht(h16.copy())
    same = np.array_equal(f16.astype(np.int64), f64.astype(np.int64))
    bound = int(np.abs(f64).max())
    print(f"  N=2^{int(math.log2(N)):<2d} m={m}  int16==float64: {same}   max|F|={bound} (bound m={m}, int16 max 32767)")
    ok &= same

print(f"  -> {'EXACT MATCH, no overflow' if ok else 'MISMATCH'}")

print("\n[2] INTERMEDIATE BOUND — every stage bounded by L1(input)=m, checked empirically")
N = 2**20; m = 5000
idx = rng.integers(0, N, size=m)
a = np.bincount(idx, minlength=N).astype(np.int32)
h = 1; peak = 0
while h < N:
    a = a.reshape(-1, 2, h)
    x = a[:, 0, :].copy(); y = a[:, 1, :]
    a[:, 0, :] = x + y; a[:, 1, :] = x - y
    a = a.reshape(N)
    peak = max(peak, int(np.abs(a).max())); h *= 2
print(f"  peak |intermediate| over ALL stages = {peak}  vs m = {m}  -> bound holds: {peak <= m}")

print("\n[3] THROUGHPUT at a safe size (int16, 2^28 = 0.54 GB) — extrapolate the wall")
N = 2**28
a = np.zeros(N, dtype=np.int16); a[rng.integers(0, N, size=4000)] = 1
t0 = time.time(); fwht(a); dt = time.time() - t0
per_elem = dt / (N * math.log2(N))
print(f"  2^28 int16 FWHT: {dt:.1f}s")
print("\n  PROJECTED (int16, ypar-sequential = one branch at a time):")
print("   n    array(2^2n)      int16 both   int16 seq    est FWHT time")
for nn in (15, 16, 17, 18):
    NN = 4**nn
    est = per_elem * NN * math.log2(NN)
    print(f"  {nn:2d}   2^{2*nn:<2d}         {NN*2/1e9:7.1f} GB  {NN*2/2/1e9:7.1f} GB   {est/60:8.1f} min")
print("\n  host now: 38 GB RAM available, 423 GB free on /mnt/droid")
