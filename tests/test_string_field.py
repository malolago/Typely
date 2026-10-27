import uuid

import pytest

from typely import StringField, string


def test_string_factory_returns_string_field() -> None:
    assert isinstance(string(), StringField)


@pytest.mark.parametrize("value", ["", "hello", "123"])
def test_accepts_string_values(value: str) -> None:
    class Model:
        name = string()

    model = Model()
    model.name = value

    assert model.name == value


@pytest.mark.parametrize("value", [1, True, None, b"text"])
def test_rejects_non_string_values(value: object) -> None:
    class Model:
        name = string()

    with pytest.raises(TypeError, match="expects a string"):
        Model().name = value


def test_regex_validator_accepts_matching_value() -> None:
    class Model:
        name = string().regex(r"^[a-z]+$")

    model = Model()
    model.name = "hello"

    assert model.name == "hello"


@pytest.mark.parametrize("value", ["Hello", "hello123", ""])
def test_regex_validator_rejects_non_matching_value(value: str) -> None:
    class Model:
        name = string().regex(r"^[a-z]+$")

    with pytest.raises(ValueError, match="must match regex"):
        Model().name = value


def test_regex_validator_checks_default_declared_before_it() -> None:
    with pytest.raises(ValueError, match="must match regex"):
        string().default("invalid").regex(r"^[0-9]+$")


def test_uuid_validator_accepts_uuid_v4() -> None:
    value = str(uuid.uuid4())

    class Model:
        identifier = string().uuid()

    model = Model()
    model.identifier = value

    assert model.identifier == value


def test_uuid_validator_rejects_invalid() -> None:
    class Model:
        identifier = string().uuid()

    with pytest.raises(ValueError):
        Model().identifier = "not-a-uuid"


def test_uuid_validator_checks_default_declared_before_it() -> None:
    with pytest.raises(ValueError):
        string().default("not-a-uuid").uuid()


@pytest.mark.parametrize("value", ["user@example.com", "first.last+tag@example.co.uk"])
def test_email_validator_accepts_valid_emails(value: str) -> None:
    class Model:
        address = string().email()

    model = Model()
    model.address = value

    assert model.address == value


@pytest.mark.parametrize("value", ["not-an-email", "user@"])
def test_email_validator_rejects_invalid_emails(value: str) -> None:
    class Model:
        address = string().email()

    with pytest.raises(ValueError, match="valid email"):
        Model().address = value


def test_email_validator_checks_default_declared_before_it() -> None:
    with pytest.raises(ValueError, match="valid email"):
        string().default("not-an-email").email()


@pytest.mark.parametrize("value", ["https://example.com", "http://example.com/path"])
def test_url_validator_accepts_valid_urls(value: str) -> None:
    class Model:
        website = string().url()

    model = Model()
    model.website = value

    assert model.website == value


@pytest.mark.parametrize("value", ["not a url", "example.com"])
def test_url_validator_rejects_invalid_urls(value: str) -> None:
    class Model:
        website = string().url()

    with pytest.raises(ValueError, match="valid url"):
        Model().website = value


def test_url_validator_checks_default_declared_before_it() -> None:
    with pytest.raises(ValueError, match="valid url"):
        string().default("not a url").url()


@pytest.mark.parametrize("value", ["example.com", "www.example.co.uk"])
def test_domain_validator_accepts_valid_domains(value: str) -> None:
    class Model:
        hostname = string().domain()

    model = Model()
    model.hostname = value

    assert model.hostname == value


@pytest.mark.parametrize("value", ["not a domain", "https://example.com"])
def test_domain_validator_rejects_invalid_domains(value: str) -> None:
    class Model:
        hostname = string().domain()

    with pytest.raises(ValueError, match="valid domain"):
        Model().hostname = value


def test_domain_validator_checks_default_declared_before_it() -> None:
    with pytest.raises(ValueError, match="valid domain"):
        string().default("not a domain").domain()


def test_min_validator_accepts_length_greater_than_threshold() -> None:
    class Model:
        name = string().min(3)

    model = Model()
    model.name = "Malo"

    assert model.name == "Malo"


@pytest.mark.parametrize("value", ["", "ab"])
def test_min_validator_rejects_length_at_or_below_threshold(value: str) -> None:
    class Model:
        name = string().min(3)

    with pytest.raises(ValueError, match="Length must be inferior to 3"):
        Model().name = value


def test_min_validator_checks_default_declared_before_it() -> None:
    with pytest.raises(ValueError, match="Length must be inferior to 3"):
        string().default("ab").min(3)


def test_max_validator_accepts_length_at_threshold() -> None:
    class Model:
        name = string().max(3)

    model = Model()
    model.name = "abc"

    assert model.name == "abc"


def test_max_validator_rejects_length_above_threshold() -> None:
    class Model:
        name = string().max(3)

    with pytest.raises(ValueError, match="Length must be inferior to 3"):
        Model().name = "abcd"


def test_max_validator_checks_default_declared_before_it() -> None:
    with pytest.raises(ValueError, match="Length must be inferior to 3"):
        string().default("abcd").max(3)


def test_between_validator_accepts_values_within_its_length_range() -> None:
    class Model:
        name = string().between(2, 4)

    model = Model()
    model.name = "abc"

    assert model.name == "abc"


@pytest.mark.parametrize("value", ["a", "abcde"])
def test_between_validator_rejects_values_outside_its_length_range(
    value: str,
) -> None:
    class Model:
        name = string().between(2, 4)

    with pytest.raises(ValueError):
        Model().name = value
