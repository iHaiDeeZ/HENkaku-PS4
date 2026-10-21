// The *at file functions (fstatat, openat, unlinkat, fchmodat, utimensat) on top of the path ones,
// and statvfs.
// The OpenOrbis C library's fstatat, unlinkat, fchmodat and utimensat only fail with ENOSYS (the
// PS4 has no such system calls for apps), and the sysroot's Boost.Filesystem (built with the POSIX
// *at APIs) and libc++'s std::filesystem go through them for every status, directory listing and
// removal: Vita3K v00.02 died at its first create_directories ("Function not implemented").
// With the linker's --wrap (toolchain/ps4-love-style.cmake) a name relative to a directory
// descriptor is resolved against the path that descriptor was opened on (openat remembers each
// directory's until it's closed), and stat, lstat, open, unlink, rmdir, chmod and utimes, which
// the kernel has, do the work.

#include <errno.h>
#include <fcntl.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/statvfs.h>
#include <sys/time.h>
#include <unistd.h>

#include <atomic>
#include <mutex>
#include <string>
#include <unordered_map>

extern "C" {
void ps4_boot_trace(const char* stage);   // ps4_crashlog.cpp
int ps4_netfs_is_path(const char* path);  // ps4_netfs.cpp
}

namespace {

// The directories openat opened: descriptor -> path (made on first use: static constructors may
// list directories before this file's run)
struct Dirs {
    std::mutex lock;
    std::unordered_map<int, std::string> paths;
};

Dirs& dirs() {
    static Dirs s_dirs;
    return s_dirs;
}

constinit std::atomic<int> s_count{0};

// The path a name relative to dirfd stands for; false (with errno) when dirfd isn't a directory
// openat opened.
bool resolve(int dirfd, const char* path, std::string& out) {
    if (!path) {
        errno = EFAULT;
        return false;
    }
    if (path[0] == '/' || (dirfd == AT_FDCWD && !*path)) {
        out = path;
        return true;
    }
    if (dirfd == AT_FDCWD) {
        // The kernel turns relative names down (EINVAL, where elsewhere they'd simply not be
        // there): Vita3K v00.03 died on Boost's status("ux0/app"). They're the working directory's.
        char cwd[1024];
        out = getcwd(cwd, sizeof(cwd)) ? cwd : "/";
        if (out.empty() || out.back() != '/')
            out += '/';
        out += path;
        return true;
    }
    {
        Dirs& d = dirs();
        std::lock_guard lock(d.lock);
        const auto it = d.paths.find(dirfd);
        if (it != d.paths.end()) {
            out = it->second;
            if (*path) {
                if (out.empty() || out.back() != '/')
                    out += '/';
                out += path;
            }
            return true;
        }
    }
    static std::atomic<int> s_logged{0};
    if (s_logged.fetch_add(1) < 8) {
        char line[200];
        snprintf(line, sizeof(line), "fileat: descriptor %d isn't a directory openat opened (%s)", dirfd, path);
        ps4_boot_trace(line);
    }
    errno = EBADF;
    return false;
}

}  // namespace

extern "C" int __wrap_fstatat(int dirfd, const char* path, struct stat* st, int flags) {
    if (path && !*path && (flags & AT_EMPTY_PATH))
        return fstat(dirfd, st);
    std::string full;
    if (!resolve(dirfd, path, full))
        return -1;
    // lstat doesn't know the network shares (ps4_netfs.cpp), which have no links anyway
    if ((flags & AT_SYMLINK_NOFOLLOW) && !ps4_netfs_is_path(full.c_str()))
        return lstat(full.c_str(), st);
    return stat(full.c_str(), st);
}

extern "C" int __wrap_openat(int dirfd, const char* path, int flags, ...) {
    int mode = 0;
    if (flags & O_CREAT) {
        va_list args;
        va_start(args, flags);
        mode = va_arg(args, int);
        va_end(args);
    }
    std::string full;
    if (!resolve(dirfd, path, full))
        return -1;
    const int fd = open(full.c_str(), flags, mode);
    if (fd < 0)
        return fd;
    struct stat st;
    if (fstat(fd, &st) == 0 && S_ISDIR(st.st_mode)) {
        Dirs& d = dirs();
        std::lock_guard lock(d.lock);
        if (d.paths.insert_or_assign(fd, full).second)
            s_count++;
    }
    return fd;
}

