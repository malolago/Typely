from typing import Any, Generic, TypeVar, overload

from ..field import Field

TupleT = TypeVar("TupleT", bound=tuple[Any, ...])

T1 = TypeVar("T1")
T2 = TypeVar("T2")
T3 = TypeVar("T3")
T4 = TypeVar("T4")
T5 = TypeVar("T5")


class TupleField(Field[TupleT], Generic[TupleT]):
    def __init__(self, args: tuple[Field[Any], ...]) -> None:
        self._types = args
        super().__init__(type=tuple)

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


# Overloading shenanigans (based on builtin's map .pyi) while waiting for https://github.com/python/typing/issues/548


@overload
def uple(types: tuple[Field[T1]], /) -> TupleField[tuple[T1]]: ...


@overload
def uple(types: tuple[Field[T1], Field[T2]], /) -> TupleField[tuple[T1, T2]]: ...


@overload
def uple(
    types: tuple[Field[T1], Field[T2], Field[T3]], /
) -> TupleField[tuple[T1, T2, T3]]: ...


@overload
def uple(
    types: tuple[Field[T1], Field[T2], Field[T3], Field[T4]], /
) -> TupleField[tuple[T1, T2, T3, T4]]: ...


@overload
def uple(
    types: tuple[Field[T1], Field[T2], Field[T3], Field[T4], Field[T5]],
    /,
) -> TupleField[tuple[T1, T2, T3, T4, T5]]: ...


@overload
def uple(types: tuple[Field[Any], ...], /) -> TupleField[tuple[Any, ...]]: ...


@overload
def uple(types: list[Field[Any]], /) -> TupleField[tuple[Any, ...]]: ...


@overload
def uple(*types: Field[Any]) -> TupleField[tuple[Any, ...]]: ...


def uple(*types: Any) -> TupleField[Any]:
    if len(types) == 1 and isinstance(types[0], (tuple, list)):
        types = tuple(types[0])

    return TupleField(args=types)
