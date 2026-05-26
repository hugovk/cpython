#ifndef Py_INTERNAL_COLORIZE_H
#define Py_INTERNAL_COLORIZE_H
#ifdef __cplusplus
extern "C" {
#endif

#ifndef Py_BUILD_CORE
#  error "this header requires Py_BUILD_CORE define"
#endif

#include <stdio.h>                // FILE

/* Determine if ANSI color codes may be emitted on the given stream.
 * Logic mirrors Lib/_colorize.py:can_colorize(). */
extern int _Py_can_colorize(FILE *f);

/* ANSI escape sequences for use from C code.
 * Matches the constants in Lib/_colorize.py:ANSIColors. */
#define _PY_ANSI_RESET    "\x1b[0m"
#define _PY_ANSI_BOLD     "\x1b[1m"
#define _PY_ANSI_CYAN     "\x1b[36m"
#define _PY_ANSI_GREY     "\x1b[90m"
#define _PY_ANSI_YELLOW   "\x1b[33m"

#ifdef __cplusplus
}
#endif
#endif /* !Py_INTERNAL_COLORIZE_H */
