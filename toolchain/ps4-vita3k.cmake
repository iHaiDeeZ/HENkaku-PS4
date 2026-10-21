# Toolchain for Vita3K on PS4: DolphinPS4/Crema's love-ps4-style modern toolchain (clang 21 +
# libc++ 21, ld.lld called directly, OpenOrbis CRT/libc), with this port's sysroot (seeded from
# M33's: Boost 1.89, OpenSSL, curl, zlib, zstd, FFmpeg 7.1, SDL3) on the find path ahead of
# PacBrew's.
include(${CMAKE_CURRENT_LIST_DIR}/ps4-love-modern.cmake)

list(PREPEND CMAKE_FIND_ROOT_PATH ${PS4_SYSROOT})
set(CMAKE_TRY_COMPILE_PLATFORM_VARIABLES ${CMAKE_TRY_COMPILE_PLATFORM_VARIABLES} CMAKE_FIND_ROOT_PATH)
# No -I for PacBrew's port libraries (usr/include: old fmt, SDL2, ...) nor for our sysroot: an -I is
# searched before every target's own include directories, so the sysroot's fmt, glslang and pugixml
# headers would hide the versions Vita3K builds from external/. The sysroot's headers come in as
# -isystem through the imported targets (Boost, OpenSSL, CURL, SDL3, ZLIB) and the ffmpeg target.
foreach(_lang C CXX ASM)
    string(REPLACE "-I${OPENORBIS}/usr/include" ""
           CMAKE_${_lang}_FLAGS_INIT "${CMAKE_${_lang}_FLAGS_INIT}")
endforeach()
