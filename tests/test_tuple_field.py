from typing import Any, cast

import pytest

from typely.fields.integer_field import integer
from typely.fields.string_field import string
from typely.fields.tuple_field import TupleField, uple


@pytest.mark.parametrize(
    "field",
    [
        uple(integer()),
        uple(integer(), string()),
        uple(integer(), string(), integer()),
        uple(integer(), string(), integer(), string()),
        uple(integer(), string(), integer(), string(), integer()),
        uple((integer(), string())),
        uple([integer(), string()]),
    ],
)
def test_tuple_factory_returns_tuple_field_for_supported_call_shapes(
    field: TupleField[Any, Any, Any],
) -> None:
    assert isinstance(field, TupleField)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (uple((integer(), string())), (1, "one")),
        (uple([integer(), string()]), (1, "one")),
    ],
)
def test_tuple_factory_accepts_fields_as_a_single_sequence(
    field: TupleField[Any, Any, Any],
    value: tuple[int, str],
) -> None:
    class Model:
        result = field

    model = Model()
    model.result = value

    assert model.result == value


def test_tuple_factory_accepts_an_empty_tuple_of_fields() -> None:
    class Model:
        value = uple(())

    model = Model()
    model.value = ()

    assert model.value == ()


def test_tuple_factory_accepts_no_fields() -> None:
    class Model:
        value = uple()

    model = Model()
    model.value = ()

    assert model.value == ()


def test_tuple_field_accepts_values_matching_each_position() -> None:
    class Model:
        value = uple(integer(), string())

    model = Model()
    model.value = (1, "one")

    assert model.value == (1, "one")


@pytest.mark.parametrize(
    ("field", "value"),
    [
        (uple(integer()), (1,)),
        (uple(integer(), string()), (1, "one")),
        (uple(integer(), string(), integer()), (1, "one", 2)),
        (uple(integer(), string(), integer(), string()), (1, "one", 2, "two")),
        (
            uple(integer(), string(), integer(), string(), integer()),
            (1, "one", 2, "two", 3),
        ),
    ],
)
def test_tuple_field_validates_values_for_each_supported_arity(
    field: TupleField[Any, Any, Any],
    value: tuple[object, ...],
) -> None:
    class Model:
        value = field

    model = Model()
    model.value = value

    assert model.value == value


def test_tuple_field_rejects_non_tuple_values() -> None:
    class Model:
        value = uple(integer(), string())

    with pytest.raises(TypeError, match="expects a tuple"):
        setattr(Model(), "value", [1, "one"])


@pytest.mark.parametrize(
    ("value", "message"),
    [
        (("one", 1), "Invalid element at index 0"),
        ((1, 2), "Invalid element at index 1"),
        ((True, "one"), "Invalid element at index 0"),
        ((1, "one", True), "Expected 2 elements, got 3."),
        ((1, "one", 2, 3), "Expected 2 elements, got 4."),
        ((1, "one", 2, "two", True), "Expected 2 elements, got 5."),
    ],
)
def test_tuple_field_reports_the_position_of_an_invalid_element(
    value: tuple[object, ...],
    message: str,
) -> None:
    class Model:
        value = uple(integer(), string())

    with pytest.raises(TypeError, match=message):
        setattr(Model(), "value", value)


def test_tuple_field_preserves_element_validation_exception_type_and_cause() -> None:
    class Model:
        value = uple(integer().positive(), string())

    with pytest.raises(
        ValueError,
        match=r"Invalid element at index 0: Value must be positive\.",
    ) as exc:
        setattr(Model(), "value", (0, "zero"))

    assert isinstance(exc.value.__cause__, ValueError)
    assert str(exc.value.__cause__) == "Value must be positive."


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ((1,), "Expected 2 elements, got 1"),
        ((1, "one", True), "Expected 2 elements, got 3"),
    ],
)
def test_tuple_field_rejects_too_few_or_too_many_values(
    value: tuple[object, ...],
    message: str,
) -> None:
    class Model:
        value = uple(integer(), string())

    with pytest.raises(TypeError, match=message):
        setattr(Model(), "value", value)


def test_tuple_field_validates_every_element_field() -> None:
    class Model:
        value = uple(integer().positive(), string().regex(r"[a-z]+"))

    model = Model()
    model.value = (1, "one")

    with pytest.raises(ValueError, match="must be positive"):
        model.value = (0, "zero")

    assert model.value == (1, "one")

    with pytest.raises(ValueError, match="must match regex"):
        model.value = (2, "TWO")


def test_tuple_field_runs_its_own_validators_after_element_validation() -> None:
    field = uple(integer(), string())

    def validate_tuple(value: tuple[int, str]) -> None:
        if value[0] >= len(value[1]):
            raise ValueError("Tuple does not satisfy its rule.")

    field._validators.append(validate_tuple)

    class Model:
        value = field

    with pytest.raises(ValueError, match="Tuple does not satisfy its rule"):
        Model().value = (4, "one")

    with pytest.raises(TypeError, match="Invalid element at index 1"):
        setattr(Model(), "value", (1, 2))


def test_tuple_field_accepts_tuple_subclasses() -> None:
    class Pair(tuple[int, str]):
        pass

    class Model:
        value = uple(integer(), string())

    model = Model()
    model.value = Pair((1, "one"))

    assert model.value == (1, "one")


def test_tuple_field_default_is_validated_and_used_when_unset() -> None:
    class Model:
        value = uple(integer(), string()).default((1, "one"))

    assert Model().value == (1, "one")


def test_tuple_field_rejects_invalid_default() -> None:
    with pytest.raises(TypeError, match="Invalid element at index 0"):
        uple(integer(), string()).default(cast(tuple[int, str], ("one", 1)))


def test_tuple_field_optional_returns_none_when_unset() -> None:
    class Model:
        value = uple(integer(), string()).optional()

    model = Model()
    assert model.value is None

    model.value = (1, "one")

    assert model.value == (1, "one")


def test_tuple_field_default_takes_precedence_over_optional() -> None:
    class Model:
        value = uple(integer(), string()).optional().default((1, "one"))

    assert Model().value == (1, "one")


def test_tuple_field_without_default_or_optional_value_raises() -> None:
    class Model:
        value = uple(integer(), string())

    with pytest.raises(AttributeError, match="Field 'value' has no value"):
        Model().value


def test_tuple_field_transformations_compose_and_do_not_change_validation() -> None:
    class Model:
        value = (
            uple(integer(), string())
            .transform(lambda pair: f"{pair[0]}:{pair[1]}")
            .transform(str.upper)
        )

    model = Model()
    model.value = (1, "one")

    assert model.value == "1:ONE"

    with pytest.raises(TypeError, match="Invalid element at index 0"):
        setattr(model, "value", ("one", 1))

    assert model.value == "1:ONE"


def test_tuple_field_transforms_default_on_read() -> None:
    class Model:
        value = (
            uple(integer(), string())
            .default((1, "one"))
            .transform(lambda pair: f"{pair[0]}:{pair[1]}")
        )

    assert Model().value == "1:one"


def test_tuple_field_class_access_returns_the_field_descriptor() -> None:
    class Model:
        value = uple(integer(), string())

    assert isinstance(Model.value, TupleField)
