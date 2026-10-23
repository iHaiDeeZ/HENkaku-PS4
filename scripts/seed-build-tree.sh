#!/usr/bin/env bash
# One-time: create ~/vita3k-build from copies of M33's build tree: the libc++ 21 sysroot (with the
# libc overlay, the PS4 ucontext layout, Boost 1.89, OpenSSL, curl, zlib, zstd, glslang and rpcs3's
# FFmpeg 7.1) and the RADV/GNM Mesa build, so this port never writes into ~/m33-build.
set -euo pipefail
M33="${M33:-$HOME/m33-build}"
PSB="${PSB:-$HOME/vita3k-build}"
mkdir -p "$PSB/src" "$PSB/build" "$PSB/out" "$PSB/logs" "$PSB/oelf"
[ -d "$PSB/sysroot" ] || cp -a "$M33/sysroot" "$PSB/sysroot"
[ -d "$PSB/host-compat" ] || cp -a "$M33/host-compat" "$PSB/host-compat"
# Mesa: the whole build directory (its static libraries are thin archives). Since 1.08 the newer PS4
# RADV of Crema's tree (as TOTK's, Oct 17: GPU submissions on their own thread), not M33's (Oct 6)
MESA="${MESA:-$HOME/totk-build/build/mesa}"
[ -d "$PSB/build/mesa" ] || cp -a "$MESA" "$PSB/build/mesa"
# The PS4's signal context layout in the libc overlay (dynarmic's and Vita3K's fault handlers read it)
PSB="$PSB" bash "$(dirname "$0")/../toolchain/ucontext-overlay.sh"
# Space-free path to this repo: toolchain flags (linker script paths) break on "PS4 Projects".
REPO="$(cd "$(dirname "$0")/.." && pwd)"
[ -e "$HOME/vita3k" ] || ln -s "$REPO" "$HOME/vita3k"
du -sh "$PSB"/* 2>/dev/null
find "$PSB/build/mesa" -name '*.a' | wc -l
