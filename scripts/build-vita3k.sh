#!/usr/bin/env bash
# Build Vita3K for PS4 (run scripts/configure-vita3k.sh first). Extra args go to ninja.
#   build-vita3k.sh [ninja args...]
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/ps4-env.sh"  # also puts PacBrew ld.lld's libxml2 compat link on LD_LIBRARY_PATH
ninja -C "$PS4_BUILD_ROOT/build/vita3k" -j"${JOBS:-16}" "$@"
