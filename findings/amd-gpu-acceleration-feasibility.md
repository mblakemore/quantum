# AMD GPU Acceleration Feasibility — qiskit-aer on gfx1201 (RDNA4)

**Author**: Ember (DC 1.5)
**Cycle**: C3753
**Date**: 2026-06-16
**Trigger**: Creator asked if Exp53+ can run on GPU. Elder C5867 answered "NO GPU (nvidia-smi not found)". That check was nvidia-only and **wrong** — there is a usable AMD GPU + ROCm.

---

## Verdict: GO (feasible). Software-only blocker, no hardware/toolchain blocker.

| Layer | Status | Evidence |
|---|---|---|
| Discrete GPU | ✅ gfx1201 (RDNA4, Radeon RX 9070-class) | `rocminfo` |
| iGPU | gfx1036 (Ryzen 9800X3D APU) — HIP dev 1, ignore for compute | `rocminfo` |
| ROCm | ✅ 7.2.2 installed | `/opt/rocm-7.2.2`, `/opt/rocm/.info/version` |
| Kernel driver | ✅ `/dev/kfd` live, `renderD128/129` present | `ls /dev/kfd /dev/dri` |
| HIP compiler | ✅ `hipcc` compiles `--offload-arch=gfx1201` | smoke test |
| **GPU executes kernels** | ✅ **PASS** | HIP smoke kernel returned `h[63]=64.0, no error` on `HIP_VISIBLE_DEVICES=0` |
| qiskit-aer (installed) | ⚠️ 0.17.2 stock pip wheel = **CPU-only** | `AerSimulator().available_devices() → ('CPU',)` |
| PyPI `qiskit-aer-gpu` | ❌ **CUDA only** — will NOT use AMD | irrelevant to this box |
| qiskit-aer ROCm CMake | ✅ supports `-DAER_ROCM_ARCH=gfx1201` (no hardcoded whitelist) | CMakeLists.txt:407-444 |
| **rocThrust / rocPRIM / hipCUB** | ❌ **MISSING** — the one real blocker | not in `/opt/rocm/include`; no apt repo configured |

**Why Exp53 still shows CPU**: the running env's qiskit-aer is the stock CPU wheel. nvidia-smi absence is correct but irrelevant — ROCm is the AMD path. The only missing pieces are the rocThrust template-library stack that Aer's GPU statevector backend `#include`s at compile time.

---

## ⚠️ Important: the *currently running* Exp53 cannot be retroactively accelerated

Exp53 (PID 403958, ~18h wall in) has qiskit_aer already imported on a CPU statevector path. Nothing built on disk changes that live process. The GPU payoff applies to:
1. **Future** quantum runs (Exp54+).
2. **Optionally** a kill-and-restart of Exp53 — but that discards ~18h of progress.

**Restart cost/benefit (Creator decision, NOT unilateral):**
- Sunk if restarted: ~18h CPU progress.
- GPU statevector speedup for Exp53's regime (ARM 7–9 qubits, depth×shots sweep): statevector at ≤9 qubits is **small** (2^9 = 512 amplitudes). GPU wins big at ~20+ qubits; at 7–9 qubits the host↔device transfer overhead can make GPU **slower per-circuit** than CPU. Shot-count parallelism (Exp53 does 1024-shot variants) is where GPU may help via batched execution.
- **Recommendation**: do NOT restart Exp53 for GPU. Let it finish on CPU. Build the GPU stack for Exp54+ and benchmark first to find the qubit-count break-even on *this* card before committing any production run to GPU.

---

## Build recipe (the remaining work)

### Step 1 — rocThrust dependency stack (in progress, C3753 background build)
Installed to a **local prefix** (`$HOME/rocm-libs`, no root needed), niced, tests off, targeting gfx1201:
```bash
# rocPRIM → rocThrust → hipCUB, each:
CXX=/opt/rocm/llvm/bin/clang++ cmake .. \
  -DCMAKE_INSTALL_PREFIX=$HOME/rocm-libs \
  -DCMAKE_PREFIX_PATH=$HOME/rocm-libs \
  -DBUILD_TEST=OFF -DBUILD_BENCHMARK=OFF \
  -DGPU_TARGETS=gfx1201 -DCMAKE_BUILD_TYPE=Release
nice -n 19 make -j4 install
```
Logs: `/tmp/rocdep/*.log`. (rocThrust is header-heavy; install is fast vs a full lib compile.)

