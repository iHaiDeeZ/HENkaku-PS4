# Vita3K for PS4

[Vita3K](https://github.com/Vita3K/Vita3K) (PlayStation Vita emulator) as a PS4 homebrew app, built
in WSL Ubuntu with the M33 / Resonance / DolphinPS4 / Crema PS4 toolchain (clang 21 + libc++ 21 on
OpenOrbis).

Status: **v00.03**: v00.02 crashed at startup on the console (see "How the port works", file
functions); v00.03 fixes that and downloads the firmware by itself. Not yet seen running.

## Using it

1. Install `out/Vita3K-vXX.YY.pkg` with GoldHEN's Package Installer and start **Vita3K**.
2. The first time, the launcher downloads the PS Vita firmware (3.74, 128 MiB) and font package
   (54 MiB) from Sony's update server and installs them. Circle stops the download (it carries on
   later, and doesn't start by itself again); Square starts it. Without a connection, copy Sony's
   update files (`PSVUPDAT.PUP`, `PSP2UPDAT.PUP`) to `/data/Vita3K/install/` instead.
3. Over FTP, copy games to **`/data/Vita3K/install/`**: `.vpk` or `.zip` archives, dumped game
   folders (with `sce_sys/param.sfo`), or a `.pkg` with a `.zrif` text file of the same name
   holding its zRIF (or its `.rif` license next to it).
4. In the launcher press **Triangle**: everything there is installed, and what installed moves to
   `install/done/`.
5. Pick a game and press **Cross**.

| DualShock 4 | PS Vita |
|---|---|
| Cross / Circle / Square / Triangle, D-pad, sticks | the same |
| L1 / R1 | L / R |
| OPTIONS | START |
| Touchpad click | SELECT |
| Touchpad | front touch screen |
| L2 / R2 / L3 / R3 | the PS TV's |
| **L3 + R3** | Vita3K's pause menu (Resume / Exit) |

When a game ends (or Exit in the pause menu) the app restarts into the launcher.

## On the console

| Path | What |
|---|---|
| `/data/Vita3K/install` | what the launcher installs (Triangle); `done/` afterwards |
| `/data/Vita3K/cache/download/stopped` | there after Circle stopped the firmware download (Square starts it again) |
| `/data/Vita3K/fs` | the Vita's file system: `ux0` (apps, saves), `vs0`/`os0`/`sa0`/`pd0` (firmware) |
| `/data/Vita3K/config.yml` | Vita3K's settings |
| `/data/Vita3K/cache` | shader cache; `download/`: the firmware while it downloads |
| `/data/Vita3K` | `vita3k.log`, `boot-trace.log` (startup milestones), `crash.log` |
| `/app0` | the package: `eboot.bin`, `data/`, `shaders-builtin/`, `icons/` |

Title ID `VITA00003` (content ID `IV0000-VITA00003_00-VITA3KPS4EMU0000`).

## How the port works

- **Frontend** (`vita3k/ps4/` in the patch): `ps4_main.cpp` replaces the Qt UI and the SDL window.
  The launcher (`ps4_launcher.cpp`, `ps4_canvas.cpp`) is drawn by the CPU into VideoOut buffers
  12-13 in the console's own fonts; the game runs in an `app::AppSessionController` session like
  the SDL frontend's. A session leaves threads, guest memory and the GPU device behind, so when the
  game ends the app restarts itself (`sceSystemServiceLoadExec`) back into the launcher; a game
  starting another executable restarts into it the same way.
- **Graphics**: Vita3K's Vulkan renderer on DolphinPS4's RADV port, linked in. `ps4_wsi.cpp` (M33's
  WSI) adds `VK_EXT_headless_surface` and `VK_KHR_swapchain` on VideoOut (linear 1920x1080 images,
  GPU-side flips); the renderer gets its entry points from `ps4_vk_get_instance_proc_addr()` and
  its surface from the PS4 frame host (`renderer::FrameHost`).
- **CPU**: dynarmic's x86-64 JIT (`patches/dynarmic-ps4.patch`). Only flexible memory can run code
  on the PS4 and there is a JIT per guest thread, so each 128 MiB code cache is a virtual range
  reservation committed in 256 KiB steps as code is emitted (system flexible memory, else regular),
  with a 512 KiB constant pool. Fastmem through dynarmic's POSIX fault handler (SIGSEGV and SIGBUS).
- **Guest memory** (`mem/src/mem.cpp`): the Vita's 4 GiB address space is a virtual range
  reservation; the host pages the allocator commits are backed by direct memory mapped in place
  (16 KiB pages), and given back to a free list when freed. Write tracking uses `mprotect` and the
  fault handler (the PS4's FreeBSD signal context, `mc_err`), which hands other faults to the crash
  log.
- **Audio**: `audio/src/impl/ps4_audio.cpp`, one sceAudioOut port (48 kHz stereo) fed by a mixer
  thread; each Vita port is resampled to 48 kHz into a ring.
- **Input**: ScePad into Vita3K's virtual keyboard state (game and menus), the touchpad as touch
  events, motion as sensor events (`ps4_pad.cpp`).
- **SDL3**: built for the console (`scripts/build-sdl3.sh`) for Vita3K's core services only (threads,
  timers, surfaces, gamepad and sensor types); dummy video and audio drivers.
- **Firmware download** (`ps4_download.cpp`, `ps4_launcher.cpp`): libcurl over plain HTTP from
  Sony's update server (the URLs Vita3K's welcome dialog links to), resumed from a `.part` file,
  checked against the expected size, then `install_pup`.
- **Libraries**: Boost 1.89, OpenSSL, curl and FFmpeg 7.1 from M33's sysroot.
- **File functions** (`port/ps4_fileat.cpp`): the OpenOrbis C library has `fstatat`, `unlinkat`,
  `fchmodat` and `utimensat` only as stubs failing with ENOSYS, and the sysroot's Boost.Filesystem
  uses them for every status check and removal (v00.02 died at its first `create_directories`).
  Linker wraps implement them with `stat`, `lstat`, `open`, `unlink`, `rmdir`, `chmod` and `utimes`;
  `openat` remembers which path each directory descriptor stands for. `statvfs` is wrapped too:
  the C library's never fills in its result.
- **Runtime** (`port/`, from M33): heap, crash and boot logs, profiler, DNS, the RADV winsys.

## Building

```
scripts/seed-build-tree.sh          # ~/vita3k-build from M33's sysroot and RADV build
scripts/clone-vita3k.sh             # upstream Vita3K at patches/BASE.txt + the PS4 patches, branch ps4
scripts/build-sdl3.sh               # SDL3 for the console, into the sysroot
scripts/rebuild-vita3k.sh           # configure + build (logs in ~/vita3k-build/logs)
VITA3K_VERSION=00.01 scripts/package-vita3k.sh
scripts/save-patch.sh "message"     # commit ~/vita3k-build/src/vita3k and refresh patches/
```

Run the scripts from WSL through `~/vita3k` (the space in "PS4 Projects" breaks linker flags).
Upload from Windows (Git Bash): `scripts/upload-to-console.sh out/Vita3K-vXX.YY.pkg`.

## License

GPL-2.0-or-later, as Vita3K ([LICENSE](LICENSE)): the patches are modifications of Vita3K and
dynarmic (0BSD). The PS4 runtime in `port/` and the toolchain scripts come from the M33 / Resonance /
DolphinPS4 / Crema ports; `port/mesa/ac_ps4_drm.c` is the RADV winsys of the PS4 Mesa port (MIT).
No PS Vita firmware, Sony system files or games are included: supply your own.