extern "C" int __wrap_unlinkat(int dirfd, const char* path, int flags) {
    std::string full;
    if (!resolve(dirfd, path, full))
        return -1;
    return (flags & AT_REMOVEDIR) ? rmdir(full.c_str()) : unlink(full.c_str());
}

// (no lchmod or lutimes on the PS4: links are followed, there are none in its file systems)
extern "C" int __wrap_fchmodat(int dirfd, const char* path, mode_t mode, int flags) {
    (void)flags;
    std::string full;
    if (!resolve(dirfd, path, full))
        return -1;
    return chmod(full.c_str(), mode);
}

extern "C" int __wrap_utimensat(int dirfd, const char* path, const struct timespec times[2], int flags) {
    (void)flags;
    std::string full;
    if (!resolve(dirfd, path, full))
        return -1;
    if (!times)
        return utimes(full.c_str(), nullptr);
    struct timeval tv[2];
    struct stat st;
    bool have_st = false;
    for (int i = 0; i < 2; i++) {
        if (times[i].tv_nsec == UTIME_NOW) {
            gettimeofday(&tv[i], nullptr);
        } else if (times[i].tv_nsec == UTIME_OMIT) {
            if (!have_st) {
                if (stat(full.c_str(), &st) != 0)
                    return -1;
                have_st = true;
            }
            const struct timespec& kept = i == 0 ? st.st_atim : st.st_mtim;
            tv[i].tv_sec = kept.tv_sec;
            tv[i].tv_usec = kept.tv_nsec / 1000;
        } else {
            tv[i].tv_sec = times[i].tv_sec;
            tv[i].tv_usec = times[i].tv_nsec / 1000;
        }
    }
    return utimes(full.c_str(), tv);
}

// statvfs: the C library's asks the kernel (fstatfs) and then fills nothing in, so Boost's space()
// (games asking how much room there is) got whatever was on the stack.
extern "C" int _fstatfs(int fd, void* buf);  // libkernel

extern "C" int __wrap_statvfs(const char* path, struct statvfs* out) {
    // The kernel's struct statfs (FreeBSD's): the counts come after version, type and flags. The
    // rest is as long as FreeBSD 12's, whichever size the kernel writes.
    struct KernelStatfs {
        uint32_t version;
        uint32_t type;
        uint64_t flags;
        uint64_t bsize;  // the unit of the block counts
        uint64_t iosize;
        uint64_t blocks;
        uint64_t bfree;
        int64_t bavail;
        uint64_t files;
        int64_t ffree;
        uint8_t rest[2344 - 72];
    };
    const int fd = open(path, O_RDONLY);
    if (fd < 0)
        return -1;
    KernelStatfs fs{};
    const int result = _fstatfs(fd, &fs);
    const int saved = errno;
    close(fd);
    if (result != 0) {
        errno = saved;
        return -1;
    }
    memset(out, 0, sizeof(*out));
    out->f_bsize = out->f_frsize = fs.bsize;
    out->f_blocks = fs.blocks;
    out->f_bfree = fs.bfree;
    out->f_bavail = fs.bavail > 0 ? fs.bavail : 0;
    out->f_files = fs.files;
    out->f_ffree = out->f_favail = fs.ffree > 0 ? fs.ffree : 0;
    out->f_namemax = 255;
    return 0;
}

// From __wrap_close (ps4_crashlog.cpp), before the descriptor goes: it no longer names a directory.
extern "C" void ps4_fileat_closed(int fd) {
    if (s_count.load(std::memory_order_relaxed) == 0)
        return;
    Dirs& d = dirs();
    std::lock_guard lock(d.lock);
    if (d.paths.erase(fd))
        s_count--;
}
