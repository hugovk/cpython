/* Helpers for emitting ANSI color codes from C code.
 *
 * Keep behaviour in sync with Lib/_colorize.py:can_colorize().
 */

#include "Python.h"
#include "pycore_colorize.h"

#include <stdlib.h>               // getenv()
#include <string.h>               // strcmp()
#ifdef MS_WINDOWS
#  include <windows.h>            // GetStdHandle(), GetConsoleMode()
#  include <io.h>                 // isatty(), fileno()
#else
#  include <unistd.h>             // isatty()
#endif

int
_Py_can_colorize(FILE *f)
{
    const char *env;

    env = Py_GETENV("PYTHON_COLORS");
    if (env) {
        if (strcmp(env, "0") == 0) {
            return 0;
        }
        if (strcmp(env, "1") == 0) {
            return 1;
        }
    }
    if (getenv("NO_COLOR")) {
        return 0;
    }
    if (getenv("FORCE_COLOR")) {
        return 1;
    }
    env = getenv("TERM");
    if (env && strcmp(env, "dumb") == 0) {
        return 0;
    }
#if defined(MS_WINDOWS) && defined(HAVE_WINDOWS_CONSOLE_IO)
    {
        DWORD mode = 0;
        DWORD nStdHandle = (f == stderr) ? STD_ERROR_HANDLE
                                         : STD_OUTPUT_HANDLE;
        HANDLE handle = GetStdHandle(nStdHandle);
        if (!GetConsoleMode(handle, &mode)
            || !(mode & ENABLE_VIRTUAL_TERMINAL_PROCESSING))
        {
            return 0;
        }
    }
#endif
    return isatty(fileno(f));
}
