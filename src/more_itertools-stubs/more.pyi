from collections import Sequence, defaultdict
from decimal import Decimal
from fractions import Fraction
from typing import (
    Any,
    Optional,
    Union,
    TypeVar,
    Type,
    Generic,
    Iterable,
    Iterator,
    List,
    Tuple,
    Callable,
    Generator,
    ContextManager,
    overload,
)
from typing_extensions import Protocol

_T = TypeVar('_T')
_T_contra = TypeVar('_T_contra', contravariant=True)
_U = TypeVar('_U')
_V = TypeVar('_V')
_KT = TypeVar('_KT')
_VT = TypeVar('_VT')
_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_T3 = TypeVar('_T3')
_T4 = TypeVar('_T4')
_T5 = TypeVar('_T5')

def chunked(iterable: Iterable[_T], n: int) -> Iterator[List[_T]]: ...
@overload
def first(iterable: Iterable[_T]) -> _T: ...
@overload
def first(iterable: Iterable[_T], default: _U) -> Union[_T, _U]: ...
@overload
def last(iterable: Iterable[_T]) -> _T: ...
@overload
def last(iterable: Iterable[_T], default: _U) -> Union[_T, _U]: ...

_P = TypeVar('_P', bound=peekable)

class peekable(Generic[_T]):
    def __init__(self, iterable: Iterable[_T]) -> None: ...
    def __iter__(self: _P) -> _P: ...
    def __bool__(self) -> bool: ...
    @overload
    def peek(self) -> _T: ...
    @overload
    def peek(self, default: _U) -> Union[_T, _U]: ...
    def prepend(self, *items: _T) -> None: ...
    def __next__(self) -> _T: ...
    @overload
    def __getitem__(self, index: int) -> _T: ...
    @overload
    def __getitem__(self, index: slice) -> List[_T]: ...

def collate(
    *iterables: Iterable[_T], key: Callable[[_T], Any] = ..., repeat: bool = ...
) -> Iterator[_T]: ...

_CF = TypeVar('_CF', bound=Callable[..., Generator[Any, Any, Any]])

def consumer(func: _CF) -> _CF: ...
def ilen(iterable: Iterable[Any]) -> int: ...
def iterate(func: Callable[[_T], _T], start: _T) -> Iterator[_T]: ...
def with_iter(context_manager: ContextManager[Iterable[_T]]) -> Iterator[_T]: ...
def one(
    iterable: Iterable[_T],
    too_short: Optional[Exception] = ...,
    too_long: Optional[Exception] = ...,
) -> _T: ...
def distinct_permutations(iterable: Iterable[_T]) -> Iterator[Tuple[_T, ...]]: ...
def intersperse(
    e: _U, iterable: Iterable[_T], n: int = ...
) -> Iterator[Union[_T, _U]]: ...
def unique_to_each(*iterables: Iterable[_T]) -> List[List[_T]]: ...
@overload
def windowed(
    seq: Iterable[_T], n: int, step: int = ...
) -> Iterator[Tuple[Optional[_T], ...]]: ...
@overload
def windowed(
    seq: Iterable[_T], n: int, fillvalue: _U, step: int = ...
) -> Iterator[Tuple[Union[_T, _U], ...]]: ...
def substrings(iterable: Iterable[_T]) -> Iterator[Tuple[_T, ...]]: ...

class bucket(Generic[_KT, _VT]):
    def __init__(
        self,
        iterable: Iterable[_VT],
        key: Callable[[_VT], _KT],
        validator: Optional[Callable[[_VT], bool]] = ...,
    ) -> None: ...
    def __contains__(self, value: _KT) -> bool: ...
    def __getitem__(self, value: _KT) -> Iterator[_VT]: ...