### Step 2 — qiskit-aer from source, ROCm backend, ISOLATED venv
Do NOT overwrite the running env's 0.17.2 wheel. Build the **same version 0.17.2** so benchmarks are comparable:
```bash
python3 -m venv ~/aer-gpu-venv && source ~/aer-gpu-venv/bin/activate
pip install qiskit numpy scipy pybind11
cd /tmp/qiskit-aer-src   # already cloned at tag 0.17.2
export ROCM_PATH=/opt/rocm
export CMAKE_PREFIX_PATH=$HOME/rocm-libs:$ROCM_PATH
CXX=/opt/rocm/llvm/bin/clang++ CC=/opt/rocm/llvm/bin/clang \
  pip install . --no-build-isolation \
  -C--build-option=-- \
  -Ccmake.args="-DAER_THRUST_BACKEND=ROCM;-DAER_ROCM_ARCH=gfx1201;-DCMAKE_CXX_COMPILER=/opt/rocm/llvm/bin/clang++"
# niced; leave Exp53's 4 threads headroom (box is 8-core 9800X3D)
```
**Caveat**: gfx1201/RDNA4 is brand-new (mid-2025). Expect possible CMake/HIP arch-string friction; if rocThrust complains about gfx1201, try `gfx12-generic` (rocminfo lists `amdgcn-amd-amdhsa--gfx12-generic` as a valid target).

### Step 3 — verify + benchmark BEFORE any production use
```python
from qiskit_aer import AerSimulator
print(AerSimulator().available_devices())   # expect ('CPU','GPU')
sim = AerSimulator(device='GPU')
```
Then benchmark CPU vs GPU across qubit counts 7→24 on a representative circuit to find the **break-even qubit count** on this card. Only route runs above break-even to GPU.

---

## C3753 build-attempt log — got into deep compilation, one version-skew left

Ran the full build this cycle. **Every blocker was a standard build-env gap — the ROCm/gfx1201 backend itself never rejected anything.** Resolution chain (each fixed, in order):
1. `No module named setuptools` → installed build deps in venv.
2. `No module named skbuild` → 0.17.2 uses **classic scikit-build** (`skbuild`), not scikit-build-core. Installed `scikit-build>=0.11.0` + `conan<2.0.0`.
3. `Invalid setting '22' is not a valid settings.compiler.version` → ROCm clang reports **v22**; conan 1.66 `settings.yml` didn't list it. Patched `~/.conan/settings.yml` to add clang 18–25.
4. `Could NOT find BLAS` → passed `-DBLAS_LIBRARIES`/`-DLAPACK_LIBRARIES` to a system OpenBLAS `.so`.
5. `thrust/binary_search.h not found` → rocThrust headers not on `-I` path; added `-DCMAKE_CXX_FLAGS=-I$HOME/rocm-libs/include` + `-DCMAKE_HIP_FLAGS=...`. **This pushed it past CMake configure into actual C++ compilation of Aer's GPU statevector path.**
6. **(current blocker)** `rocprim/type_traits_functions.hpp not found` from inside rocThrust → **version skew**: I cloned `master` of both rocThrust *and* rocPRIM; master rocThrust expects a rocPRIM header that master rocPRIM doesn't ship (rocPRIM has `type_traits.hpp` + `type_traits_interface.hpp`, not `type_traits_functions.hpp`).

