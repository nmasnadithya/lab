from typing import Union, List, Tuple, Optional, Iterable, Sized, Dict, overload

import numpy as np

from .artifacts import Artifact
from .colors import StyleCode
from .indicators import Indicator
from .internal import LoggerInternal as _LoggerInternal

_internal: Optional[_LoggerInternal] = None


def internal() -> _LoggerInternal:
    global _internal
    if _internal is None:
        _internal = _LoggerInternal()

    return _internal


@overload
def log(message: str, *, is_new_line=True):
    ...


@overload
def log(message: str, color: StyleCode,
        *,
        is_new_line=True):
    ...

@overload
def log(message: str, colors: List[StyleCode],
        *,
        is_new_line=True):
    ...

@overload
def log(messages: List[Union[str, Tuple[str, StyleCode]]],
        *,
        is_new_line=True):
    ...


def log(message: Union[str, List[Union[str, Tuple[str, StyleCode]]]],
        color: List[StyleCode] or StyleCode or None = None,
        *,
        is_new_line=True):
    r"""
    This has multiple overloads

    .. function:: log(message: str, *, is_new_line=True)
        :noindex:

    .. function:: log(message: str, color: StyleCode, *, is_new_line=True)
        :noindex:

    .. function:: log(message: str, colors: List[StyleCode], *, is_new_line=True)
        :noindex:

    .. function:: log(messages: List[Union[str, Tuple[str, StyleCode]]], *, is_new_line=True)
        :noindex:

    Arguments:
        message (str): string to be printed
        color (StyleCode): color/style of the message
        colors (List[StyleCode]): list of colors/styles for the message
        messages (List[Union[str, Tuple[str, StyleCode]]]): a list of messages.
            Each element should be either a string or a tuple of string and styles.

    Keyword Arguments:
        is_new_line (bool): whether to print a new line at the end

    Example::
        >>> logger.log("test")
    """
    if type(message) == str:
        internal().log([(message, color)], is_new_line=is_new_line)
    elif type(message) == list:
        internal().log(message, is_new_line=is_new_line)


def add_indicator(indicator: Indicator):
    r"""
    Arguments:
        indicator (Indicator): indicator

    """

    internal().add_indicator(indicator)


def add_artifact(artifact: Artifact):
    r"""
    Arguments:
        artifact (Artifact): artifact

    """
    internal().add_artifact(artifact)


@overload
def store(values: Dict[str, any]):
    ...


@overload
def store(name: str, value: any):
    ...


@overload
def store(**kwargs: any):
    ...


def store(*args, **kwargs):
    internal().store(*args, **kwargs)


@overload
def write():
    ...


@overload
def write(global_step: int):
    ...


@overload
def write(values: Dict[str, any]):
    ...


@overload
def write(name: str, value: any):
    ...


@overload
def write(**kwargs: any):
    ...


@overload
def write(global_step: int, values: Dict[str, any]):
    ...


@overload
def write(global_step: int, name: str, value: any):
    ...


@overload
def write(global_step: int, **kwargs: any):
    ...


def write(*args, **kwargs):
    if len(args) > 0 and type(args[0]) == int:
        set_global_step(args[0])
        args = args[1:]

    if len(args) > 0 or len(kwargs.keys()) > 0:
        store(*args, **kwargs)

    internal().write()


def new_line():
    internal().new_line()


def set_global_step(global_step: Optional[int]):
    internal().set_global_step(global_step)


def add_global_step(increment_global_step: int = 1):
    internal().add_global_step(int(increment_global_step))


def get_global_step() -> int:
    return internal().global_step


def iterate(name, iterable: Union[Iterable, Sized, int],
            total_steps: Optional[int] = None, *,
            is_silent: bool = False,
            is_timed: bool = True):
    return internal().iterate(name, iterable, total_steps, is_silent=is_silent,
                              is_timed=is_timed)


def enum(name, iterable: Sized, *,
         is_silent: bool = False,
         is_timed: bool = True):
    return internal().enum(name, iterable, is_silent=is_silent, is_timed=is_timed)


def section(name, *,
            is_silent: bool = False,
            is_timed: bool = True,
            is_partial: bool = False,
            is_new_line: bool = True,
            total_steps: float = 1.0):
    return internal().section(name, is_silent=is_silent,
                              is_timed=is_timed,
                              is_partial=is_partial,
                              total_steps=total_steps,
                              is_new_line=is_new_line)


def progress(steps: float):
    internal().progress(steps)


def set_successful(is_successful=True):
    internal().set_successful(is_successful)


@overload
def loop(iterator_: int, *,
         is_print_iteration_time=True):
    ...


@overload
def loop(iterator_: range, *,
         is_print_iteration_time=True):
    ...


def loop(iterator_: Union[range, int], *,
         is_print_iteration_time=True):
    if type(iterator_) == int:
        return internal().loop(range(iterator_), is_print_iteration_time=is_print_iteration_time)
    else:
        return internal().loop(iterator_, is_print_iteration_time=is_print_iteration_time)


def finish_loop():
    internal().finish_loop()


def save_checkpoint():
    internal().save_checkpoint()


@overload
def info(items: Dict):
    ...


@overload
def info(items: List):
    ...


@overload
def info(*items: any):
    ...


@overload
def info(**items: any):
    ...


def info(*args, **kwargs):
    """
    🎨 Pretty prints a set of values.
    """

    internal().info(*args, **kwargs)


def get_data_path():
    return internal().get_data_path()


def save_numpy(name: str, array: np.ndarray):
    """
    Save a single numpy array.
    This is used to save processed data
    """
    internal().save_numpy(name, array)
