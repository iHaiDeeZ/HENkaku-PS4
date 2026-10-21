#!/usr/bin/env bash
# Configure Vita3K for PS4: the PS4 frontend (vita3k/ps4), Vulkan on DolphinPS4's RADV port, no Qt,
# no cubeb, SDL3 / Boost / OpenSSL / curl / FFmpeg 7.1 from the sysroot. Run through ~/vita3k (no
# space in the path).
#   configure-vita3k.sh [extra cmake args...]
#
# pthreads are in libkernel, but CMake's probe programs don't link: FindThreads is told.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/ps4-env.sh"
SRC="${VITA3K_SRC:-$PS4_BUILD_ROOT/src/vita3k}"
BUILD="$PS4_BUILD_ROOT/build/vita3k"
export PS4_SYSROOT="$PS4_BUILD_ROOT/sysroot"
export PKG_CONFIG_LIBDIR="$PS4_SYSROOT/lib/pkgconfig"
unset PKG_CONFIG_PATH
ps4_cmake -S "$SRC" -B "$BUILD" -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE="$HERE/../toolchain/ps4-vita3k.cmake" \
    "-DCMAKE_PROJECT_Vita3K_INCLUDE=$HERE/../toolchain/ps4-love-style.cmake" \
    -DPS4_PAID="${PS4_PAID:-0x3800000000000035}" \
    -DPS4_MESA_BUILD="$PS4_BUILD_ROOT/build/mesa" \
    -DPS4_SYSROOT="$PS4_SYSROOT" \
    -DUSE_DISCORD_RICH_PRESENCE=OFF -DUSE_LTO=NEVER \
    -DVITA3K_FORCE_SYSTEM_BOOST=ON \
    -DCMAKE_HAVE_LIBC_PTHREAD=1 -DCMAKE_THREAD_LIBS_INIT= -DThreads_FOUND=TRUE \
    -DBUILD_TESTING=OFF \
    "$@"
