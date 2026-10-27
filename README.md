# Typely

**Keep your data tidy, your models readable, and your types with you every step of the way.**

Typely is a lightweight validation library for Python models. Declare fields
right where you use them, chain the rules that matter, and get clear feedback
when a value does not fit. No separate schemas or decorator-heavy setup—just
Python classes, readable declarations, and validation that follows your data.

## Why Typely?

- **Declarative models** — define fields once and use them as regular attributes.
- **Immediate validation** — invalid values are rejected during assignment,
  including values passed to a model constructor.
- **Composable constraints** — chain checks such as `.positive()`, `.between()`,
  and `.email()`.
- **Useful built-in types** — integers, strings, dates, lists, and fixed-shape
  tuples.
- **Defaults and optional fields** — make fields optional or provide validated
  defaults.
- **End-to-end typing** — field declarations carry their types through model
  attributes, assignments, collection items, and tuple positions, so your editor
  and type checker can help throughout your code.
- **Python 3.11+** — uses modern Python typing features.

## Installation

Typely requires Python 3.11 or later. To install from a source checkout:

```bash
python -m pip install .
```

## Get started

```python
from typely import BaseModel, integer, string


class User(BaseModel):
    name = string().default("Guest")
    age = integer().min(0).max(130)
    score = integer().between(0, 100).default(50)


user = User(age=25, score=92)

print(user.name)   # Guest
print(user.age)    # 25
print(user.score)  # 92

user.age = -1      # Raises ValueError
User(age=25, unknown=1)  # Raises TypeError
```

Values are checked both during construction and whenever they are assigned
afterwards. A failed assignment does not replace the field's previous value.
Unknown keyword arguments passed to a model constructor raise `TypeError`.

## Fields and constraints

Import the field factories from `typely`:

| Factory | Validates | Available constraints |
| --- | --- | --- |
| `integer()` | Integers (booleans are not accepted as integers) | `.positive()`, `.min(n)`, `.max(n)`, `.between(min, max)` |
| `string()` | Strings | `.regex(pattern)`, `.uuid()`, `.email()`, `.url()`, `.domain()`, `.min(n)`, `.max(n)`, `.between(min, max)` |
| `date()` | `datetime.date`, `datetime.datetime`, or a date string | `.min(date)`, `.max(date)`, `.between(min, max)` |
| `array(field)` | A list whose elements match `field` | `.minLength(n)`, `.maxLength(n)`, `.fixedLength(n)`, `.distinct()` |
| `uple(...)` | A tuple with one matching field per position | Constraints on each tuple element's field |

Constraints can be chained. Defaults are validated when they are set and again
if later constraints are added:

```python
from typely import BaseModel, array, integer, string


class Product(BaseModel):
    sku = string().regex(r"[A-Z]{3}-\d{4}").default("ABC-1234")
    quantity = integer().min(0).default(0)
    ratings = array(integer().between(1, 5)).maxLength(10)
```

Integer and date `.min()` / `.max()` bounds are inclusive. String `.min(n)`
accepts strings with **at least** `n` characters, and `.max(n)` accepts strings
with **at most** `n` characters. In other words, both string length boundaries
are inclusive too.

## Typed from declaration to use

Typely uses generic fields and typed descriptors so a field's type stays visible
as you read and assign model attributes. Collection and tuple factories carry
element types too, helping your editor and type checker catch mismatches before
you run the code:

```python
from typely import BaseModel, array, integer, string, uple


class Reading(BaseModel):
    label = string()
    values = array(integer())
    result = uple(integer(), string())


reading = Reading(label="Morning", values=[18, 21], result=(2, "ok"))
label: str = reading.label
first_value: int = reading.values[0]
result_code: int = reading.result[0]
```

Tuple positions are precisely typed for tuples of up to five fields. As with
any Python typing workflow, use a type checker such as mypy or Pyright to get
static feedback; Typely also enforces its validation rules at runtime.

