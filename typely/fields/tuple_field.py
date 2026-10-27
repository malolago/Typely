from collections.abc import Callable
from typing import Any, Generic, TypeVar, Self, cast, overload

from ..field import Field, _Optional, _Required

TupleT = TypeVar("TupleT", bound=tuple[Any, ...])
OutputT = TypeVar("OutputT")
NewOutputT = TypeVar("NewOutputT")
TupleState = TypeVar("TupleState", _Required, _Optional)

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")


class TupleField(
    Field[TupleT, OutputT, TupleState],
    Generic[TupleT, OutputT, TupleState],
):
    def __init__(
        self,
        args: tuple[Field[Any, Any, Any], ...],
    ) -> None:
        self._types = args
        super().__init__(type=cast(type[TupleT], tuple))

    def _validate(self, value: TupleT) -> None:
        if not isinstance(value, tuple):
            raise TypeError("This field expects a tuple.")

        if len(value) != len(self._types):
            raise TypeError(f"Expected {len(self._types)} elements, got {len(value)}.")

        for index, (element, field) in enumerate(zip(value, self._types)):
            try:
                field._validate(element)
            except (TypeError, ValueError) as exc:
                raise type(exc)(f"Invalid element at index {index}: {exc}") from exc

        super()._validate(value)

    @overload
    def optional(
        self: "TupleField[TupleT, OutputT, _Required]",
    ) -> "TupleField[TupleT, OutputT, _Optional]": ...

    @overload
    def optional(
        self: "TupleField[TupleT, OutputT, _Optional]",
    ) -> "TupleField[TupleT, OutputT, _Optional]": ...

    def optional(self) -> Any:
        self._optional = True
        return self

    @overload
    def transform(
        self: "TupleField[TupleT, OutputT, _Required]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "TupleField[TupleT, NewOutputT, _Required]": ...

    @overload
    def transform(
        self: "TupleField[TupleT, OutputT, _Optional]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "TupleField[TupleT, NewOutputT, _Optional]": ...

    def transform(
        self,
        fn: Callable[[Any], Any],
    ) -> Any:
        previous = self._transform
        self._transform = lambda value: fn(previous(value))
        return self


# Overloading shenanigans (based on builtin's map .pyi) while waiting for https://github.com/python/typing/issues/548

# Un tuple passé comme argument unique


@overload
def uple(
    types: tuple[Field[T1, Any, Any]], /
) -> TupleField[tuple[T1], tuple[T1], _Required]: ...


@overload
def uple(
    types: tuple[Field[T1, Any, Any], Field[T2, Any, Any]], /
) -> TupleField[tuple[T1, T2], tuple[T1, T2], _Required]: ...


@overload
def uple(
    types: tuple[
        Field[T1, Any, Any],
        Field[T2, Any, Any],
        Field[T3, Any, Any],
    ],
    /,
) -> TupleField[tuple[T1, T2, T3], tuple[T1, T2, T3], _Required]: ...


@overload
def uple(
    types: tuple[
        Field[T1, Any, Any],
        Field[T2, Any, Any],
        Field[T3, Any, Any],
        Field[T4, Any, Any],
    ],
    /,
) -> TupleField[
    tuple[T1, T2, T3, T4],
    tuple[T1, T2, T3, T4],
    _Required,
]: ...


@overload
def uple(
    types: tuple[
        Field[T1, Any, Any],
        Field[T2, Any, Any],
        Field[T3, Any, Any],
        Field[T4, Any, Any],
        Field[T5, Any, Any],
    ],
    /,
) -> TupleField[
    tuple[T1, T2, T3, T4, T5],
    tuple[T1, T2, T3, T4, T5],
    _Required,
]: ...


# Des champs passés comme arguments positionnels


@overload
def uple(
    type1: Field[T1, Any, Any], /
) -> TupleField[tuple[T1], tuple[T1], _Required]: ...


@overload
def uple(
    type1: Field[T1, Any, Any], type2: Field[T2, Any, Any], /
) -> TupleField[tuple[T1, T2], tuple[T1, T2], _Required]: ...


@overload
def uple(
    type1: Field[T1, Any, Any],
    type2: Field[T2, Any, Any],
    type3: Field[T3, Any, Any],
    /,
) -> TupleField[tuple[T1, T2, T3], tuple[T1, T2, T3], _Required]: ...


@overload
def uple(
    type1: Field[T1, Any, Any],
    type2: Field[T2, Any, Any],
    type3: Field[T3, Any, Any],
    type4: Field[T4, Any, Any],
    /,
) -> TupleField[
    tuple[T1, T2, T3, T4],
    tuple[T1, T2, T3, T4],
    _Required,
]: ...


@overload
def uple(
    type1: Field[T1, Any, Any],
    type2: Field[T2, Any, Any],
    type3: Field[T3, Any, Any],
    type4: Field[T4, Any, Any],
    type5: Field[T5, Any, Any],
    /,
) -> TupleField[
    tuple[T1, T2, T3, T4, T5],
    tuple[T1, T2, T3, T4, T5],
    _Required,
]: ...


# Formes génériques de repli


@overload
def uple(
    types: tuple[Field[Any, Any, Any], ...], /
) -> TupleField[tuple[Any, ...], tuple[Any, ...], _Required]: ...


@overload
def uple(
    types: list[Field[Any, Any, Any]], /
) -> TupleField[tuple[Any, ...], tuple[Any, ...], _Required]: ...


@overload
def uple(
    *types: Field[Any, Any, Any],
) -> TupleField[tuple[Any, ...], tuple[Any, ...], _Required]: ...


def uple(*types: Any) -> TupleField[tuple[Any, ...], tuple[Any, ...], _Required]:
    if len(types) == 1 and isinstance(types[0], (tuple, list)):
        types = tuple(types[0])

    return cast(
        TupleField[tuple[Any, ...], tuple[Any, ...], _Required],
        TupleField(args=tuple(types)),
    )
