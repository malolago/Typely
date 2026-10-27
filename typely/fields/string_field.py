from typing import Any, Callable, Generic, Self, TypeVar, cast, overload

from validators.domain import domain
from validators.email import email
from validators.url import url
from ..field import Field, _Optional, _Required, _MISSING

import re
from validators import uuid

OutputT = TypeVar("OutputT")
NewOutputT = TypeVar("NewOutputT")
StringState = TypeVar("StringState", _Required, _Optional)


class StringField(Field[str, OutputT, StringState], Generic[OutputT, StringState]):
    def _validate(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("This field expects a string.")

        super()._validate(value)

    @overload
    def optional(
        self: "StringField[OutputT, _Required]",
    ) -> "StringField[OutputT, _Optional]": ...

    @overload
    def optional(
        self: "StringField[OutputT, _Optional]",
    ) -> "StringField[OutputT, _Optional]": ...

    def optional(self) -> Any:
        self._optional = True
        return self

    @overload
    def transform(
        self: "StringField[OutputT, _Required]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "StringField[NewOutputT, _Required]": ...

    @overload
    def transform(
        self: "StringField[OutputT, _Optional]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "StringField[NewOutputT, _Optional]": ...

    def transform(
        self,
        fn: Callable[[Any], Any],
    ) -> Any:
        previous = self._transform
        self._transform = lambda value: fn(previous(value))
        return self

    def regex(self, regex: str) -> Self:
        def check(value: str) -> None:
            if not re.fullmatch(regex, value):
                raise ValueError(f"Value {value} must match regex {regex}.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(str, self._default))

        return self

    def uuid(self) -> Self:
        def check(value: str) -> None:
            if not uuid(value):
                raise ValueError(f"Value {value} must be a valid UUID-v4.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(str, self._default))

        return self

    def email(self) -> Self:
        def check(value: str) -> None:
            if not email(value):
                raise ValueError(f"Value {value} must be a valid email.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(str, self._default))

        return self

    def url(self) -> Self:
        def check(value: str) -> None:
            if not url(value):
                raise ValueError(f"Value {value} must be a valid url.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(str, self._default))

        return self

    def min(self, min: int) -> Self:
        def check(value: str) -> None:
            if len(value) < min:
                raise ValueError(f"Length must be inferior to {min}.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(str, self._default))

        return self

    def max(self, max: int) -> Self:
        def check(value: str) -> None:
            if len(value) > max:
                raise ValueError(f"Length must be inferior to {max}.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(str, self._default))

        return self

    def between(self, min: int, max: int) -> Self:
        return self.min(min).max(max)

    def domain(self) -> Self:
        def check(value: str) -> None:
            if not domain(value):
                raise ValueError(f"Value {value} must be a valid domain.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(str, self._default))

        return self


def string() -> StringField[str, _Required]:
    return cast(StringField[str, _Required], StringField(type=str))
