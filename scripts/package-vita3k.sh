#!/usr/bin/env bash
# Package the PS4 Vita3K build (after rebuild-vita3k.sh) as Vita3K, VITA00003
# (IV0000-VITA00003_00-VITA3KPS4EMU0000.pkg) into out/Vita3K-vXX.YY.pkg. Earlier packages in out/ stay.
#   VITA3K_VERSION=00.01 package-vita3k.sh
# The console gets the package from Windows with scripts/upload-to-console.sh (uploads sent from WSL
# were lost on the console).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/ps4-env.sh"
BUILD="$PS4_BUILD_ROOT/build/vita3k"
SRC="${VITA3K_SRC:-$PS4_BUILD_ROOT/src/vita3k}"
EBOOT="$BUILD/vita3k/vita3k_eboot/eboot.bin"
VERSION="${VITA3K_VERSION:-00.01}"

[ -f "$EBOOT" ] || { echo "missing $EBOOT: build first" >&2; exit 1; }
ELF="$BUILD/bin/Vita3K"
[ "$EBOOT" -nt "$ELF" ] || { echo "$EBOOT is older than the ELF: the last build failed" >&2; exit 1; }
[[ "$VERSION" =~ ^[0-9][0-9]\.[0-9][0-9]$ ]] || { echo "version must look like 01.00" >&2; exit 1; }
STAGE="$PS4_BUILD_ROOT/build/vita3k-stage"
rm -rf "$STAGE"
mkdir -p "$STAGE/sce_sys"
cp "$EBOOT" "$STAGE/eboot.bin"
cp "$HERE/../sce_sys/icon0.png" "$HERE/../sce_sys/pic1.png" "$STAGE/sce_sys/"
echo "$VERSION" > "$STAGE/version.txt"
# Vita3K's static assets (Root::static_assets_path = /app0/): data/, shaders-builtin/, icons/
cp -r "$SRC/data" "$STAGE/data"
cp -r "$SRC/vita3k/shaders-builtin" "$STAGE/shaders-builtin"
cp -r "$SRC/vita3k/icons" "$STAGE/icons"
# the HENkaku menu's icon (an ensō drawn by scripts/make-henkaku-icon.py)
cp "$HERE/../assets/henkaku.png" "$STAGE/icons/henkaku.png"
cp "$SRC/COPYING.txt" "$STAGE/COPYING.txt"
# The launcher's and the overlay's font until the PS Vita's font package is installed (Roboto, OFL;
# the app can't read the PS4's own fonts in /preinst)
cp -r "$HERE/../fonts" "$STAGE/fonts"
# PkgTool's pkg_build crashes ("Sequence contains no elements") on empty folders.
find "$STAGE" -type d -empty -delete
# Vulkan (RADV on GNM) runs under the plain homebrew identity (4.5 GiB of direct memory).
PKG="$(SFO_STYLE=plain NO_RIGHT_SPRX=1 DOLPHIN_PS4_MODULES_DIR=/nonexistent "$HERE/make-pkg.sh" "$STAGE" VITA00003 "Vita3K" "$VERSION" VITA3KPS4EMU "$PS4_BUILD_ROOT/out" | tail -1)"
ls -la "$PKG"
# a copy next to the repo (E:\PS4 Projects\Vita3K\out), easy to find from Windows; *.pkg is ignored by git
mkdir -p "$HERE/../out"
NAME="Vita3K-v$VERSION.pkg"
cp "$PKG" "$HERE/../out/$NAME"
# Keep the symbols of every packaged build: crash logs must be symbolized against the exact binary.
mkdir -p "$PS4_BUILD_ROOT/oelf"
cp "$BUILD/vita3k/vita3k_eboot/vita3k.oelf" "$PS4_BUILD_ROOT/oelf/v$VERSION.oelf"
cp "$ELF" "$PS4_BUILD_ROOT/oelf/v$VERSION.elf"
echo "now, from Windows (Git Bash): scripts/upload-to-console.sh out/$NAME"
