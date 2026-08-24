/**
 * atb_nshome_interpose.m
 *
 * DYLD interpose library for ATBClone hard clones of macOS Electron apps.
 *
 * Problem: macOS Cocoa's NSHomeDirectory() reads from the password database
 * (getpwuid), NOT from the HOME env var. Electron/Chromium uses NSHomeDirectory()
 * to compute the user data path (~/Library/Application Support/<AppName>), which
 * is also where the ProcessSingleton socket lives. This means clones share the
 * same singleton socket as the original app, causing the clone to detect the
 * original as a running instance and exit immediately.
 *
 * Fix: Replace NSHomeDirectory() with a version that reads the HOME env var,
 * making the Cocoa-derived paths consistent with the HOME override in the
 * clone's wrapper script.
 *
 * Compile (arm64):
 *   clang -arch arm64 -dynamiclib \
 *     -framework Foundation \
 *     -install_name @executable_path/atb_nshome.dylib \
 *     -o atb_nshome.dylib atb_nshome_interpose.m
 *
 * Usage: export DYLD_INSERT_LIBRARIES=/path/to/atb_nshome.dylib
 * (HOME must already be set to the clone-specific home directory)
 */

#import <Foundation/Foundation.h>
#include <pwd.h>
#include <unistd.h>
#include <stdlib.h>

// ---------------------------------------------------------------------------
// Replacement NSHomeDirectory
// Returns HOME env var if set, otherwise falls back to the passwd database.
// ---------------------------------------------------------------------------
NSString* _atb_NSHomeDirectory(void) {
    const char* home = getenv("HOME");
    if (home && home[0] != '\0') {
        return [NSString stringWithUTF8String:home];
    }
    // Fallback: read from passwd database (can't call original without recursion)
    struct passwd* pw = getpwuid(getuid());
    if (pw && pw->pw_dir && pw->pw_dir[0] != '\0') {
        return [NSString stringWithUTF8String:pw->pw_dir];
    }
    return @"/tmp";
}

// ---------------------------------------------------------------------------
// Interpose table - replaces NSHomeDirectory at dyld symbol-binding time.
// Applied to ALL images in the process (including Lark Framework.framework).
// ---------------------------------------------------------------------------
typedef struct {
    const void* replacer;
    const void* replacee;
} _ATBInterpose;

extern NSString* NSHomeDirectory(void);

__attribute__((used))
static const _ATBInterpose _atb_interposers[]
    __attribute__((section("__DATA,__interpose"))) = {
    { (const void*)_atb_NSHomeDirectory, (const void*)NSHomeDirectory },
};