def spy(iterable: Iterable[_T], n: int = ...) -> Tuple[List[_T], Iterator[_T]]: ...
def interleave(*iterables: Iterable[_T]) -> Iterator[_T]: ...
def interleave_longest(*iterables: Iterable[_T]) -> Iterator[_T]: ...
def collapse(
    iterable: Iterable[Any],
    base_type: Optional[Union[Type[Any], Tuple[Type[Any], ...]]] = ...,
    levels: Optional[int] = ...,
) -> Iterator[Any]: ...
@overload
def side_effect(
    func: Callable[[_T], Any],
    iterable: Iterable[_T],
    before: Optional[Callable[[], Any]] = ...,
    after: Optional[Callable[[], Any]] = ...,
) -> Iterator[_T]: ...
@overload
def side_effect(
    func: Callable[[List[_T]], Any],
    iterable: Iterable[_T],
    chunk_size: int,
    before: Optional[Callable[[], Any]] = ...,
    after: Optional[Callable[[], Any]] = ...,
) -> Iterator[_T]: ...
def sliced(seq: Sequence[_T], n: int) -> Iterator[Sequence[_T]]: ...
def split_at(
    iterable: Iterable[_T], pred: Callable[[_T], bool]
) -> Iterator[List[_T]]: ...
def split_before(
    iterable: Iterable[_T], pred: Callable[[_T], bool]
) -> Iterator[List[_T]]: ...
def split_after(
    iterable: Iterable[_T], pred: Callable[[_T], bool]
) -> Iterator[List[_T]]: ...
def split_into(
    iterable: Iterable[_T], sizes: Iterable[Optional[int]]
) -> Iterator[List[_T]]: ...
@overload
def padded(
    iterable: Iterable[_T], n: Optional[int] = ..., next_multiple: bool = ...
) -> Iterator[Optional[_T]]: ...
@overload
def padded(
    iterable: Iterable[_T],
    fillvalue: _U = ...,
    n: Optional[int] = ...,
    next_multiple: bool = ...,
) -> Iterator[Union[_T, _U]]: ...
def distribute(n: int, iterable: Iterable[_T]) -> List[Iterator[_T]]: ...
@overload
def stagger(
    iterable: Iterable[_T], offsets: Tuple[int, ...] = ..., longest: bool = ...
) -> Iterator[Tuple[Optional[_T], ...]]: ...
@overload
def stagger(
    iterable: Iterable[_T],
    offsets: Tuple[int, ...] = ...,
    longest: bool = ...,
    fillvalue: _U = ...,
) -> Iterator[Tuple[Union[_T, _U], ...]]: ...
@overload
def zip_offset(
    *iterables: Iterable[_T], offsets: Tuple[int, ...], longest: bool = ...
) -> Iterator[Tuple[Optional[_T], ...]]: ...
@overload
def zip_offset(
    *iterables: Iterable[_T],
    offsets: Tuple[int, ...],
    longest: bool = ...,
    fillvalue: None = ...,
) -> Iterator[Tuple[Optional[_T], ...]]: ...
@overload
def zip_offset(
    *iterables: Iterable[_T],
    offsets: Tuple[int, ...],
    longest: bool = ...,
    fillvalue: _U = ...,
) -> Iterator[Tuple[Union[_T, _U], ...]]: ...
def sort_together(
    iterables: Iterable[Iterable[_T]],
    key_list: Tuple[int, ...] = ...,
    reverse: bool = ...,
) -> Iterable[Tuple[_T, ...]]: ...
@overload
def unzip(iterable: Iterable[Tuple[_T1]]) -> Tuple[Iterator[_T1]]: ...
@overload
def unzip(
    iterable: Iterable[Tuple[_T1, _T2]]
) -> Tuple[Iterator[_T1], Iterator[_T2]]: ...
@overload
def unzip(
    iterable: Iterable[Tuple[_T1, _T2, _T3]]
) -> Tuple[Iterator[_T1], Iterator[_T2], Iterator[_T3]]: ...
@overload
def unzip(
    iterable: Iterable[Tuple[_T1, _T2, _T3, _T4]]
) -> Tuple[Iterator[_T1], Iterator[_T2], Iterator[_T3], Iterator[_T4]]: ...
@overload
def unzip(
    iterable: Iterable[Tuple[_T1, _T2, _T3, _T4, _T5]]
) -> Tuple[
    Iterator[_T1], Iterator[_T2], Iterator[_T3], Iterator[_T4], Iterator[_T5]
]: ...
@overload
def unzip(iterable: Iterable[Tuple[Any, ...]]) -> Tuple[Iterator[Any], ...]: ...
def divide(n: int, iterable: Iterable[_T]) -> List[Iterator[_T]]: ...
@overload
def always_iterable(
    obj: Iterable[_T],
    base_type: Optional[Union[Type[Any], Tuple[Type[Any], ...]]] = ...,
) -> Iterator[_T]: ...
@overload
def always_iterable(
    obj: _T, base_type: Optional[Union[Type[Any], Tuple[Type[Any], ...]]] = ...
) -> Iterator[_T]: ...
def adjacent(
    predicate: Callable[[_T], bool], iterable: Iterable[_T], distance: int = ...
) -> Iterator[Tuple[bool, _T]]: ...
@overload
def groupby_transform(iterable: Iterable[_T]) -> Iterator[Tuple[_T, Iterator[_T]]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T], keyfunc: Callable[[_T], _U]
) -> Iterator[Tuple[_U, Iterator[_T]]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T], valuefunc: Callable[[_T], _V]
) -> Iterator[Tuple[_T, Iterator[_V]]]: ...
@overload
def groupby_transform(
    iterable: Iterable[_T], keyfunc: Callable[[_T], _U], valuefunc: Callable[[_T], _V]
) -> Iterator[Tuple[_U, Iterator[_V]]]: ...
@overload
def numeric_range(__stop: float) -> Iterator[float]: ...
@overload
def numeric_range(__stop: Decimal) -> Iterator[Decimal]: ...
@overload
def numeric_range(__stop: Fraction) -> Iterator[Fraction]: ...
@overload
def numeric_range(
    __start: Union[float, Fraction],
    __stop: Union[float, Decimal, Fraction],
    __step: float,
) -> Iterator[float]: ...
@overload
def numeric_range(
    __start: float, __stop: Union[float, Decimal, Fraction], __step: Fraction
) -> Iterator[float]: ...
@overload
def numeric_range(
    __start: Fraction, __stop: Union[float, Decimal, Fraction], __step: Fraction
) -> Iterator[Fraction]: ...
@overload
def numeric_range(
    __start: Decimal, __stop: Union[float, Decimal, Fraction], __step: Decimal
) -> Iterator[Decimal]: ...
def count_cycle(
    iterable: Iterable[_T], n: Optional[int] = ...
) -> Iterator[Tuple[int, _T]]: ...

