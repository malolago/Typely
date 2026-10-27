from typing import Self, cast

from validators.domain import domain
from validators.email import email
from validators.url import url
from ..field import Field

import re
from validators import uuid


class StringField(Field[str]):
    def _validate(self, value: str) -> None:
        if not isinstance(value, str):
            raise TypeError("This field expects a string.")

        super()._validate(value)

    def regex(self, regex: str) -> Self:
        def check(value: str) -> None:
            if not re.fullmatch(regex, value):
                raise ValueError(f"Value {value} must match regex {regex}.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(str, self._default))

        return self

    def uuid(self) -> Self:
        def check(value: str) -> None:
            if not uuid(value):
                raise ValueError(f"Value {value} must be a valid UUID-v4.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(str, self._default))

        return self

    def email(self) -> Self:
        def check(value: str) -> None:
            if not email(value):
                raise ValueError(f"Value {value} must be a valid email.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(str, self._default))

        return self

    def url(self) -> Self:
        def check(value: str) -> None:
            if not url(value):
                raise ValueError(f"Value {value} must be a valid url.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(str, self._default))

        return self

    def min(self, min: int) -> Self:
        def check(value: str) -> None:
            if len(value) < min:
                raise ValueError(f"Length must be inferior to {min}.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(str, self._default))

        return self

    def max(self, max: int) -> Self:
        def check(value: str) -> None:
            if len(value) > max:
                raise ValueError(f"Length must be inferior to {max}.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(str, self._default))

        return self

    def between(self, min: int, max: int) -> Self:
        return self.min(min).max(max)

    def domain(self) -> Self:
        def check(value: str) -> None:
            if not domain(value):
                raise ValueError(f"Value {value} must be a valid domain.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(str, self._default))

        return self


def string() -> StringField:
    return StringField(type=str)