## Transforming values

Use `.transform()` to control the value returned when a field is read. Typely
validates and stores the original value; the transform is applied when you
access the field. This is handy for presentation or normalization without
changing the value you assigned:

```python
from typely import BaseModel, string


class User(BaseModel):
    name = string().transform(str.title)


user = User(name="ada lovelace")
print(user.name)  # Ada Lovelace
```

Transforms compose with field constraints and defaults:

```python
class Label(BaseModel):
    value = string().min(3).default("typely").transform(str.upper)


label = Label()
print(label.value)  # TYPELY
```

This example returns a string, so its result matches the declared field type.
For accurate static typing, keep a transform's result compatible with that
field's type; type-changing transforms are not currently reflected in the
inferred field type.

## Optional fields and defaults

An unassigned required field raises `AttributeError` when read. Use
`.optional()` to make an unset field return `None`, or `.default(value)` to
provide a validated fallback:

```python
from typely import BaseModel, string


class Profile(BaseModel):
    nickname = string().optional()
    display_name = string().default("Anonymous")


profile = Profile()
assert profile.nickname is None
assert profile.display_name == "Anonymous"
```

Defaults are shared field-level values; use immutable defaults where possible.

## Dates

Date fields accept `datetime.date` objects, `datetime.datetime` objects (which
are normalized to dates), and strings. ISO 8601 is the default string format:

```python
from typely import BaseModel, date


class Event(BaseModel):
    day = date().between("2026-01-01", "2026-12-31")


event = Event(day="2026-10-26")
print(event.day)  # datetime.date(2026, 10, 26)
```

For another string format, use Python's `strptime` format directives:

```python
from typely import BaseModel, date


class Appointment(BaseModel):
    day = date(format="strptime", strp="%d/%m/%Y")


appointment = Appointment(day="26/10/2026")
```

Date values are stored and returned as `datetime.date` objects, not strings.

## Lists and tuples

Pass a field factory to `array()` to validate every list element. Use
`minLength()`, `maxLength()`, or `fixedLength()` to constrain the collection:

```python
from typely import BaseModel, array, integer


class Survey(BaseModel):
    answers = array(integer().between(1, 5)).fixedLength(3)


survey = Survey(answers=[4, 5, 3])
```

Use `uple()` for a tuple whose positions have different validation rules:

```python
from typely import BaseModel, integer, string, uple


class Measurement(BaseModel):
    result = uple(integer().min(0), string().regex(r"[a-z]+"))


measurement = Measurement(result=(42, "ok"))
```

The tuple must have exactly the same number of values as the fields passed to
`uple()`. Both forms are supported: `uple(integer(), string())` and
`uple((integer(), string()))`.

## Nested models

Use a nested model instance as a field default, or annotate a field with a
`BaseModel` subclass to accept it in the parent constructor:

```python
from typely import BaseModel, integer, string


class Address(BaseModel):
    city = string()


class User(BaseModel):
    age = integer()
    address: Address


user = User(age=25, address=Address(city="Paris"))
print(user.address.city)  # Paris
```

Nested model instances used as defaults can be overridden when constructing the
parent:

```python
class UserWithDefaultAddress(BaseModel):
    age = integer()
    address = Address(city="Paris")


user = UserWithDefaultAddress(age=25)
assert user.address.city == "Paris"

user = UserWithDefaultAddress(age=25, address=Address(city="Lyon"))
assert user.address.city == "Lyon"
```

## Error behavior

Typely uses Python exceptions to make validation failures explicit:

- `TypeError` for a value with the wrong type or an unknown model constructor
  argument.
- `ValueError` for a value that has the right type but fails a constraint.
- `AttributeError` when reading a required field that has not been assigned and
  has no default.

## Development

Run the test suite from the project directory:

```bash
python -m pytest
```

## License

No license is currently specified in the project. Add a license before
redistributing Typely or accepting contributions under an open-source license.
