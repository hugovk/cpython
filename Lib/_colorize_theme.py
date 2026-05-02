"""Theming infrastructure for `_colorize`."""

import builtins

from collections.abc import Mapping
from dataclasses import dataclass, field, fields

from _colorize import ANSIColors


# types
if False:
    from collections.abc import Callable, Iterator
    from dataclasses import Field
    from typing import IO, Literal, Self, ClassVar

    _theme: Theme


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
        super().__setattr__('_name_to_value', name_to_value.__getitem__)

    def copy_with(self, **kwargs: str) -> Self:
        color_state: dict[str, str] = {}
        for color_name in self.__dataclass_fields__:
            color_state[color_name] = getattr(self, color_name)
        color_state.update(kwargs)
        return type(self)(**color_state)

    @classmethod
    def no_colors(cls) -> Self:
        color_state: dict[str, str] = {}
        for color_name in cls.__dataclass_fields__:
            color_state[color_name] = ""
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
    """A suite of themes for all sections of Python.

    When adding a new one, remember to also modify `copy_with` and `no_colors`
    below.
    """

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
        return type(self)(**new)

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
    from _colorize import can_colorize

    if force_color or (not force_no_color and can_colorize(file=tty_file)):
        return _theme
    return theme_no_color


def set_theme(t: Theme) -> None:
    global _theme

    if not isinstance(t, Theme):
        raise ValueError(f"Expected Theme object, found {t}")

    _theme = t


set_theme(default_theme)
