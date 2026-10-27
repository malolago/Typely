from datetime import date as Date, datetime

import pytest

from typely.fields.date_field import DateField, date


def test_date_factory_returns_date_field() -> None:
    assert isinstance(date(), DateField)


def test_iso8601_date_string_is_stored_as_date() -> None:
    class Model:
        birthday = date()

    model = Model()
    model.birthday = "2026-10-26"

    assert model.birthday == Date(2026, 10, 26)
    assert isinstance(model.birthday, Date)


def test_date_field_accepts_date_object() -> None:
    class Model:
        birthday = date()

    value = Date(2026, 10, 26)
    model = Model()
    model.birthday = value

    assert model.birthday == value


def test_date_field_normalizes_datetime_to_date() -> None:
    class Model:
        birthday = date()

    model = Model()
    model.birthday = datetime(2026, 10, 26, 14, 30)

    assert model.birthday == Date(2026, 10, 26)
    assert type(model.birthday) is Date


@pytest.mark.parametrize("value", [None, 42, True, object()])
def test_date_field_rejects_values_that_are_not_dates_or_strings(
    value: object,
) -> None:
    class Model:
        birthday = date()

    with pytest.raises(TypeError, match="date objects or strings"):
        Model().birthday = value


@pytest.mark.parametrize("value", ["not-a-date", "2026-02-30"])
def test_iso8601_parser_rejects_invalid_date_strings(value: str) -> None:
    class Model:
        birthday = date()

    with pytest.raises(ValueError, match="must match date format ISO 8601"):
        Model().birthday = value


def test_strptime_format_parses_date_string() -> None:
    class Model:
        birthday = date(format="strptime", strp="%d/%m/%Y")

    model = Model()
    model.birthday = "26/10/2026"

    assert model.birthday == Date(2026, 10, 26)


def test_strptime_parser_rejects_string_that_does_not_match_format() -> None:
    class Model:
        birthday = date(format="strptime", strp="%d/%m/%Y")

    with pytest.raises(
        ValueError,
        match=r"must match date format strptime \(%d/%m/%Y\)",
    ):
        Model().birthday = "2026-10-26"


def test_strptime_format_requires_a_format_string() -> None:
    with pytest.raises(ValueError, match="format is required"):
        date(format="strptime", strp=None)


def test_iso8601_format_rejects_custom_format_string() -> None:
    with pytest.raises(ValueError, match="does not require a custom format"):
        date(format="iso8601", strp="%Y-%m-%d")


def test_date_field_parses_string_default() -> None:
    class Model:
        birthday = date().default("2026-10-26")

    assert Model().birthday == Date(2026, 10, 26)
    assert type(Model().birthday) is Date


def test_date_field_normalizes_datetime_default() -> None:
    class Model:
        birthday = date().default(datetime(2026, 10, 26, 14, 30))

    assert Model().birthday == Date(2026, 10, 26)
    assert type(Model().birthday) is Date


def test_default_string_uses_configured_strptime_format() -> None:
    class Model:
        birthday = date(format="strptime", strp="%d/%m/%Y").default("26/10/2026")

    assert Model().birthday == Date(2026, 10, 26)


def test_min_accepts_boundary_and_later_dates() -> None:
    class Model:
        day = date().min("2026-10-26")

    model = Model()
    model.day = "2026-10-26"
    assert model.day == Date(2026, 10, 26)

    model.day = "2026-10-27"
    assert model.day == Date(2026, 10, 27)


def test_min_rejects_dates_before_boundary() -> None:
    class Model:
        day = date().min("2026-10-26")

    with pytest.raises(ValueError, match="on or after 2026-10-26"):
        Model().day = "2026-10-25"


def test_max_accepts_boundary_and_earlier_dates() -> None:
    class Model:
        day = date().max("2026-10-26")

    model = Model()
    model.day = "2026-10-26"
    assert model.day == Date(2026, 10, 26)

    model.day = "2026-10-25"
    assert model.day == Date(2026, 10, 25)


def test_max_rejects_dates_after_boundary() -> None:
    class Model:
        day = date().max("2026-10-26")

    with pytest.raises(ValueError, match="on or before 2026-10-26"):
        Model().day = "2026-10-27"


@pytest.mark.parametrize("value", ["2026-10-26", "2026-10-27"])
def test_between_accepts_inclusive_boundaries_and_dates_inside_range(
    value: str,
) -> None:
    class Model:
        day = date().between("2026-10-26", "2026-10-27")

    model = Model()
    model.day = value

    assert model.day == Date.fromisoformat(value)


@pytest.mark.parametrize("value", ["2026-10-25", "2026-10-28"])
def test_between_rejects_dates_outside_range(value: str) -> None:
    class Model:
        day = date().between("2026-10-26", "2026-10-27")

    with pytest.raises(ValueError):
        Model().day = value


def test_between_rejects_minimum_after_maximum() -> None:
    with pytest.raises(ValueError, match="minimum date cannot be after"):
        date().between("2026-10-28", "2026-10-26")


def test_min_validator_checks_existing_default() -> None:
    with pytest.raises(ValueError, match="on or after 2026-10-27"):
        date().default("2026-10-26").min("2026-10-27")


def test_failed_assignment_does_not_replace_previous_value() -> None:
    class Model:
        day = date().min("2026-10-26")

    model = Model()
    model.day = "2026-10-26"

    with pytest.raises(ValueError):
        model.day = "2026-10-25"

    assert model.day == Date(2026, 10, 26)
