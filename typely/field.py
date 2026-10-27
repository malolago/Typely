from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar, overload

T = TypeVar("T")


class Field(Generic[T]):
    def __init__(self, type: Any) -> None:
        self._type = type
        self._optional = False
        self._default: T | None = None
        self._name = ""
        self._validators: list[Callable[[T], None]] = []
        self._transform: Callable[[T], Any] = lambda x: x

    def default(self, value: T) -> Self:
        self._validate(value)
        self._default = value
        return self

    def optional(self) -> Self:
        self._optional = True
        return self

    def transform(self, fn: Callable[[T], Any]) -> Self:
        self._transform = fn
        return self

    def _validate(self, value: T) -> None:
        for validator in self._validators:
            validator(value)

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = f"_field_{name}"

    @overload
    def __get__(self, instance: None, owner: type[Any] | None = None) -> Self: ...

    @overload
    def __get__(self, instance: object, owner: type[Any] | None = None) -> T: ...

    def __get__(self, instance: object | None, owner: type[Any] | None = None) -> Any:
        if instance is None:
            return self

        try:
            return self._transform(getattr(instance, self._name))
        except AttributeError:
            if self._default is not None:
                return self._transform(self._default)
            if self._optional:
                return None
            raise AttributeError(f"Field '{self._name[7:]}' has no value.") from None

    def __set__(self, instance: object, value: T) -> None:
        self._validate(value)
        setattr(instance, self._name, value)
