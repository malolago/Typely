from datetime import date as Date
from typing import assert_type

from typely import BaseModel, array, date, integer, string, uple


class Contact(BaseModel):
    email = string()
    age = integer()
    registered_on = date()
    scores = array(integer())
    result = uple(integer(), string())
    nickname = string().optional()
    display_name = string().transform(str.title)
    score_label = integer().transform(str)
    optional_note = string().optional().transform(str.upper)


class Admin(Contact):
    level = integer()


def check_basemodel_instance_attribute_inference() -> None:
    contact = Contact()

    assert_type(contact.email, str)
    assert_type(contact.age, int)
    assert_type(contact.registered_on, Date)
    assert_type(contact.scores, list[int])
    assert_type(contact.scores[0], int)
    assert_type(contact.result, tuple[int, str])
    assert_type(contact.result[0], int)
    assert_type(contact.result[1], str)
    assert_type(contact.nickname, str | None)
    assert_type(contact.display_name, str)
    assert_type(contact.score_label, str)
    assert_type(contact.optional_note, str | None)

    admin = Admin()
    assert_type(admin.email, str)
    assert_type(admin.level, int)


class Address(BaseModel):
    city = string()


class UserWithAddress(BaseModel):
    address: Address


def check_nested_basemodel_attribute_inference() -> None:
    user = UserWithAddress()
    assert_type(user.address, Address)
    assert_type(user.address.city, str)
