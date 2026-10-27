from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar, cast, overload

from ..field import Field, _Optional, _Required, _MISSING

T = TypeVar("T")
OutputT = TypeVar("OutputT")
NewOutputT = TypeVar("NewOutputT")
ArrayState = TypeVar("ArrayState", _Required, _Optional)


class ArrayField(
    Field[list[T], OutputT, ArrayState],
    Generic[T, OutputT, ArrayState],
):
    def __init__(self, type: Field[T, Any, Any]) -> None:
        self._elem_type = type
        super().__init__(type=list)

    def _validate(self, value: list[T]) -> None:
        if not isinstance(value, list):
            raise TypeError("This field expects a list.")

        for element in value:
            self._elem_type._validate(element)

        super()._validate(value)

    @overload
    def optional(
        self: "ArrayField[T, OutputT, _Required]",
    ) -> "ArrayField[T, OutputT, _Optional]": ...

    @overload
    def optional(
        self: "ArrayField[T, OutputT, _Optional]",
    ) -> "ArrayField[T, OutputT, _Optional]": ...

    def optional(self) -> Any:
        self._optional = True
        return self

    @overload
    def transform(
        self: "ArrayField[T, OutputT, _Required]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "ArrayField[T, NewOutputT, _Required]": ...

    @overload
    def transform(
        self: "ArrayField[T, OutputT, _Optional]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "ArrayField[T, NewOutputT, _Optional]": ...

    def transform(
        self,
        fn: Callable[[Any], Any],
    ) -> Any:
        previous = self._transform
        self._transform = lambda value: fn(previous(value))
        return self

    def minLength(self, minimum: int) -> Self:
        def check(value: list[T]) -> None:
            if len(value) < minimum:
                raise ValueError(
                    f"List must be of size greater or equal than {minimum}."
                )

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(list[T], self._default))

        return self

    def maxLength(self, maximum: int) -> Self:
        def check(value: list[T]) -> None:
            if len(value) > maximum:
                raise ValueError(f"List must be of size smaller than {maximum}.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(list[T], self._default))

        return self

    def fixedLength(self, length: int) -> Self:
        def check(value: list[T]) -> None:
            if len(value) != length:
                raise ValueError(f"List must be of size {length}.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(list[T], self._default))

        return self

    def distinct(self) -> Self:
        def check(value: list[T]) -> None:
            if len(value) != len(set(value)):
                raise ValueError("List must have distinct elements.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(list[T], self._default))

        return self


def array(type: Field[T, Any, Any]) -> ArrayField[T, list[T], _Required]:
    return cast(
        ArrayField[T, list[T], _Required],
        ArrayField(type),
    )
