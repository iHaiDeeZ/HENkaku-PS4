#!/usr/bin/env bash
# Clone upstream Vita3K (with submodules) into the WSL build tree at the base recorded in
# patches/BASE.txt, apply the PS4 patches on a branch "ps4", and link the repo space-free.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"
[ -e "$HOME/vita3k" ] || ln -s "$REPO" "$HOME/vita3k"
BASE="$(awk '/^base:/{print $2}' "$REPO/patches/BASE.txt")"
mkdir -p "$HOME/vita3k-build/src" "$HOME/vita3k-build/logs"
cd "$HOME/vita3k-build/src"
[ -d vita3k ] || git clone https://github.com/Vita3K/Vita3K.git vita3k
cd vita3k
git fetch -q origin
git checkout -q "$BASE"
git submodule update --init --recursive
git checkout -q -B ps4
git apply "$REPO/patches/vita3k-ps4.patch"
git -C external/dynarmic apply "$REPO/patches/dynarmic-ps4.patch"
git add -A -- . ':!external/dynarmic'
git commit -q -m "PS4 port" || true
git log -1 --format='%h %ci %s'
