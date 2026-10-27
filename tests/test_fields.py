import pytest

from typely import Field


def test_field_default_is_returned_when_instance_has_no_value() -> None:
    class Model:
        value = Field[int](int).default(10)

    assert Model().value == 10


def test_optional_field_returns_none_when_instance_has_no_value() -> None:
    class Model:
        value = Field[int](int).optional()

    assert Model().value is None


def test_required_field_without_value_raises_attribute_error() -> None:
    class Model:
        value = Field[int](int)

    with pytest.raises(AttributeError, match="Field 'value' has no value"):
        _ = Model().value


def test_instance_assignment_overrides_default() -> None:
    class Model:
        value = Field[int](int).default(10)

    model = Model()
    model.value = 20

    assert model.value == 20
