from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar, cast, overload

from ..field import _MISSING, Field, _Optional, _Required

OutputT = TypeVar("OutputT")
NewOutputT = TypeVar("NewOutputT")
IntState = TypeVar("IntState", _Required, _Optional)


class IntField(
    Field[int, OutputT, IntState],
    Generic[OutputT, IntState],
):
    def _validate(self, value: int) -> None:
        if type(value) is not int:
            raise TypeError("This field expects an integer.")

        super()._validate(value)

    @overload
    def optional(
        self: "IntField[OutputT, _Required]",
    ) -> "IntField[OutputT, _Optional]": ...

    @overload
    def optional(
        self: "IntField[OutputT, _Optional]",
    ) -> "IntField[OutputT, _Optional]": ...

    def optional(self) -> Any:
        self._optional = True
        return self

    @overload
    def transform(
        self: "IntField[OutputT, _Required]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "IntField[NewOutputT, _Required]": ...

    @overload
    def transform(
        self: "IntField[OutputT, _Optional]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "IntField[NewOutputT, _Optional]": ...

    def transform(
        self,
        fn: Callable[[Any], Any],
    ) -> Any:
        previous = self._transform
        self._transform = lambda value: fn(previous(value))
        return self

    def positive(self) -> Self:

        def check(value: int) -> None:
            if value <= 0:
                raise ValueError("Value must be positive.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(int, self._default))

        return self

    def min(self, minimum: int) -> Self:
        def check(value: int) -> None:
            if value < minimum:
                raise ValueError(f"Value must be at least {minimum}.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(int, self._default))

        return self

    def max(self, maximum: int) -> Self:
        def check(value: int) -> None:
            if value > maximum:
                raise ValueError(f"Value must be at most {maximum}.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(int, self._default))

        return self

    def between(self, minimum: int, maximum: int) -> Self:
        return self.min(minimum).max(maximum)


def integer() -> IntField[int, _Required]:
    return cast(
        IntField[int, _Required],
        IntField(type=int),
    )
