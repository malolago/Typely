from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar, cast, overload


class _Required:
    pass


class _Optional:
    pass


T = TypeVar("T")
U = TypeVar("U", default=T)
State = TypeVar("State", _Required, _Optional, default=_Required)
V = TypeVar("V")


_MISSING = object()


class Field(Generic[T, U, State]):
    def __init__(self, type: type[T]) -> None:
        self._type = type
        self._optional = False
        self._default: object = _MISSING
        self._name = ""
        self._validators: list[Callable[[T], None]] = []
        self._transform: Callable[[Any], Any] = lambda x: x

    def default(self, value: T) -> Self:
        self._validate(value)
        self._default = value
        return self

    @overload
    def optional(
        self: "Field[T, U, _Required]",
    ) -> "Field[T, U, _Optional]": ...

    @overload
    def optional(
        self: "Field[T, U, _Optional]",
    ) -> "Field[T, U, _Optional]": ...

    def optional(self) -> Any:
        self._optional = True
        return self

    @overload
    def transform(
        self: "Field[T, U, _Required]",
        fn: Callable[[U], V],
    ) -> "Field[T, V, _Required]": ...

    @overload
    def transform(
        self: "Field[T, U, _Optional]",
        fn: Callable[[U], V],
    ) -> "Field[T, V, _Optional]": ...

    def transform(self, fn: Callable[[Any], Any]) -> Any:
        previous = self._transform
        self._transform = lambda x: fn(previous(x))
        return self

    def _validate(self, value: T) -> None:
        for validator in self._validators:
            validator(value)

    def __set_name__(self, owner: type, name: str) -> None:
        self._name = f"_field_{name}"

    @overload
    def __get__(self, instance: None, owner: type[Any] | None = None) -> Self: ...

    @overload
    def __get__(
        self: "Field[T, U, _Required]",
        instance: object,
        owner: type[Any] | None = None,
    ) -> U: ...

    @overload
    def __get__(
        self: "Field[T, U, _Optional]",
        instance: object,
        owner: type[Any] | None = None,
    ) -> U | None: ...

    def __get__(self, instance: object | None, owner: type[Any] | None = None) -> Any:
        if instance is None:
            return self

        try:
            value = getattr(instance, self._name)
        except AttributeError:
            if self._default is not _MISSING:
                return self._transform(cast(T, self._default))
            if self._optional:
                return None
            raise AttributeError(f"Field '{self._name[7:]}' has no value.") from None

        return self._transform(value)

    def __set__(self, instance: object, value: T) -> None:
        self._validate(value)
        setattr(instance, self._name, value)
