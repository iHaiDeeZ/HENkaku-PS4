# Building HENkaku

```
scripts/seed-build-tree.sh          # ~/vita3k-build from M33's sysroot and RADV build
scripts/clone-vita3k.sh             # upstream Vita3K at patches/BASE.txt + the PS4 patches, branch ps4
scripts/build-sdl3.sh               # SDL3 for the console, into the sysroot
scripts/rebuild-vita3k.sh           # configure + build (logs in ~/vita3k-build/logs)
VITA3K_VERSION=01.00 scripts/package-vita3k.sh
scripts/save-patch.sh "message"     # commit ~/vita3k-build/src/vita3k and refresh patches/
```

Run the scripts from WSL through `~/vita3k` (the space in "PS4 Projects" breaks linker flags).
Upload from Windows (Git Bash): `scripts/upload-to-console.sh out/HENkaku-vXX.YY.pkg`.

The build starts from M33's build tree in WSL (`~/m33-build`: its libc++ 21 sysroot with Boost 1.89, OpenSSL,
curl, zlib, zstd, glslang and FFmpeg 7.1) and the RADV/GNM Mesa build of Crema's tree as TOTK uses it
(`~/totk-build/build/mesa`, Oct 17: GPU submissions on their own thread), which `scripts/seed-build-tree.sh` copies
into `~/vita3k-build` once. How the port itself works is in [PORT.md](PORT.md).
