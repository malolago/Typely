import pytest

from typely import BaseModel, array, date, integer, string, uple


class User(BaseModel):
    name = string().default("Guest")
    age = integer().min(0)


class Admin(User):
    level = integer().positive().default(1)


class Address(BaseModel):
    city = string().optional()

    user: User


class Event(BaseModel):
    day = date()
    scores = array(integer().min(0))
    result = uple(integer(), string())


def test_constructor_assigns_values_and_uses_defaults() -> None:
    user = User(age=25)

    assert user.name == "Guest"
    assert user.age == 25


def test_constructor_destructuring() -> None:
    kwargs = {"age": 25}
    user = User(**kwargs)

    assert user.name == "Guest"
    assert user.age == 25


def test_constructor_validates_values() -> None:
    with pytest.raises(ValueError, match="at least 0"):
        User(age=-1)


def test_constructor_rejects_unknown_fields() -> None:
    with pytest.raises(TypeError, match="Unknown fields: extra"):
        User(age=25, extra=True)


def test_constructor_rejects_multiple_unknown_fields_in_sorted_order() -> None:
    with pytest.raises(TypeError, match="Unknown fields: alpha, zeta"):
        User(age=25, zeta=1, alpha=2)


def test_subclass_inherits_fields_and_adds_its_own() -> None:
    admin = Admin(age=30)

    assert admin.name == "Guest"
    assert admin.age == 30
    assert admin.level == 1


def test_assignment_after_initialization_is_validated() -> None:
    user = User(age=25)

    with pytest.raises(ValueError, match="at least 0"):
        user.age = -1

    assert user.age == 25


def test_constructor_accepts_annotated_nested_model() -> None:
    user = User(age=30)

    address = Address(user=user)

    assert address.user is user


def test_constructor_assigns_nested_date_array_and_tuple_fields() -> None:
    event = Event(
        day="2026-10-26",
        scores=[10, 20],
        result=(1, "first"),
    )

    assert event.day.isoformat() == "2026-10-26"
    assert event.scores == [10, 20]
    assert event.result == (1, "first")


@pytest.mark.parametrize(
    ("field", "value", "error"),
    [
        ("day", "not-a-date", ValueError),
        ("scores", [1, -1], ValueError),
        ("scores", (1, 2), TypeError),
        ("result", (1,), TypeError),
        ("result", (True, "first"), TypeError),
    ],
)
def test_constructor_validates_new_field_types(
    field: str,
    value: object,
    error: type[Exception],
) -> None:
    with pytest.raises(error):
        Event(**{field: value})


def test_nested_model_default_can_be_overridden_in_constructor() -> None:
    class UserWithAddress(BaseModel):
        age = integer()
        address = Address(city="Paris")

    replacement = Address(city="Lyon")
    user = UserWithAddress(age=25, address=replacement)

    assert user.address is replacement
    assert user.address.city == "Lyon"


def test_nested_model_default_is_used_when_not_overridden() -> None:
    class UserWithAddress(BaseModel):
        age = integer()
        address = Address(city="Paris")

    user = UserWithAddress(age=25)

    assert isinstance(user.address, Address)
    assert user.address.city == "Paris"
