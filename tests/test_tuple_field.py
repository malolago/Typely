import pytest

from typely.fields.integer_field import integer
from typely.fields.string_field import string
from typely.fields.tuple_field import TupleField, uple


def test_tuple_factory_returns_tuple_field() -> None:
    assert isinstance(uple(integer()), TupleField)


def test_tuple_field_accepts_values_matching_each_position() -> None:
    class Model:
        value = uple(integer(), string())

    model = Model()
    model.value = (1, "one")

    assert model.value == (1, "one")


def test_tuple_factory_accepts_fields_as_a_single_sequence() -> None:
    class Model:
        value = uple((integer(), string()))

    model = Model()
    model.value = (1, "one")

    assert model.value == (1, "one")


def test_tuple_field_rejects_non_tuple_values() -> None:
    class Model:
        value = uple(integer(), string())

    with pytest.raises(TypeError):
        Model().value = [1, "one"]


@pytest.mark.parametrize("value", [("one", 1), (True, "one")])
def test_tuple_field_validates_element_types(value: tuple[object, ...]) -> None:
    class Model:
        value = uple(integer(), string())

    with pytest.raises(TypeError):
        Model().value = value


def test_tuple_field_runs_each_element_field_validator() -> None:
    class Model:
        value = uple(integer().positive(), string())

    with pytest.raises(ValueError, match="must be positive"):
        Model().value = (0, "zero")


@pytest.mark.parametrize("value", [(1,), (1, "one", True)])
def test_tuple_field_rejects_wrong_number_of_values(
    value: tuple[object, ...],
) -> None:
    class Model:
        value = uple(integer(), string())

    with pytest.raises((TypeError, ValueError)):
        Model().value = value


def test_tuple_field_runs_validators_for_all_positions() -> None:
    class Model:
        value = uple(integer(), string().regex(r"[a-z]+"))

    with pytest.raises(ValueError, match="must match regex"):
        Model().value = (1, "ONE")
