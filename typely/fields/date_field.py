from datetime import date as Date, datetime
from typing import Any, Callable, Generic, TypeVar, Self, Literal, Self, cast, overload

from ..field import Field, _Optional, _Required, _MISSING

DateFormat = Literal["iso8601", "strptime"]

OutputT = TypeVar("OutputT")
NewOutputT = TypeVar("NewOutputT")
DateState = TypeVar("DateState", _Required, _Optional)


class DateField(Field[Date, OutputT, DateState], Generic[OutputT, DateState]):
    def __init__(
        self,
        format: DateFormat = "iso8601",
        strp: str | None = None,
    ) -> None:
        self._format_type: DateFormat = "iso8601"
        self._strptime_format: str | None = None

        super().__init__(type=Date)

        self.format(format, strp)

    def _parse(self, value: str) -> Date:
        try:
            if self._format_type == "iso8601":
                return Date.fromisoformat(value)

            return datetime.strptime(
                value,
                cast(str, self._strptime_format),
            ).date()

        except ValueError as exc:
            expected = (
                "ISO 8601"
                if self._format_type == "iso8601"
                else f"strptime ({self._strptime_format})"
            )

            raise ValueError(
                f"Value {value!r} must match date format {expected}."
            ) from exc

    def _as_date(self, value: Date | str) -> Date:
        """Convertit une entrée en datetime.date."""
        if isinstance(value, datetime):
            return value.date()

        if isinstance(value, Date):
            return value

        if isinstance(value, str):
            return self._parse(value)

        raise TypeError("Date values must be date objects or strings.")

    def _validate(self, value: Date | str) -> None:
        normalized = self._as_date(value)
        super()._validate(normalized)

    @overload
    def optional(
        self: "DateField[OutputT, _Required]",
    ) -> "DateField[OutputT, _Optional]": ...

    @overload
    def optional(
        self: "DateField[OutputT, _Optional]",
    ) -> "DateField[OutputT, _Optional]": ...

    def optional(self) -> Any:
        self._optional = True
        return self

    @overload
    def transform(
        self: "DateField[OutputT, _Required]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "DateField[NewOutputT, _Required]": ...

    @overload
    def transform(
        self: "DateField[OutputT, _Optional]",
        fn: Callable[[OutputT], NewOutputT],
    ) -> "DateField[NewOutputT, _Optional]": ...

    def transform(
        self,
        fn: Callable[[Any], Any],
    ) -> Any:
        previous = self._transform
        self._transform = lambda value: fn(previous(value))
        return self

    def __set__(self, instance: object, value: Date | str) -> None:
        normalized = self._as_date(value)
        self._validate(normalized)
        setattr(instance, self._name, normalized)

    def default(self, value: Date | str) -> Self:
        return super().default(self._as_date(value))

    def format(
        self,
        format_type: DateFormat = "iso8601",
        fmt: str | None = None,
    ) -> Self:
        if format_type == "iso8601":
            if fmt is not None:
                raise ValueError("ISO 8601 does not require a custom format.")

            self._format_type = "iso8601"
            self._strptime_format = None

        elif format_type == "strptime":
            if not fmt:
                raise ValueError("A format is required when using strptime.")

            self._format_type = "strptime"
            self._strptime_format = fmt

        else:
            raise ValueError(f"Unsupported date format: {format_type!r}.")

        if self._default is not _MISSING:
            self._validate(cast(Date | str, self._default))

        return self

    def min(self, min: Date | str) -> Self:
        min_date = self._as_date(min)

        def check(value: Date) -> None:
            if value < min_date:
                raise ValueError(f"Date must be on or after {min_date.isoformat()}.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(Date | str, self._default))

        return self

    def max(self, max: Date | str) -> Self:
        max_date = self._as_date(max)

        def check(value: Date) -> None:
            if value > max_date:
                raise ValueError(f"Date must be on or before {max_date.isoformat()}.")

        self._validators.append(check)

        if self._default is not _MISSING:
            self._validate(cast(Date | str, self._default))

        return self

    def between(
        self,
        min: Date | str,
        max: Date | str,
    ) -> Self:
        min_date = self._as_date(min)
        max_date = self._as_date(max)

        if min_date > max_date:
            raise ValueError("The minimum date cannot be after the maximum date.")

        return self.min(min_date).max(max_date)


@overload
def date(
    format: Literal["iso8601"] = "iso8601",
    strp: None = None,
) -> DateField[Date, _Required]: ...


@overload
def date(
    format: Literal["strptime"],
    strp: str,
) -> DateField[Date, _Required]: ...


def date(
    format: DateFormat = "iso8601",
    strp: str | None = None,
) -> DateField[Date, _Required]:
    return cast(DateField[Date, _Required], DateField(format, strp))
    return DateField(format, strp)
