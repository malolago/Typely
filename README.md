# Typely 

Validation for Python models that stays out of your way.

Declare your fields where you use them, chain the constraints you care about, and get a clear error when a value doesn't fit.


```python
from typely import BaseModel, integer, string


class User(BaseModel):
    name = string().default("Guest")
    age = integer().min(0).max(130)
    score = integer().between(0, 100).default(50)


user = User(age=25, score=92)
print(user.name)  # Guest
user.age = -1     # ValueError
```

## Why Typely?

Because validation should live where the data lives. A few things Typely cares about:

- Fields are declared once, then behave like normal attributes.
- Validation runs on every assignment, including values passed to the constructor. A bad value never silently replaces a good one.
- Constraints chain the way you'd expect: `.positive()`, `.between(1, 5)`, `.email()`, ...
- The usual suspects are built in: integers, strings, dates, lists, and fixed-shape tuples.
- Fields can be optional, or carry validated defaults.
- Types travel with your fields — through attributes, assignments, list items, and tuple positions — so your editor and type checker can actually help.
- Python 3.11+, because the modern typing features are worth it.

## Installation 📦

Typely needs Python 3.11 or later. The easiest way to install it is straight from GitHub, with uv:

```bash
uv add "typely @ git+https://github.com/malolago/Typely.git"
```

Or, if you prefer working from a local clone:

```bash
git clone https://github.com/malolago/Typely.git
cd Typely
uv sync
```

## Getting started 🚀

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

A few details worth knowing up front:

- Values are checked at construction *and* on every assignment afterwards.
- A failed assignment doesn't replace the field's previous value, so nothing gets corrupted.
- Unknown keyword arguments in a constructor raise `TypeError`, so typos don't slip through.

## Fields and constraints 🧩

Import the field factories from `typely`:

| Factory | Validates | Constraints |
| --- | --- | --- |
| `integer()` | Integers (no, `True` is not an integer here) | `.positive()`, `.min(n)`, `.max(n)`, `.between(min, max)` |
| `string()` | Strings | `.regex(pattern)`, `.uuid()`, `.email()`, `.url()`, `.domain()`, `.min(n)`, `.max(n)`, `.between(min, max)` |
| `date()` | `datetime.date`, `datetime.datetime`, or a date string | `.min(date)`, `.max(date)`, `.between(min, max)` |
| `array(field)` | A list whose elements match `field` | `.minLength(n)`, `.maxLength(n)`, `.fixedLength(n)`, `.distinct()` |
| `uple(...)` | A tuple with one matching field per position | Whatever constraints each element's field supports |

Constraints chain freely. Defaults are validated when set, and re-validated if you add constraints afterwards:

```python
from typely import BaseModel, array, integer, string


class Product(BaseModel):
    sku = string().regex(r"[A-Z]{3}-\d{4}").default("ABC-1234")
    quantity = integer().min(0).default(0)
    ratings = array(integer().between(1, 5)).maxLength(10)
```

Be mindful however, bounds are inclusive. `.min(0)` accepts 0, string `.min(3)` wants *at least* 3 characters, and `.max(n)` at most `n`.

## Types, all the way down 🧠

Typely leans on generic fields and typed descriptors, so a field's type stays visible as you read and assign model attributes. Collection factories carry their element types too. Your editor and type checker catch mismatches before you even run the code:

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

Tuple positions are precisely typed (for tuples of up to five fields). As with any Python typing, you'll want a type checker like mypy or Pyright for static feedback. Typely enforces its rules at runtime regardless.

## Transforming values ✨

Sometimes you want to store one thing and read back another — normalizing a string, say, without touching what was actually assigned. That's what `.transform()` is for: the original value is validated and stored, and the transform runs when you read the field:

```python
from typely import BaseModel, string


class User(BaseModel):
    name = string().transform(str.title)


user = User(name="ada lovelace")
print(user.name)  # Ada Lovelace
```

Transforms play nicely with constraints and defaults:

```python
class Label(BaseModel):
    value = string().min(3).default("typely").transform(str.upper)


label = Label()
print(label.value)  # TYPELY
```

## Optional fields and defaults ⚙️

Reading a required field that was never assigned raises `AttributeError`. If that's not what you want, make the field `.optional()` (unset reads as `None`) or give it a validated `.default(value)`:

```python
from typely import BaseModel, string


class Profile(BaseModel):
    nickname = string().optional()
    display_name = string().default("Anonymous")


profile = Profile()
assert profile.nickname is None
assert profile.display_name == "Anonymous"
```

One caveat: defaults are shared at the field level, so stick to immutable values where you can.

## Dates 📅

Date fields accept `datetime.date` objects, `datetime.datetime` objects (normalized to dates), and strings — ISO 8601 by default:

```python
from typely import BaseModel, date


class Event(BaseModel):
    day = date().between("2026-01-01", "2026-12-31")


event = Event(day="2026-10-26")
print(event.day)  # datetime.date(2026, 10, 26)
```

For another format, tell the field to use `strptime` directives:

```python
from typely import BaseModel, date


class Appointment(BaseModel):
    day = date(format="strptime", strp="%d/%m/%Y")


appointment = Appointment(day="26/10/2026")
```

## Lists and tuples 📋

Hand a field factory to `array()` and every element gets validated. Length constraints are right there too:

```python
from typely import BaseModel, array, integer


class Survey(BaseModel):
    answers = array(integer().between(1, 5)).fixedLength(3)


survey = Survey(answers=[4, 5, 3])
```

For tuples where each position has its own rules, use `uple()`:

```python
from typely import BaseModel, integer, string, uple


class Measurement(BaseModel):
    result = uple(integer().min(0), string().regex(r"[a-z]+"))


measurement = Measurement(result=(42, "ok"))
```

The tuple must have exactly as many values as the fields you passed — and both `uple(integer(), string())` and `uple((integer(), string()))` work.

## Nested models 🪆

Models compose the way you'd hope. Use a nested model instance as a field default, or annotate a field with a `BaseModel` subclass to accept it in the parent constructor:

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

A nested instance used as a default can still be overridden at construction:

```python
class UserWithDefaultAddress(BaseModel):
    age = integer()
    address = Address(city="Paris")


user = UserWithDefaultAddress(age=25)
assert user.address.city == "Paris"

user = UserWithDefaultAddress(age=25, address=Address(city="Lyon"))
assert user.address.city == "Lyon"
```

## When things go wrong 💥

Typely keeps its error vocabulary small, on purpose:

- `TypeError` — wrong type, or an unknown keyword argument in a constructor.
- `ValueError` — right type, but a constraint says no.
- `AttributeError` — you read a required field that was never assigned and has no default.

## Development 🛠️

Clone the repo and sync dependencies with uv:

```bash
git clone https://github.com/malolago/Typely.git
cd Typely
uv sync
```

Dev dependencies live in the dev group of `pyproject.toml` — add new ones with `uv add --dev`.

Run the tests:

```bash
uv run pytest
```

With coverage:

```bash
uv run pytest --cov=typely --cov-report=term-missing
```

Lint and formatting are handled by ruff:

```bash
uv run ruff check .        # lint
uv run ruff format --check .  # format check

uv run ruff check --fix .  # auto-fix
uv run ruff format .       # format
```

## Contributing 🤝

Issues and pull requests are welcome! If you're adding a feature or fixing a bug, a test or two to go with it goes a long way. 🙌

## License 📜

Typely is released under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license.