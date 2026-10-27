from typing import Type, TypeVar
from typing import Self, cast

from typely.fields.integer_field import integer

from ..field import Field

T = TypeVar("T")


class ArrayField(Field[list[T]]):
    def __init__(self, type: Field[T]) -> None:
        self._elem_type = type
        super().__init__(type=list)

    def _validate(self, value: list[T]) -> None:
        if not isinstance(value, list):
            raise TypeError("This field expects a list.")
        for element in value:
            self._elem_type._validate(element)

        return super()._validate(value)

    def minLength(self, minimum: int) -> Self:
        def check(value: list[T]) -> None:
            if len(value) < minimum:
                raise ValueError(
                    f"List must be of size greater or equal than {minimum}."
                )

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(list, self._default))

        return self

    def maxLength(self, maximum: int) -> Self:
        def check(value: list[T]) -> None:
            if len(value) > maximum:
                raise ValueError(f"List must be of size smaller than {maximum}.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(list, self._default))

        return self

    def fixedLength(self, length: int) -> Self:
        def check(value: list[T]) -> None:
            if len(value) != length:
                raise ValueError(f"List must be of size {length}.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(list, self._default))

        return self

    def distinct(self) -> Self:
        def check(value: list[T]) -> None:
            if len(value) != len(set(value)):
                raise ValueError(f"List must have distinct elements.")

        self._validators.append(check)

        if self._default is not None:
            self._validate(cast(list, self._default))

        return self


def array(type: Field[T]):
    return ArrayField(type)
