import os
import sys

COLORIZE = True


# types
if False:
    from typing import IO
    from _colorize_theme import Theme


class ANSIColors:
    RESET = "\x1b[0m"
    BLACK = "\x1b[30m"
    BLUE = "\x1b[34m"
    CYAN = "\x1b[36m"
    GREEN = "\x1b[32m"
    GREY = "\x1b[90m"
    MAGENTA = "\x1b[35m"
    RED = "\x1b[31m"
    WHITE = "\x1b[37m"  # more like LIGHT GRAY
    YELLOW = "\x1b[33m"

    BOLD = "\x1b[1m"
    BOLD_BLACK = "\x1b[1;30m"  # DARK GRAY
    BOLD_BLUE = "\x1b[1;34m"
    BOLD_CYAN = "\x1b[1;36m"
    BOLD_GREEN = "\x1b[1;32m"
    BOLD_MAGENTA = "\x1b[1;35m"
    BOLD_RED = "\x1b[1;31m"
    BOLD_WHITE = "\x1b[1;37m"  # actual WHITE
    BOLD_YELLOW = "\x1b[1;33m"

    # intense = like bold but without being bold
    INTENSE_BLACK = "\x1b[90m"
    INTENSE_BLUE = "\x1b[94m"
    INTENSE_CYAN = "\x1b[96m"
    INTENSE_GREEN = "\x1b[92m"
    INTENSE_MAGENTA = "\x1b[95m"
    INTENSE_RED = "\x1b[91m"
    INTENSE_WHITE = "\x1b[97m"
    INTENSE_YELLOW = "\x1b[93m"

    BACKGROUND_BLACK = "\x1b[40m"
    BACKGROUND_BLUE = "\x1b[44m"
    BACKGROUND_CYAN = "\x1b[46m"
    BACKGROUND_GREEN = "\x1b[42m"
    BACKGROUND_MAGENTA = "\x1b[45m"
    BACKGROUND_RED = "\x1b[41m"
    BACKGROUND_WHITE = "\x1b[47m"
    BACKGROUND_YELLOW = "\x1b[43m"

    INTENSE_BACKGROUND_BLACK = "\x1b[100m"
    INTENSE_BACKGROUND_BLUE = "\x1b[104m"
    INTENSE_BACKGROUND_CYAN = "\x1b[106m"
    INTENSE_BACKGROUND_GREEN = "\x1b[102m"
    INTENSE_BACKGROUND_MAGENTA = "\x1b[105m"
    INTENSE_BACKGROUND_RED = "\x1b[101m"
    INTENSE_BACKGROUND_WHITE = "\x1b[107m"
    INTENSE_BACKGROUND_YELLOW = "\x1b[103m"


ColorCodes = set()
NoColors = ANSIColors()

for attr, code in ANSIColors.__dict__.items():
    if not attr.startswith("__"):
        ColorCodes.add(code)
        setattr(NoColors, attr, "")


def get_colors(
    colorize: bool = False, *, file: IO[str] | IO[bytes] | None = None
) -> ANSIColors:
    if colorize or can_colorize(file=file):
        return ANSIColors()
    else:
        return NoColors


def decolor(text: str) -> str:
    """Remove ANSI color codes from a string."""
    for code in ColorCodes:
        text = text.replace(code, "")
    return text


def can_colorize(*, file: IO[str] | IO[bytes] | None = None) -> bool:

    def _safe_getenv(k: str, fallback: str | None = None) -> str | None:
        """Exception-safe environment retrieval. See gh-128636."""
        try:
            return os.environ.get(k, fallback)
        except Exception:
            return fallback

    if file is None:
        file = sys.stdout

    if not sys.flags.ignore_environment:
        if _safe_getenv("PYTHON_COLORS") == "0":
            return False
        if _safe_getenv("PYTHON_COLORS") == "1":
            return True
    if _safe_getenv("NO_COLOR"):
        return False
    if not COLORIZE:
        return False
    if _safe_getenv("FORCE_COLOR"):
        return True
    if _safe_getenv("TERM") == "dumb":
        return False

    if not hasattr(file, "fileno"):
        return False

    if sys.platform == "win32":
        try:
            import nt

            if not nt._supports_virtual_terminal():
                return False
        except (ImportError, AttributeError):
            return False

    try:
        return os.isatty(file.fileno())
    except OSError:
        return hasattr(file, "isatty") and file.isatty()


