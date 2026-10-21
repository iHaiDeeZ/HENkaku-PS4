#!/usr/bin/env bash
# Configure + build with logs (~/vita3k-build/logs/{configure,build}.log) and an error summary.
# Exits with the build's status (a failed build must never be packaged).
#   rebuild-vita3k.sh [clean]
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
[ "${1:-}" = clean ] && rm -rf "$HOME/vita3k-build/build/vita3k"
bash "$HERE/logrun.sh" configure bash "$HERE/configure-vita3k.sh" || { tail -40 "$HOME/vita3k-build/logs/configure.log"; exit 1; }
bash "$HERE/logrun.sh" build bash "$HERE/build-vita3k.sh" -k 0
rc=$?
L="$HOME/vita3k-build/logs/build.log"
tail -1 "$L"; echo "errors: $(grep -c 'error:' "$L")"
grep "error:" "$L" | sed 's/.*src\/vita3k\///' | sort | uniq -c | sort -rn | head -${TOP:-60}
exit $rc
