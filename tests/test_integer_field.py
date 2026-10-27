import pytest

from typely import IntField, integer


def test_integer_factory_returns_int_field() -> None:
    assert isinstance(integer(), IntField)


@pytest.mark.parametrize("value", [0, 10, -10])
def test_accepts_integer_values(value: int) -> None:
    class Model:
        number = integer()

    model = Model()
    model.number = value

    assert model.number == value


@pytest.mark.parametrize("value", [True, False, 1.0, "1", None])
def test_rejects_non_integer_values(value: object) -> None:
    class Model:
        number = integer()

    with pytest.raises(TypeError, match="expects an integer"):
        Model().number = value


def test_positive_validator_accepts_positive_values() -> None:
    class Model:
        number = integer().positive()

    model = Model()
    model.number = 1

    assert model.number == 1


def test_positive_validator_rejects_zero_and_negative_values() -> None:
    class Model:
        number = integer().positive()

    for value in (0, -1):
        with pytest.raises(ValueError, match="must be positive"):
            Model().number = value


def test_min_and_max_validators_accept_boundaries() -> None:
    class Model:
        number = integer().min(1).max(5)

    model = Model()
    model.number = 1
    assert model.number == 1
    model.number = 5
    assert model.number == 5


@pytest.mark.parametrize(
    ("value", "message"),
    [(-1, "at least 0"), (11, "at most 10")],
)
def test_min_and_max_validators_reject_out_of_range_values(
    value: int, message: str
) -> None:
    class Model:
        number = integer().min(0).max(10)

    with pytest.raises(ValueError, match=message):
        Model().number = value


def test_default_is_checked_against_validators_added_afterward() -> None:
    with pytest.raises(ValueError, match="must be positive"):
        integer().default(0).positive()


def test_validated_default_is_returned() -> None:
    class Model:
        number = integer().positive().default(3)

    assert Model().number == 3
