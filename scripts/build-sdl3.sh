#!/usr/bin/env bash
# SDL3 for the PS4, from Vita3K's submodule (external/sdl), installed into ~/vita3k-build/sysroot.
#   build-sdl3.sh
# Vita3K uses SDL for its core services (threads, semaphores, timers, surfaces, gamepad and sensor
# types, camera and audio APIs), not for the window or the sound: the PS4 frontend (ps4/) presents
# through VideoOut and plays through sceAudioOut. So: no video or audio drivers but the dummy ones,
# the virtual joystick only, and no dynamic loading. Configure checks link real PS4 executables
# (PS4_TRY_LINK), so only functions the console has are used.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
PSB="${PSB:-$HOME/vita3k-build}"
SRC="${SDL_SRC:-$PSB/src/vita3k/external/sdl}"
BUILD="$PSB/build/sdl3"
export PS4_SYSROOT="$PSB/sysroot"
source "$HERE/ps4-env.sh"   # PacBrew paths, ld.lld compat
rm -rf "$BUILD"
env -u CFLAGS -u CXXFLAGS -u CPPFLAGS -u LDFLAGS -u LIBS \
cmake -S "$SRC" -B "$BUILD" -G Ninja \
    -DCMAKE_TOOLCHAIN_FILE="$HERE/../toolchain/ps4-deps.cmake" -DPS4_TRY_LINK=ON \
    -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX="$PS4_SYSROOT" \
    -DSDL_SHARED=OFF -DSDL_STATIC=ON -DSDL_TEST_LIBRARY=OFF -DSDL_TESTS=OFF -DSDL_EXAMPLES=OFF \
    -DSDL_UNIX_CONSOLE_BUILD=ON -DSDL_DEPS_SHARED=OFF -DSDL_RPATH=OFF -DSDL_DLOPEN_NOTES=OFF \
    -DSDL_X11=OFF -DSDL_WAYLAND=OFF -DSDL_KMSDRM=OFF -DSDL_OPENGL=OFF -DSDL_OPENGLES=OFF \
    -DSDL_VULKAN=OFF -DSDL_RENDER_VULKAN=OFF -DSDL_RENDER_GPU=OFF -DSDL_GPU=OFF -DSDL_RENDER=OFF \
    -DSDL_OPENVR=OFF -DSDL_RPI=OFF -DSDL_ROCKCHIP=OFF -DSDL_VIVANTE=OFF -DSDL_OFFSCREEN=OFF \
    -DSDL_DUMMYVIDEO=ON -DSDL_DUMMYAUDIO=ON -DSDL_DISKAUDIO=OFF -DSDL_DUMMYCAMERA=ON \
    -DSDL_OSS=OFF -DSDL_ALSA=OFF -DSDL_JACK=OFF -DSDL_PIPEWIRE=OFF -DSDL_PULSEAUDIO=OFF -DSDL_SNDIO=OFF \
    -DSDL_HIDAPI=OFF -DSDL_HIDAPI_LIBUSB=OFF -DSDL_HIDAPI_JOYSTICK=OFF -DSDL_VIRTUAL_JOYSTICK=ON \
    -DSDL_LIBUDEV=OFF -DSDL_DBUS=OFF -DSDL_IBUS=OFF -DSDL_LIBURING=OFF -DSDL_FRIBIDI=OFF -DSDL_LIBTHAI=OFF \
    -DSDL_SYSTEM_ICONV=OFF -DSDL_LIBICONV=OFF -DSDL_DIALOG=OFF -DSDL_TRAY=OFF \
    -DSDL_PTHREADS=ON -DSDL_PTHREADS_SEM=ON -DSDL_CLOCK_GETTIME=ON \
    -DSDL_AVX2=OFF -DSDL_AVX512F=OFF \
    > "$PSB/logs/sdl3-configure.log" 2>&1 || { tail -40 "$PSB/logs/sdl3-configure.log"; exit 1; }
grep -E "^-- (  )?SDL_|Enabled|Subsystems|Video drivers|Audio drivers|Joystick|^-- Options" "$PSB/logs/sdl3-configure.log" | head -40 || true
ninja -C "$BUILD" -j"${JOBS:-16}" > "$PSB/logs/sdl3-build.log" 2>&1 || { grep -E "error|undefined" "$PSB/logs/sdl3-build.log" | head -40; exit 1; }
ninja -C "$BUILD" install > /dev/null
ls -la "$PS4_SYSROOT/lib/libSDL3.a" "$PS4_SYSROOT/lib/cmake/SDL3" | head