#
# Experimental theming support (see gh-133346)
#
# The theme classes (`Theme`, `ThemeSection`, the per-area dataclasses such
# as `Argparse`, `Ast`, ..., `Traceback`, `Unittest`) along with
# `default_theme`, `theme_no_color`, `light_profiler_theme`, `set_theme`,
# and `get_theme` live in `_colorize_theme` and are lazily imported below
# using PEP 810 lazy imports.  This keeps `import _colorize` (and therefore
# `import traceback`) cheap when no theming is needed.
#
# Usage:
#
# - Create a theme by copying an existing `Theme` with one or more sections
#   replaced, using `default_theme.copy_with()`;
# - create a theme section by copying an existing `ThemeSection` with one or
#   more colors replaced, using for example `default_theme.syntax.copy_with()`;
# - create a theme from scratch by instantiating a `Theme` data class with
#   the required sections (which are also dataclass instances).
#
# Then call `_colorize.set_theme(your_theme)` to set it.
#
# Put your theme configuration in $PYTHONSTARTUP for the interactive shell,
# or sitecustomize.py in your virtual environment or Python installation for
# other uses.  Your applications can call `_colorize.set_theme()` too.
#
# Note that thanks to the dataclasses providing default values for all fields,
# creating a new theme or theme section from scratch is possible without
# specifying all keys.
#
# For example, here's a theme that makes punctuation and operators less prominent:
#
#   try:
#       from _colorize import set_theme, default_theme, Syntax, ANSIColors
#   except ImportError:
#       pass
#   else:
#       theme_with_dim_operators = default_theme.copy_with(
#           syntax=Syntax(op=ANSIColors.INTENSE_BLACK),
#       )
#       set_theme(theme_with_dim_operators)
#       del set_theme, default_theme, Syntax, ANSIColors, theme_with_dim_operators
#
# Guarding the import ensures that your .pythonstartup file will still work in
# Python 3.13 and older. Deleting the variables ensures they don't remain in your
# interactive shell's global scope.

lazy from _colorize_theme import (
    Theme,
    ThemeSection,
    CursesColors,
    Argparse,
    Ast,
    Difflib,
    FancyCompleter,
    HttpServer,
    LiveProfiler,
    Pickletools,
    Syntax,
    Timeit,
    Tokenize,
    Traceback,
    Unittest,
    LiveProfilerLight,
    default_theme,
    theme_no_color,
    light_profiler_theme,
    set_theme,
)


class _ShutdownTheme:
    """All-empty stand-in returned by `get_theme()` if `_colorize_theme` cannot
    be imported. Happens during late interpreter shutdown when called
    from a `__del__` that is the first user of the theme machinery."""

    def __getattr__(self, _):
        return self

    def __getitem__(self, _):
        return ""

    def __format__(self, _):
        return ""

    def __str__(self):
        return ""

    def __add__(self, other):
        return other

    __radd__ = __add__


_shutdown_theme = _ShutdownTheme()


def get_theme(
    *,
    tty_file: IO[str] | IO[bytes] | None = None,
    force_color: bool = False,
    force_no_color: bool = False,
) -> Theme:
    """Returns the currently set theme, potentially in a zero-color variant.

    In cases where colorizing is not possible (see `can_colorize`), the returned
    theme contains all empty strings in all color definitions.
    See `Theme.no_colors()` for more information.

    It is recommended not to cache the result of this function for extended
    periods of time because the user might influence theme selection by
    the interactive shell, a debugger, or application-specific code. The
    environment (including environment variable state and console configuration
    on Windows) can also change in the course of the application life cycle.
    """
    try:
        from _colorize_theme import get_theme
        return get_theme(
            tty_file=tty_file,
            force_color=force_color,
            force_no_color=force_no_color,
        )
    except ImportError:
        # Late interpreter shutdown: meta_path has been torn down. Return a
        # minimal stand-in so traceback formatting from `__del__` still works.
        return _shutdown_theme  # type: ignore[return-value]
