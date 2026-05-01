import os
import sys

COLORIZE = True


# types
if False:
    from typing import IO, Literal, Self, ClassVar
    from collections.abc import Callable, Iterator
    from dataclasses import Field
    _theme: Theme


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


class CursesColors:
    """Curses color constants for terminal UI theming."""
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    DEFAULT = -1


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
#
# To keep `import _colorize` (and therefore `import traceback`) cheap, the
# `dataclasses` module and the Theme classes below are not loaded until
# something actually needs them.  The names are resolved lazily through the
# module-level `__getattr__`, and `get_theme()`/`set_theme()` invoke
# `_build_themes()` on first call.

_LAZY_THEME_NAMES = frozenset({
    "Argparse",
    "Ast",
    "Difflib",
    "FancyCompleter",
    "HttpServer",
    "LiveProfiler",
    "LiveProfilerLight",
    "Pickletools",
    "Syntax",
    "Theme",
    "ThemeSection",
    "Timeit",
    "Tokenize",
    "Traceback",
    "Unittest",
    "default_theme",
    "light_profiler_theme",
    "theme_no_color",
})


class _ShutdownTheme:
    """All-empty stand-in returned by `get_theme()` if the theme machinery
    cannot be built. Happens during late interpreter shutdown when called
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


def _build_themes() -> None:
    """Define the Theme dataclasses and install them as module globals.

    Called on first access to `get_theme`/`set_theme` or any of the names
    in `_LAZY_THEME_NAMES`.  Subsequent calls short-circuit because the
    names live in `globals()` after the first run, so attribute lookups
    bypass the module-level `__getattr__` entirely.
    """
    g = globals()
    if "Theme" in g:
        return

    import builtins
    from collections.abc import Mapping
    from dataclasses import dataclass, field, fields

    class ThemeSection(Mapping[str, str]):
        """A mixin/base class for theme sections.

        It enables dictionary access to a section, as well as implements convenience
        methods.
        """

        # The two types below are just that: types to inform the type checker that the
        # mixin will work in context of those fields existing
        __dataclass_fields__: ClassVar[dict[str, Field[str]]]
        _name_to_value: Callable[[str], str]

        def __post_init__(self) -> None:
            name_to_value = {}
            for color_name in self.__dataclass_fields__:
                name_to_value[color_name] = getattr(self, color_name)
            super().__setattr__("_name_to_value", name_to_value.__getitem__)

        def copy_with(self, **kwargs: str) -> Self:
            color_state = {
                name: kwargs.get(name, getattr(self, name))
                for name in self.__dataclass_fields__
            }
            return type(self)(**color_state)

        @classmethod
        def no_colors(cls) -> Self:
            color_state = {name: "" for name in cls.__dataclass_fields__}
            return cls(**color_state)

        def __getitem__(self, key: str) -> str:
            return self._name_to_value(key)

        def __len__(self) -> int:
            return len(self.__dataclass_fields__)

        def __iter__(self) -> Iterator[str]:
            return iter(self.__dataclass_fields__)

    @dataclass(frozen=True, kw_only=True)
    class Argparse(ThemeSection):
        usage: str = ANSIColors.BOLD_BLUE
        prog: str = ANSIColors.BOLD_MAGENTA
        prog_extra: str = ANSIColors.MAGENTA
        heading: str = ANSIColors.BOLD_BLUE
        summary_long_option: str = ANSIColors.CYAN
        summary_short_option: str = ANSIColors.GREEN
        summary_label: str = ANSIColors.YELLOW
        summary_action: str = ANSIColors.GREEN
        long_option: str = ANSIColors.BOLD_CYAN
        short_option: str = ANSIColors.BOLD_GREEN
        label: str = ANSIColors.BOLD_YELLOW
        action: str = ANSIColors.BOLD_GREEN
        default: str = ANSIColors.GREY
        interpolated_value: str = ANSIColors.YELLOW
        reset: str = ANSIColors.RESET
        error: str = ANSIColors.BOLD_MAGENTA
        warning: str = ANSIColors.BOLD_YELLOW
        message: str = ANSIColors.MAGENTA

    @dataclass(frozen=True, kw_only=True)
    class Ast(ThemeSection):
        node: str = ANSIColors.CYAN
        field: str = ANSIColors.BLUE
        attribute: str = ANSIColors.GREY
        string: str = ANSIColors.GREEN
        number: str = ANSIColors.YELLOW
        keyword: str = ANSIColors.BOLD_BLUE
        reset: str = ANSIColors.RESET

    @dataclass(frozen=True, kw_only=True)
    class Difflib(ThemeSection):
        """A 'git diff'-like theme for `difflib.unified_diff`."""
        added: str = ANSIColors.GREEN
        context: str = ANSIColors.RESET  # context lines
        header: str = ANSIColors.BOLD  # eg "---" and "+++" lines
        hunk: str = ANSIColors.CYAN  # the "@@" lines
        removed: str = ANSIColors.RED
        reset: str = ANSIColors.RESET

    @dataclass(frozen=True, kw_only=True)
    class FancyCompleter(ThemeSection):
        # functions and methods
        function: builtins.str = ANSIColors.BOLD_BLUE
        builtin_function_or_method: builtins.str = ANSIColors.BOLD_BLUE
        method: builtins.str = ANSIColors.BOLD_CYAN
        method_wrapper: builtins.str = ANSIColors.BOLD_CYAN
        wrapper_descriptor: builtins.str = ANSIColors.BOLD_CYAN
        method_descriptor: builtins.str = ANSIColors.BOLD_CYAN

        # numbers
        int: builtins.str = ANSIColors.BOLD_YELLOW
        float: builtins.str = ANSIColors.BOLD_YELLOW
        complex: builtins.str = ANSIColors.BOLD_YELLOW
        bool: builtins.str = ANSIColors.BOLD_YELLOW

        # others
        type: builtins.str = ANSIColors.BOLD_MAGENTA
        module: builtins.str = ANSIColors.CYAN
        NoneType: builtins.str = ANSIColors.GREY
        bytes: builtins.str = ANSIColors.BOLD_GREEN
        str: builtins.str = ANSIColors.BOLD_GREEN

    @dataclass(frozen=True, kw_only=True)
    class HttpServer(ThemeSection):
        error: str = ANSIColors.YELLOW
        path: str = ANSIColors.CYAN
        serving: str = ANSIColors.GREEN
        size: str = ANSIColors.GREY
        status_informational: str = ANSIColors.RESET
        status_ok: str = ANSIColors.GREEN
        status_redirect: str = ANSIColors.INTENSE_CYAN
        status_client_error: str = ANSIColors.YELLOW
        status_server_error: str = ANSIColors.RED
        timestamp: str = ANSIColors.GREY
        url: str = ANSIColors.CYAN
        reset: str = ANSIColors.RESET

    @dataclass(frozen=True, kw_only=True)
    class LiveProfiler(ThemeSection):
        """Theme section for the live profiling TUI (Tachyon profiler).

        Colors use CursesColors constants (BLACK, RED, GREEN, YELLOW,
        BLUE, MAGENTA, CYAN, WHITE, DEFAULT).
        """
        # Header colors
        title_fg: int = CursesColors.CYAN
        title_bg: int = CursesColors.DEFAULT

        # Status display colors
        pid_fg: int = CursesColors.CYAN
        uptime_fg: int = CursesColors.GREEN
        time_fg: int = CursesColors.YELLOW
        interval_fg: int = CursesColors.MAGENTA

        # Thread view colors
        thread_all_fg: int = CursesColors.GREEN
        thread_single_fg: int = CursesColors.MAGENTA

        # Progress bar colors
        bar_good_fg: int = CursesColors.GREEN
        bar_bad_fg: int = CursesColors.RED

        # Stats colors
        on_gil_fg: int = CursesColors.GREEN
        off_gil_fg: int = CursesColors.RED
        waiting_gil_fg: int = CursesColors.YELLOW
        gc_fg: int = CursesColors.MAGENTA

        # Function display colors
        func_total_fg: int = CursesColors.CYAN
        func_exec_fg: int = CursesColors.GREEN
        func_stack_fg: int = CursesColors.YELLOW
        func_shown_fg: int = CursesColors.MAGENTA

        # Table header colors (for sorted column highlight)
        sorted_header_fg: int = CursesColors.BLACK
        sorted_header_bg: int = CursesColors.CYAN

        # Normal header colors (non-sorted columns) - use reverse video style
        normal_header_fg: int = CursesColors.BLACK
        normal_header_bg: int = CursesColors.WHITE

        # Data row colors
        samples_fg: int = CursesColors.CYAN
        file_fg: int = CursesColors.GREEN
        func_fg: int = CursesColors.YELLOW

        # Trend indicator colors
        trend_up_fg: int = CursesColors.GREEN
        trend_down_fg: int = CursesColors.RED

        # Medal colors for top functions
        medal_gold_fg: int = CursesColors.RED
        medal_silver_fg: int = CursesColors.YELLOW
        medal_bronze_fg: int = CursesColors.GREEN

        # Background style: 'dark' or 'light'
        background_style: Literal["dark", "light"] = "dark"

    LiveProfilerLight = LiveProfiler(
        # Header colors
        title_fg=CursesColors.BLUE,  # Blue is more readable than cyan on light bg

        # Status display colors - darker colors for light backgrounds
        pid_fg=CursesColors.BLUE,
        uptime_fg=CursesColors.BLACK,
        time_fg=CursesColors.BLACK,
        interval_fg=CursesColors.BLUE,

        # Thread view colors
        thread_all_fg=CursesColors.BLACK,
        thread_single_fg=CursesColors.BLUE,

        # Stats colors
        waiting_gil_fg=CursesColors.RED,
        gc_fg=CursesColors.BLUE,

        # Function display colors
        func_total_fg=CursesColors.BLUE,
        func_exec_fg=CursesColors.BLACK,
        func_stack_fg=CursesColors.BLACK,
        func_shown_fg=CursesColors.BLUE,

        # Table header colors (for sorted column highlight)
        sorted_header_fg=CursesColors.WHITE,
        sorted_header_bg=CursesColors.BLUE,

        # Normal header colors (non-sorted columns)
        normal_header_fg=CursesColors.WHITE,
        normal_header_bg=CursesColors.BLACK,

        # Data row colors - use dark colors readable on white
        samples_fg=CursesColors.BLACK,
        file_fg=CursesColors.BLACK,
        func_fg=CursesColors.BLUE,  # Blue is more readable than magenta on light bg

        # Medal colors for top functions
        medal_silver_fg=CursesColors.BLUE,

        # Background style
        background_style="light",
    )

    @dataclass(frozen=True, kw_only=True)
    class Pickletools(ThemeSection):
        annotation: str = ANSIColors.GREY
        arg_number: str = ANSIColors.YELLOW
        arg_string: str = ANSIColors.GREEN
        mark: str = ANSIColors.GREY
        op_call: str = ANSIColors.GREEN
        op_container: str = ANSIColors.INTENSE_BLUE
        op_memo: str = ANSIColors.MAGENTA
        op_meta: str = ANSIColors.GREY
        op_stack: str = ANSIColors.BOLD_RED
        opcode_code: str = ANSIColors.CYAN
        position: str = ANSIColors.GREY
        proto: str = ANSIColors.YELLOW
        reset: str = ANSIColors.RESET

    @dataclass(frozen=True, kw_only=True)
    class Syntax(ThemeSection):
        prompt: str = ANSIColors.BOLD_MAGENTA
        keyword: str = ANSIColors.BOLD_BLUE
        keyword_constant: str = ANSIColors.BOLD_BLUE
        builtin: str = ANSIColors.CYAN
        comment: str = ANSIColors.RED
        string: str = ANSIColors.GREEN
        number: str = ANSIColors.YELLOW
        op: str = ANSIColors.RESET
        definition: str = ANSIColors.BOLD
        soft_keyword: str = ANSIColors.BOLD_BLUE
        reset: str = ANSIColors.RESET

    @dataclass(frozen=True, kw_only=True)
    class Timeit(ThemeSection):
        timing: str = ANSIColors.CYAN
        best: str = ANSIColors.BOLD_GREEN
        per_loop: str = ANSIColors.GREEN
        punctuation: str = ANSIColors.GREY
        warning: str = ANSIColors.YELLOW
        warning_worst: str = ANSIColors.MAGENTA
        warning_best: str = ANSIColors.GREEN
        reset: str = ANSIColors.RESET

    @dataclass(frozen=True, kw_only=True)
    class Tokenize(ThemeSection):
        whitespace: str = ANSIColors.GREY
        error: str = ANSIColors.BOLD_RED
        position: str = ANSIColors.GREY
        delimiter: str = ANSIColors.RESET

    @dataclass(frozen=True, kw_only=True)
    class Traceback(ThemeSection):
        type: str = ANSIColors.BOLD_MAGENTA
        message: str = ANSIColors.MAGENTA
        note: str = ANSIColors.CYAN
        filename: str = ANSIColors.MAGENTA
        line_no: str = ANSIColors.MAGENTA
        frame: str = ANSIColors.MAGENTA
        error_highlight: str = ANSIColors.BOLD_RED
        error_range: str = ANSIColors.RED
        reset: str = ANSIColors.RESET

    @dataclass(frozen=True, kw_only=True)
    class Unittest(ThemeSection):
        passed: str = ANSIColors.GREEN
        warn: str = ANSIColors.YELLOW
        fail: str = ANSIColors.RED
        fail_info: str = ANSIColors.BOLD_RED
        reset: str = ANSIColors.RESET

    @dataclass(frozen=True, kw_only=True)
    class Theme:
        """A suite of themes for all sections of Python."""
        argparse: Argparse = field(default_factory=Argparse)
        ast: Ast = field(default_factory=Ast)
        difflib: Difflib = field(default_factory=Difflib)
        fancycompleter: FancyCompleter = field(default_factory=FancyCompleter)
        http_server: HttpServer = field(default_factory=HttpServer)
        live_profiler: LiveProfiler = field(default_factory=LiveProfiler)
        pickletools: Pickletools = field(default_factory=Pickletools)
        syntax: Syntax = field(default_factory=Syntax)
        timeit: Timeit = field(default_factory=Timeit)
        tokenize: Tokenize = field(default_factory=Tokenize)
        traceback: Traceback = field(default_factory=Traceback)
        unittest: Unittest = field(default_factory=Unittest)

        def copy_with(self, **sections: ThemeSection) -> Self:
            """Return a new Theme based on this instance with some sections replaced.

            Themes are immutable to protect against accidental modifications that
            could lead to invalid terminal states.
            """
            new = {
                f.name: sections.get(f.name, getattr(self, f.name))
                for f in fields(self)
            }
            return type(self)(**new)  # type: ignore[arg-type]

        @classmethod
        def no_colors(cls) -> Self:
            """Return a new Theme where colors in all sections are empty strings.

            This allows writing user code as if colors are always used. The color
            fields will be ANSI color code strings when colorization is desired
            and possible, and empty strings otherwise.
            """
            new = {
                f.name: f.default_factory.no_colors()  # type: ignore[union-attr]
                for f in fields(cls)
            }
            return cls(**new)

    default_theme = Theme()
    theme_no_color = default_theme.no_colors()
    # Convenience theme with light profiler colors (for white/light terminal backgrounds)
    light_profiler_theme = default_theme.copy_with(live_profiler=LiveProfilerLight)

    local = locals()
    for name in _LAZY_THEME_NAMES:
        value = local[name]
        if isinstance(value, type):
            # Restore the qualname so the class looks module-level rather than
            # nested inside `_build_themes`. Required for pickling (e.g. an
            # `argparse.HelpFormatter` carries a Theme instance in its state).
            value.__qualname__ = name
        g[name] = value
    g["_theme"] = default_theme


def __getattr__(name: str):
    if name in _LAZY_THEME_NAMES:
        try:
            _build_themes()
        except ImportError:
            return _shutdown_theme
        return globals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
        _build_themes()
    except ImportError:
        # Late interpreter shutdown: meta_path has been torn down.  Return a
        # minimal stand-in so traceback formatting from `__del__` keeps working.
        return _shutdown_theme  # type: ignore[return-value]

    g = globals()
    if force_color or (not force_no_color and can_colorize(file=tty_file)):
        return g["_theme"]
    return g["theme_no_color"]


def set_theme(t: Theme) -> None:
    _build_themes()
    if not isinstance(t, globals()["Theme"]):
        raise ValueError(f"Expected Theme object, found {t}")
    globals()["_theme"] = t
