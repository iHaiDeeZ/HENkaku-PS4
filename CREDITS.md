# Credits

HENkaku is a port. Nearly everything that makes the games run is other people's work.

## The emulator

- **[Vita3K](https://github.com/Vita3K/Vita3K)** by the Vita3K team (GPL-2.0-or-later): the PlayStation Vita
  emulator. HENkaku applies `patches/vita3k-ps4.patch` to it at the commit in `patches/BASE.txt`, with some upstream
  pull requests that weren't merged yet (listed in [docs/PORT.md](docs/PORT.md)).
- **[dynarmic](https://github.com/Vita3K/dynarmic)** (0BSD): the ARM JIT, with `patches/dynarmic-ps4.patch`.
- The libraries Vita3K brings in its `external/` folder, built into the app under their own licences: capstone,
  CLI11, concurrentqueue, dlmalloc, fmt, glad, glslang, LibAtrac9, libfat16, miniz, psvpfstools, pugixml, spdlog,
  SPIRV-Cross, stb, substitute, VulkanMemoryAllocator-Hpp, xxHash and yaml-cpp.

## The PS4 side

- **[Mesa](https://mesa3d.org)** (MIT): the RADV Vulkan driver, ported to the PS4's GPU. `port/mesa/ac_ps4_drm.c`
  is that port's winsys.
- **[OpenOrbis](https://github.com/OpenOrbis)** (GPL-3.0 toolchain; its libraries under their own terms) and
  **[PacBrew](https://github.com/PacBrew)**: the PS4 toolchains.
- **[LLVM](https://llvm.org)** (Apache-2.0 WITH LLVM-exception): clang 21 and libc++ 21.
- **[SDL3](https://github.com/libsdl-org/SDL)** (zlib): the services Vita3K uses, built for the console
  (`scripts/build-sdl3.sh`).
- **[Boost](https://www.boost.org)** 1.89 (BSL-1.0), **[OpenSSL](https://www.openssl.org)** (Apache-2.0),
  **[curl](https://curl.se)** (curl licence), **[zlib](https://zlib.net)**, **[zstd](https://github.com/facebook/zstd)**
  (BSD) and **[FFmpeg](https://ffmpeg.org)** 7.1 (LGPL-2.1-or-later): the sysroot's libraries, from M33's build.
- **[Resonance](https://github.com/iHaiDeeZ/Resonance)**, **[DolphinPS4](https://github.com/iHaiDeeZ/DolphinPS4)**,
  **[M33](https://github.com/iHaiDeeZ/M33)** and **[Crema](https://github.com/iHaiDeeZ/Crema)** by ShiroKlein:
  the PS4 runtime in `port/` (heap, crash and boot logs, profiler, DNS) and the VideoOut presentation.

## In the package

- **[AMD FidelityFX Super Resolution 1](https://github.com/GPUOpen-Effects/FidelityFX-FSR)** (MIT): EASU and
  RCAS in Vita3K's screen filter, through its 32-bit path on the PS4.
- **Roboto** (SIL Open Font License 1.1, `fonts/OFL-Roboto.txt`): the launcher's text until the PS Vita's own fonts
  are installed.
- **The HENkaku ensō** (`assets/henkaku-logo.png`), from team molecule's [HENkaku](https://henkaku.xyz):
  `scripts/make-henkaku-art.py` makes the app's icon, background and this repository's banner from it.
- No PS Vita firmware, Sony system files or games: HENkaku downloads the firmware from Sony's update server on the
  console, and the home screen's pictures are read from it there.

## Thanks

To the Vita3K team for making the emulator open, to the dynarmic and Mesa developers, to team molecule for
HENkaku, and to everyone keeping the PS Vita and PS4 homebrew scenes and their toolchains alive.
