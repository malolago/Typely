import pytest

from typely.fields.integer_field import integer
from typely.fields.list_field import array


def test_array_accepts_list_of_values_matching_element_field() -> None:
    class Model:
        values = array(integer())

    model = Model()
    model.values = [1, 2, 3]

    assert model.values == [1, 2, 3]


def test_array_rejects_non_list_values() -> None:
    class Model:
        values = array(integer())

    with pytest.raises(TypeError, match="expects a list"):
        Model().values = (1, 2, 3)


def test_array_validates_each_element_type() -> None:
    class Model:
        values = array(integer())

    with pytest.raises(TypeError):
        Model().values = [1, "two"]


def test_array_applies_element_field_validators() -> None:
    class Model:
        values = array(integer().positive())

    with pytest.raises(ValueError, match="must be positive"):
        Model().values = [1, 0, 3]


def test_min_length_accepts_list_at_the_minimum() -> None:
    class Model:
        values = array(integer()).minLength(2)

    model = Model()
    model.values = [1, 2]

    assert model.values == [1, 2]


def test_min_length_rejects_list_below_the_minimum() -> None:
    class Model:
        values = array(integer()).minLength(2)

    with pytest.raises(ValueError):
        Model().values = [1]


def test_max_length_accepts_list_at_the_maximum() -> None:
    class Model:
        values = array(integer()).maxLength(2)

    model = Model()
    model.values = [1, 2]

    assert model.values == [1, 2]


def test_max_length_rejects_list_above_the_maximum() -> None:
    class Model:
        values = array(integer()).maxLength(2)

    with pytest.raises(ValueError):
        Model().values = [1, 2, 3]


def test_fixed_length_accepts_list_of_exact_length() -> None:
    class Model:
        values = array(integer()).fixedLength(2)

    model = Model()
    model.values = [1, 2]

    assert model.values == [1, 2]


@pytest.mark.parametrize("value", [[], [1], [1, 2, 3]])
def test_fixed_length_rejects_list_of_different_length(
    value: list[int],
) -> None:
    class Model:
        values = array(integer()).fixedLength(2)

    with pytest.raises(ValueError):
        Model().values = value


def test_distinct_accepts_list_without_duplicate_elements() -> None:
    class Model:
        values = array(integer()).distinct()

    model = Model()
    model.values = [1, 2, 3]

    assert model.values == [1, 2, 3]


def test_distinct_rejects_list_with_duplicate_elements() -> None:
    class Model:
        values = array(integer()).distinct()

    with pytest.raises(ValueError, match="distinct elements"):
        Model().values = [1, 2, 1]


def test_length_validator_checks_default_declared_before_it() -> None:
    with pytest.raises(ValueError):
        array(integer()).default([1]).minLength(2)
