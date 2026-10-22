# HENkaku (Vita3K for PS4)

**HENkaku** is [Vita3K](https://github.com/Vita3K/Vita3K) (PlayStation Vita emulator) as a PS4 homebrew app (title ID VITA00003, data in `/data/Vita3K`), built
in WSL Ubuntu with the M33 / Resonance / DolphinPS4 / Crema PS4 toolchain (clang 21 + libc++ 21 on
OpenOrbis).

Status: **v00.32**. On the console the launcher works (text, firmware download, installing a VPK),
PKGj runs (renderer on RADV, audio, dynarmic, the network), and Mortal Kombat (PCSE00023) plays:
v00.12 fixed the GPU hang at the start of a fight by turning Vita3K's memory mapping off (see
"Graphics" below). Its fights ran at 30 fps where the game wants 60 (slow motion); v00.13 (fast
floating point in dynarmic, GPU trace mode off) brought them to 30-43, the game's main thread and
render thread taking about 12 ms of CPU each per frame, one after the other. v00.14 gave the guest
memory 2 MiB pages and inlined the game's atomics; its measurements were lost (two starts of the
launcher rotated the game's log away), so v00.15 keeps the last game's log as `vita3k.game.log`.
v00.15 is the PS Vita look: a home screen of bubbles with a LiveArea for each game (Vita3K's list
stays, HENkaku > System > Style), the **HENkaku** settings for all games and for each game, the
in-game HENkaku menu (L3 + R3) in sections and pages, and FSR 1 working on the PS4 (32-bit
shaders) with a sharpness setting. v00.16 names the whole app HENkaku (its PS4 icon, home screen
art and screens use the HENkaku ensō logo); it installs over Vita3K v00.15 and keeps its games
and settings. v00.16's log showed Mortal Kombat no longer short of CPU: its threads are half idle and
it holds 30 fps itself, waiting two vblanks for each frame in two calls (sceDisplayWaitSetFrameBuf,
then sceDisplayWaitVblankStart), which Vita3K's FPS hack (a vcount of 2 made 1) never caught.
v00.17 makes the FPS hack skip a frame's second wait too, and redoes the home screen as the Vita's
(bubbles at its size and places, a blue wave wallpaper, glossy bubbles, pages turning with their
rows following one another, a pressed bubble giving, LiveAreas as cards to the right, L1 / R1
between them, Triangle peels one away, Cross zooms into the game) drawn from sprites made once and
paced to the TV's refresh (v00.16 drew everything again, big soft circles included, for each
press), and the in-game menu shows the button symbols. Remember to install each new package from
`/data/pkg`.

v00.17's log (logs/v00.17-run1) showed fights at 14-60 fps with nothing saturated (GPU fence waits 0,
game and render threads about half busy): Vita3K made sceGxmDisplayQueueAddEntry, for a game with a
display queue of 1, wait until that very frame was on screen, so building a frame, the renderer and
the vblank ran one after another, and a frame a little over 16.7 ms took 33. v00.18 waits only for
the frame before, as the Vita does (HENkaku > CPU, or Speed in game: Frame queue), and the perf line
adds how long frames wait for the renderer. v00.20 logs which call a stuck game thread waits in (and where one spins); v00.21 adds who holds the locks they wait for. v00.22 runs the threads a game pins to one Vita core one at a time, as on the Vita (God of War Collection deadlocked in FIOS), and says when a VPK is a Vitamin dump. v00.23 finds the game a launcher starts whatever its case (God of War Collection starts GOW1.self, copied as gow1.self). v00.25 repacks vertices whose attributes are not 4 byte aligned, which the PS4 GPU fetched wrong (God of War II: spikes, blocks for letters). v00.26-v00.28 add profilers (HENkaku > Diagnostics, each can be off); v00.29 copies vertex data from each draw's first vertex. v00.30 adds Controls (all games and per game, also in the in-game menu): any DualShock 4 button can give any Vita button, PS TV button or a touch at one of nine places of the front screen or the rear touch pad, and the touch pad can be the front screen, the rear pad, both halves or nothing. v00.31 makes L2/R2 rear touches and L3/R3 front touches by default. v00.32 takes upstream fixes not merged yet (Vita3K PRs 4146 display queue order, 4144 and 4207 shader translation, 4235 save slots, 4251 linear YUV422 textures, 4139 downscaled surfaces, 4204 param.sfo checks, 4284 NGS prewritten PCM, 4250 save data manager, parts of 4220 and 4252) and fixes Vita3K issues 4218 (an audio decode writing past its buffer), 3323 (an ATRAC9 division by zero) and 4282 (the page allocator going below its start). v00.19 adds HENkaku > Look (themes, a moving wave,
pictures from `/data/Vita3K/wallpapers` as the wallpaper) and an About page.