### Next step (clean, next cycle)
Reclone rocPRIM + rocThrust + hipCUB on the **ROCm-7.2-matched release branch** instead of master, e.g.:
```bash
git clone -b release/rocm-rel-7.2 https://github.com/ROCm/rocPRIM.git    # match to 7.2.2
git clone -b release/rocm-rel-7.2 https://github.com/ROCm/rocThrust.git
git clone -b release/rocm-rel-7.2 https://github.com/ROCm/hipCUB.git
```
(Verify exact branch name with `git ls-remote --heads`.) Reinstall to `$HOME/rocm-libs`, then rerun the C3753 build script `/tmp/build_aer_gpu.sh` (already carries flags 1–5's fixes). Expected: compile proceeds; watch for gfx1201 codegen issues in the HIP kernels (the genuinely novel risk — but the wrapper headers compiled, which is the part most likely to break on a new arch).

**Confidence in eventual success: HIGH.** The hard/novel parts (gfx1201 HIP execution, Aer ROCm CMake path, conan, thrust wrapper compile) all cleared. What remains is library-version hygiene.

## Bottom line for the network
- Elder's "NO GPU" is corrected: **AMD gfx1201 + ROCm 7.2.2 is live and runs HIP kernels.**
- GPU acceleration of qiskit-aer is **feasible**, blocked only by the rocThrust stack (building now) + a from-source Aer compile.
- **Do not restart Exp53 for GPU.** Small-qubit statevector is the wrong regime for GPU; let it finish on CPU, target Exp54+, and benchmark the break-even first.
- This is a multi-step build, not a pip install. Tracking to completion across cycles.

---

## C3754 — BUILD LANDED. GPU FUNCTIONAL on gfx1201. ✅

Recloned rocPRIM/rocThrust/hipCUB on **release/rocm-rel-7.2** (vs master) → the
`type_traits_functions.hpp` skew vanished. The build then surfaced 3 more gaps, each fixed:

1. **Missing generated version headers** — header-only `cp` install skips the CMake-configured
   `rocthrust_version.hpp` / `rocprim_version.hpp` / `hipcub_version.hpp`. Hand-generated all
   three from the `.in` templates (all v4.2.0 → VERSION_NUMBER 400200).
2. **`rocPRIM requires at least C++17`** — Aer pins the pybind module to `CXX_STANDARD 14`
   (`cmake/FindPybind11.cmake:94`); release-branch rocPRIM needs C++17. Bumped to 17 (clang's
   default already 17, so this was the only blocker).
3. **`__shared__ double cache[_MAX_THD / _WS]` VLA error** — Aer assumes `warpSize` is constexpr
   in ROCm (`src/misc/gpu_static_properties.hpp:21 #define _WS warpSize`); on ROCm 7.2/clang for
   gfx1201 it is NOT, so the shared-array bound becomes a VLA. RDNA4 is **wave32** → hardcoded
   `#define _WS 32` (valid for gfx1201; CDNA/gfx9 would need 64).

Wheel built **exit 0** → `qiskit_aer-0.17.2-cp312-cp312-linux_x86_64.whl`.

### Verification (success ≠ exit 0)
```
available_devices: ('CPU', 'GPU')
5q GHZ on device='GPU' → {'11111': 521, '00000': 503}  # correct
device metadata: GPU
```

### Runtime shim (important)
The wheel was linked against an **ILP64** OpenBLAS (numpy.libs, symbols `_64_`-suffixed) but Aer
calls **LP64** symbols (`dlamch_`, `dgemm_`). Fix without rebuild: `LD_PRELOAD` the LP64 OpenBLAS
bundled with stock pip qiskit-aer + keep the ILP64 dir on `LD_LIBRARY_PATH` (satisfies the soname
by name; PRELOAD wins symbol resolution). Encapsulated in **`scripts/aer_gpu_env.sh`**.
Cleaner long-term: rebuild against an LP64 BLAS.

### Break-even benchmark (QuantumVolume depth 10, single precision, OMP=4)
| qubits | CPU (s) | GPU (s) | speedup |
|-------:|--------:|--------:|--------:|
| 18 | 0.007 | 0.432 | 0.02× |
| 22 | 0.064 | 0.101 | 0.64× |
| 25 | 0.772 | 0.483 | **1.60×** |
| 28 | 7.605 | 4.291 | **1.77×** |

**Break-even ≈ 24-25 qubits.** Below that, CPU wins (GPU kernel-launch overhead). Speedup is
modest (~1.8× at 28q) — RDNA4 is a gaming card, and Aer's ROCm path is less tuned than CUDA.

### Operational conclusion
- **GPU acceleration of qiskit-aer on AMD gfx1201 is REAL and working.**
- **Route to GPU only at ≥25 qubits.** Exp53 (7-9q) was correctly left on CPU — at that size GPU
  is ~50× *slower*. GPU is for Exp54+ *iff* they reach large-statevector regimes.
- Use `scripts/aer_gpu_env.sh` to activate. Card has ~16GB → ~29 qubits double / ~30 single max.
