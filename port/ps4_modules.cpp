// PS4: the system modules this port calls into, loaded before main (SMW's platform_ps4.cpp load_system_modules).
// Calling into a system library whose module isn't loaded ends the app without a word: v00.00 and v00.01 died in
// their first sceVideoOutOpen that way (no signal, no crash.log).
#include <cstdint>
#include <cstdio>

extern "C" int32_t sceSysmoduleLoadModuleInternal(uint32_t id);
extern "C" void ps4_boot_trace(const char* stage);  // ps4_crashlog.cpp

namespace {

__attribute__((constructor(102))) void load_system_modules() {
    const struct {
        const char* name;
        uint32_t id;
    } modules[] = {
        {"SystemService", 0x80000010}, {"UserService", 0x80000011}, {"VideoOut", 0x80000022},
        {"AudioOut", 0x80000001},      {"Pad", 0x80000024},
    };
    for (const auto& m : modules) {
        int r = sceSysmoduleLoadModuleInternal(m.id);
        if (r != 0) {
            char line[96];
            snprintf(line, sizeof line, "loading system module %s failed (%x)", m.name, unsigned(r));
            ps4_boot_trace(line);
        }
    }
    ps4_boot_trace("system modules loaded");
}

}  // namespace