HENkaku for the PS4 is made by **iHaiDeeZ / ShiroKlein** ([github.com/iHaiDeeZ](https://github.com/iHaiDeeZ)).

## Using it

1. Install `out/HENkaku-vXX.YY.pkg` (`out/Vita3K-vXX.YY.pkg` up to v00.15) with GoldHEN's Package
   Installer and start **HENkaku**.
2. The first time, the launcher downloads the PS Vita firmware (3.74, 128 MiB) and font package
   (54 MiB) from Sony's update server and installs them. Circle stops the download (it carries on
   later, and doesn't start by itself again); Square starts it. Without a connection, copy Sony's
   update files (`PSVUPDAT.PUP`, `PSP2UPDAT.PUP`) to `/data/Vita3K/install/` and install them
   like a game.
3. Put games where the PS4 can see them: over FTP in **`/data/Vita3K/install/`** (or anywhere
   under `/data`), or on a USB drive. Vita3K installs `.vpk` and `.zip` archives, dumped game
   folders (with `sce_sys/param.sfo`), and `.pkg` files with a `.zrif` text file of the same name
   holding the zRIF (or their `.rif` license installed first).
4. On the home screen open **Install** (or press **Triangle**): the install screen opens on
   `/data/Vita3K/install`. **Cross** installs the file picked (or opens a folder), **Square**
   installs everything in the folder, **Circle** goes up, to the list of places: the install
   folder, the PS4's storage (`/data`) and the USB drives. What installs from the install folder
   moves to `install/done/`; anywhere else it stays.
5. Back home (the game just installed is picked), **Cross** opens its LiveArea, **Cross** again
   starts it.

A NoNpDrm dump (with `sce_sys/package/work.bin`) copied straight into
`/data/Vita3K/fs/ux0/app/` is still encrypted; the first time it starts, the launcher decrypts it
in place (as installing it would have) and installs its license. Installing it from the install
screen instead is the same, from anywhere but Vita3K's own folders.

### The home screen

As on a PS Vita: bubbles, ten to a page in rows of 3, 4 and 3, the pages one under another (the
dots at the right). The D-pad or the left stick moves between them, L1 / R1 go a page up or down.

| Bubble | Cross opens |
|---|---|
| **HENkaku** (the ensō) | the settings of all games |
| **Install** | the install screen |
| a game | its LiveArea: its background and start picture (`sce_sys/livearea/contents`), **Cross** starts it, **Square** opens its own settings, **Circle** goes back |

**Square** on a game's bubble opens its settings, **Triangle** the install screen, **OPTIONS** the
HENkaku settings (Quit Vita3K is there too). Vita3K's list (HENkaku > System > Style) works as it
did, Cross starting the game picked, with Square for its settings and OPTIONS for HENkaku.

### HENkaku: the settings

Pages within pages, with sections: **Display** (show FPS and where, screen filter, FSR 1's
sharpness, texture filtering), **Graphics** (resolution, GPU accuracy, frame read-back, shader
compiling, texture checks, the 30 to 60 FPS hack), **Audio** (volume, NGS), **CPU** (dynarmic's
optimisations, the game's threads on one Jaguar cluster or all cores), **System** (the home
screen's style, the games' enter button). Left / right or Cross change a setting, Circle goes back.

- From the HENkaku bubble: **all games** (Vita3K's `config.yml`, and `ps4.cfg` for the PS4's own).
- From a game (Square, or its LiveArea): **that game**, over all games' settings: saved in
  `config/config_<game>.xml` from the first change; "Use the settings of all games" removes it.
- In a game (**L3 + R3**): the HENkaku menu. Resume and Exit, the settings that change at once
  (Display, Audio, Speed: show FPS, filter, FSR 1 sharpness, volume, shader compiling, FPS hack),
  and **This game**: the game's own pages, for its next start (resolution, accuracy, ...).

Settings marked "next start" apply when the game starts again (the app starts over after every
game, so: Exit, then start it).

| DualShock 4 | PS Vita |
|---|---|
| Cross / Circle / Square / Triangle, D-pad, sticks | the same |
| L1 / R1 | L / R |
| OPTIONS | START |
| Touchpad click | SELECT |
| Touchpad | front touch screen |
| L2 / R2 / L3 / R3 | the PS TV's |
| **L3 + R3** | the HENkaku menu (pauses the game) |

When a game ends (or Exit in the HENkaku menu) the app restarts into the launcher.

## On the console

| Path | What |
|---|---|
| `/data/Vita3K/install` | where the install screen (Triangle) opens; `done/` afterwards |
| `/data/Vita3K/cache/download/stopped` | there after Circle stopped the firmware download (Square starts it again) |
| `/data/Vita3K/fs` | the Vita's file system: `ux0` (apps, saves), `vs0`/`os0`/`sa0`/`pd0` (firmware) |
| `/data/Vita3K/config.yml` | Vita3K's settings: all games' |
| `/data/Vita3K/config/config_<game>.xml` | a game's own settings (HENkaku, from the game) |
| `/data/Vita3K/ps4.cfg` | the PS4's own: home screen style, FSR 1 sharpness, game threads |
| `/data/Vita3K/cache` | shader cache; `download/`: the firmware while it downloads |
| `/data/Vita3K` | `vita3k.log`, `boot-trace.log` (startup milestones), `crash.log` (appended to); the run before's are `vita3k.prev.log` and `boot-trace.prev.log` (the app starts over after every game, so a game's log is there), and the last game's run stays as `vita3k.game.log` |
| `/data/Vita3K/trace-log` | an empty file there keeps Vita3K's trace and debug lines in the log (left out otherwise: thousands while a game loads, each a write to the file) |
| `/app0` | the package: `eboot.bin`, `data/`, `shaders-builtin/`, `icons/`, `fonts/` |

Title ID `VITA00003` (content ID `IV0000-VITA00003_00-VITA3KPS4EMU0000`).

## How the port works

- **Frontend** (`vita3k/ps4/` in the patch): `ps4_main.cpp` replaces the Qt UI and the SDL window.
  The launcher (`ps4_launcher.cpp`, `ps4_canvas.cpp`: the game list and the install screen, which
  browses the install folder, `/data` and `/mnt/usbN`) is drawn by the CPU into VideoOut buffers
  12-13; whether it reached the screen is in `boot-trace.log` (`launcher: screen ready`,
  `first frame`). Its text is in the PS Vita's fonts once Vita3K has the font package
  (`sa0/data/font/pvf`: Latin, Japanese, Chinese, Korean), else in the Roboto in the package
  (`fonts/`); the PS4's own fonts (`/preinst/common/font`) aren't readable by the app on the test
  console (`boot-trace.log` says which it got). The game runs in an `app::AppSessionController` session like
  the SDL frontend's. A session leaves threads, guest memory and the GPU device behind, so when the
  game ends the app restarts itself (`sceSystemServiceLoadExec`) back into the launcher; a game
  starting another executable restarts into it the same way. The home screen of bubbles, the
  LiveArea and the HENkaku settings pages are drawn the same way (`ps4_launcher.cpp`); the
  settings themselves are in `ps4_settings.cpp` as `overlay::pause_menu_item` pages, which the
  in-game HENkaku menu (Vita3K's pause overlay, `overlay/src/pause_overlay.cpp`, now pages and
  sections with an icon) draws on its own. A change is made the way Vita3K's settings dialog
  makes it: all games' through `config::save_current_config`, a game's into its custom config,
  in a game through `app::commit_settings` (v00.14's quick menu changed `Config`'s global members
  and saved a default `current_config` over them, as `Config`'s assignment leaves that out).
- **Graphics**: Vita3K's Vulkan renderer on DolphinPS4's RADV port, linked in. `ps4_wsi.cpp` (M33's
  WSI) adds `VK_EXT_headless_surface` and `VK_KHR_swapchain` on VideoOut (linear 1920x1080 images,
  GPU-side flips); the renderer gets its entry points from `ps4_vk_get_instance_proc_addr()` and
  its surface from the PS4 frame host (`renderer::FrameHost`). Memory mapping is off on the PS4:
  with it, shaders read guest memory through buffer device addresses, which ACO compiles to FLAT
  instructions on GFX7, and the PS4 kernel sets the FLAT apertures up for GNM (a PS4 PCSX2 port's
  first FLAT store hung the GPU; Mortal Kombat's fights hung it at a skinned model). Guest memory
  then goes through descriptors, as on GPUs without buffer device addresses. **FSR 1** (screen
  filter): Vita3K offers it only with 16-bit floats in shaders, which GCN 1.1 lacks, and with a
  swapchain a compute shader can write; on the PS4 it uses FSR 1's 32-bit path
  (`shaders-builtin/vulkan/fsr_filter_*_f32.comp`, the same EASU and RCAS passes) and the WSI
  gives its linear images storage use where the GPU can (else it says so in the log and FSR falls
  back to bilinear). The sharpening (RCAS stops) is a setting. FSR 3 isn't possible here: its
  upscaler and frame generation both need the game's motion vectors and depth, which a Vita game
  doesn't give and Vita3K can't make.
- **CPU**: dynarmic's x86-64 JIT (`patches/dynarmic-ps4.patch`). Only flexible memory can run code
  on the PS4 and there is a JIT per guest thread, so each 128 MiB code cache is a virtual range
  reservation committed in 256 KiB steps as code is emitted (system flexible memory, else regular),
  with a 512 KiB constant pool. The prelude (some 4700 fastmem fallbacks, about 1.7 MiB, written
  with no commit on the way: v00.05 faulted there) gets an 8 MiB window, cut back to what it used
  when it's done. Fastmem through dynarmic's POSIX fault handler (SIGSEGV and SIGBUS). The PS4's
  Jaguar cores have no FMA, so dynarmic's accurate floating point did NEON's reciprocal steps and
  estimates in soft-float, checked every result for NaNs and switched MXCSR around NEON
  instructions; the PS4 build turns on its unsafe floating-point optimizations (yuzu's "Unsafe"
  accuracy: unfused FMA, the host's estimates, no NaN fix-ups, no standard-FPSCR switch).
  Exclusive accesses (LDREX/STREX: the game's atomics and locks) are inline, the store a
  `lock cmpxchg` on the guest memory, instead of a call into the global monitor under its spin
  lock (dynarmic's fastmem exclusives, yuzu's default).
- **Speed** (`perf:` lines in `vita3k.log`, every 10 s while a game runs): the game's frame rate,
  the emulated vblanks a second (60 when the timing holds), where the render thread's time went
  (waiting for the game's commands, showing frames, waiting for the GPU), how long the game's
  threads waited for vblanks, and every thread busier than 3% of a core with its share (guest
  threads by their own names, `render`, `pipeline compiler`, `audio mixer`, `vblank`; each reads
  its own CPU clock, as the PS4 doesn't let a thread read another's). A Vita game that misses
  its vblank runs at 30 fps and, for most, at half speed. After it, a line for each busy game
  thread (`vita3k/ps4/ps4_perf.cpp`): its time in guest code (dynarmic) and its biggest imports
  (the HLE functions it calls: their work or their waits), in ms a second and calls a second.
  And at every game start, `PS4 memory test:` compares random reads through a 2 MiB aligned
  mapping with a misaligned one: whether the console gives the guest memory large pages.
- **Shaders**: Vita3K's USSE translator turned vector instructions predicated on `!p2` into
  unconditional ones (an upstream TODO); now they get their condition. Mortal Kombat's GPU hung
  right after such a shader, and a loop counting with one never ends: every translated loop also
  stops after 4096 turns on the PS4 (a GPU that never finishes gets the app killed, with no
  trace). PS4 shader cache version 1401, so older translations are made again. A GPU hang is
  logged by the RADV winsys in `/data/DolphinPS4/radv-ps4.log` and `gpu-hang.txt` (its paths are
  DolphinPS4's); an empty `/data/Vita3K/radv-trace` file turns on its flight recorder
  (`/data/DolphinPS4/flight`) and RADV's per-draw trace ids (`RADV_DEBUG=hang`, slower; it also
  ends the app on a hang instead of the PS4 freezing) to find the draw: `gpu-hang.txt`'s last
  trace write that was done is just before it.
- **Guest memory** (`mem/src/mem.cpp`): the Vita's 4 GiB address space is a virtual range
  reservation, backed 2 MiB at a time by direct memory mapped in place, 2 MiB aligned like the
  address so the PS4 can use one large page for it; a region goes back to a free list once
  nothing in it is allocated. Up to v00.13 it was backed 16 KiB at a time, with physical runs that
  didn't line up with the addresses: every guest page cost four of the CPU's 4 KiB TLB entries,
  and the JIT's loads and stores walked page tables (Jaguar's TLBs hold a few hundred entries). Write tracking uses `mprotect` and the
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
  `open` (with `O_DIRECTORY`) and `openat` remember which path each directory descriptor stands for
  (Boost opens the top of a directory walk with `open`, then the rest relative to it: v00.07 failed
  there). The kernel refuses relative
  names (EINVAL, which Boost throws on, where elsewhere they'd just not be found: v00.03 died on
  `status("ux0/app")`), so the wraps take them from the working directory. `realpath` (the C
  library's reads `/proc/self/fd/N` with a `readlink` stub, so libc++'s `canonical`, used by
  psvpfstools to decrypt dumps, failed) and `readlink` are wrapped, and so is `statvfs`: the C
  library's never fills in its result.
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
Upload from Windows (Git Bash): `scripts/upload-to-console.sh out/HENkaku-vXX.YY.pkg`.

## License

GPL-2.0-or-later, as Vita3K ([LICENSE](LICENSE)): the patches are modifications of Vita3K and
dynarmic (0BSD). The PS4 runtime in `port/` and the toolchain scripts come from the M33 / Resonance /
DolphinPS4 / Crema ports; `port/mesa/ac_ps4_drm.c` is the RADV winsys of the PS4 Mesa port (MIT).
`assets/henkaku-logo.png` is the HENkaku ensō logo (HENkaku by team molecule); `scripts/make-henkaku-art.py`
makes `assets/henkaku.png` (the menus' icon) and `sce_sys/icon0.png` / `pic1.png` from it.
`fonts/` is Roboto 3.009 (from Vita3K's Tracy submodule), under the SIL Open Font License 1.1
(`fonts/OFL-Roboto.txt`).
No PS Vita firmware, Sony system files or games are included: supply your own.
