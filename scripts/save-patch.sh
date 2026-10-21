#!/usr/bin/env bash
# Commit the work in ~/vita3k-build/src/vita3k (branch ps4, and the dynarmic submodule's) and export it
# against the upstream base recorded in patches/BASE.txt:
#   patches/vita3k-ps4.patch    Vita3K itself
#   patches/dynarmic-ps4.patch  external/dynarmic (a submodule: its changes aren't in the first)
#   save-patch.sh "commit message"
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
SRC="${VITA3K_SRC:-$HOME/vita3k-build/src/vita3k}"
BASE="$(awk '/^base:/{print $2}' "$HERE/../patches/BASE.txt")"
MSG="${1:-PS4 port work}"

DYN="$SRC/external/dynarmic"
DYN_BASE="$(git -C "$SRC" ls-tree "$BASE" external/dynarmic | awk '{print $3}')"
git -C "$DYN" diff --binary "$DYN_BASE" > "$HERE/../patches/dynarmic-ps4.patch"

# the submodule stays at upstream's commit in the parent (its changes travel as their own patch)
git -C "$SRC" add -A -- . ':!external/dynarmic'
git -C "$SRC" diff --cached --quiet || git -C "$SRC" commit -q -m "$MSG"
git -C "$SRC" diff --binary "$BASE" HEAD -- . ':!external/dynarmic' > "$HERE/../patches/vita3k-ps4.patch"
echo "patches/vita3k-ps4.patch: $(grep -c '^diff --git' "$HERE/../patches/vita3k-ps4.patch") files"
echo "patches/dynarmic-ps4.patch: $(grep -c '^diff --git' "$HERE/../patches/dynarmic-ps4.patch") files"
