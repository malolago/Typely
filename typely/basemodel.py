from typing import Any, get_type_hints

from .field import Field


class BaseModel:
    def __init__(self, **kwargs: object) -> None:
        fields: dict[str, Field[Any]] = {}
        nested: dict[str, type[BaseModel]] = {}

        for cls in reversed(type(self).__mro__):
            for name, value in vars(cls).items():
                if isinstance(value, Field):
                    fields[name] = value
                elif isinstance(value, BaseModel):
                    nested[name] = type(value)
        for name, annotation in get_type_hints(type(self)).items():
            if isinstance(annotation, type) and issubclass(annotation, BaseModel):
                nested[name] = annotation

        self._fields = fields
        self._nested = nested

        unknown = set(kwargs) - fields.keys() - nested.keys()
        if unknown:
            raise TypeError(f"Unknown fields: {', '.join(sorted(unknown))}")

        for name, value in kwargs.items():
            setattr(self, name, value)