class _LocateFunc(Protocol[_T_contra]):
    def __call__(self, *args: _T_contra) -> bool: ...

@overload
def locate(iterable: Iterable[_T]) -> Iterator[int]: ...
@overload
def locate(iterable: Iterable[_T], pred: Callable[[_T], bool]) -> Iterator[int]: ...
@overload
def locate(
    iterable: Iterable[_T], pred: _LocateFunc[_T], window_size: int
) -> Iterator[int]: ...
def lstrip(iterable: Iterable[_T], pred: Callable[[_T], bool]) -> Iterator[_T]: ...
def rstrip(iterable: Iterable[_T], pred: Callable[[_T], bool]) -> Iterator[_T]: ...
def strip(iterable: Iterable[_T], pred: Callable[[_T], bool]) -> Iterator[_T]: ...
@overload
def islice_extended(iterable: Iterable[_T], stop: Optional[int]) -> Iterator[_T]: ...
@overload
def islice_extended(
    iterable: Iterable[_T],
    start: Optional[int],
    stop: Optional[int],
    step: Optional[int] = ...,
) -> Iterator[_T]: ...
def always_reversible(iterable: Iterable[_T]) -> Iterator[_T]: ...
def consecutive_groups(
    iterable: Iterable[_T], ordering: Callable[[_T], Any] = ...
) -> Iterator[List[_T]]: ...
def difference(
    iterable: Iterable[_T], func: Callable[[_T, _T], _T] = ...
) -> Iterator[_T]: ...

class SequenceView(Sequence[_T]):
    def __init__(self, target: Sequence[_T]) -> None: ...
    @overload
    def __getitem__(self, index: int) -> _T: ...
    @overload
    def __getitem__(self, index: slice) -> Sequence[_T]: ...
    def __len__(self) -> int: ...

_SK = TypeVar('_SK', bound=seekable)

class seekable(Generic[_T]):
    def __init__(self, iterable: Iterable[_T]) -> None: ...
    def __iter__(self: _SK) -> _SK: ...
    def __next__(self) -> _T: ...
    def elements(self) -> SequenceView[_T]: ...
    def seek(self, index: int) -> None: ...

class run_length:
    @staticmethod
    def encode(iterable: Iterable[_T]) -> Iterator[Tuple[_T, int]]: ...
    @staticmethod
    def decode(iterable: Iterable[Tuple[_T, int]]) -> Iterator[_T]: ...

def exactly_n(
    iterable: Iterable[_T], n: int, predicate: Callable[[_T], bool] = ...
) -> bool: ...
def circular_shifts(iterable: Iterable[_T]) -> Iterator[Tuple[_T]]: ...
def make_decorator(
    wrapping_func: Callable[..., _T], result_index: int = ...
) -> Callable[..., Callable[..., Callable[..., _T]]]: ...
@overload
def map_reduce(
    iterable: Iterable[_VT], keyfunc: Callable[[_T], _KT]
) -> defaultdict[_KT, List[_VT]]: ...
@overload
def map_reduce(
    iterable: Iterable[_T], keyfunc: Callable[[_T], _KT], valuefuc: Callable[[_T], _VT]
) -> defaultdict[_KT, List[_VT]]: ...
@overload
def map_reduce(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _KT],
    reducefunc: Callable[[Iterable[_T]], _VT],
) -> defaultdict[_KT, _VT]: ...
@overload
def map_reduce(
    iterable: Iterable[_T],
    keyfunc: Callable[[_T], _KT],
    valuefuc: Callable[[_T], _U],
    reducefunc: Callable[[Iterable[_U]], _VT],
) -> defaultdict[_KT, _VT]: ...
def rlocate(
    iterable: Iterable[Any],
    pred: Callable[..., bool] = ...,
    window_size: Optional[int] = ...,
) -> Iterator[int]: ...
def replace(
    iterable: Iterable[_T],
    pred: Callable[[_T], bool],
    substitutes: Iterable[_U],
    count: Optional[int] = ...,
    window_size: int = ...,
) -> Iterator[Union[_T, _U]]: ...
