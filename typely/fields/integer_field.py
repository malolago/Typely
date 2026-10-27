from typing import Self, cast

from ..field import Field


class IntField(Field[int]):
    def _validate(self, value: int) -> None:
        if type(value) is not int:
            raise TypeError("This field expects an integer.")

        super()._validate(value)

    def positive(self) -> Self:

        def check(value: int) -> None:
            if value <= 0:
                raise ValueError("Value must be positive.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(int, self._default))

        return self

    def min(self, minimum: int) -> Self:
        def check(value: int) -> None:
            if value < minimum:
                raise ValueError(f"Value must be at least {minimum}.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(int, self._default))

        return self

    def max(self, maximum: int) -> Self:
        def check(value: int) -> None:
            if value > maximum:
                raise ValueError(f"Value must be at most {maximum}.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(int, self._default))

        return self

    def between(self, minimum: int, maximum: int) -> Self:
        return self.min(minimum).max(maximum)


def integer() -> IntField:
    return IntField(type=int)
