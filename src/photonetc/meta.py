"""Helpers."""

from __future__ import annotations

import dataclasses as dc
from inspect import Parameter, Signature
from typing import (
    Any,
    Callable,
    Generic,
    TypeVar,
    dataclass_transform,
    overload,
)

__all__ = [
    "attribute",
    "attribute_list",
]


T = TypeVar("T")


class Attribute(Generic[T]):
    __slots__ = [
        "default",
        "default_factory",
        "name",
        "type",
        "value",
    ]

    def __init__(self, name: str, default, default_factory):
        if default is not dc.MISSING and default_factory is not dc.MISSING:
            raise ValueError("cannot specify both default and default_factory")

        self.name = name
        self.default = default
        self.default_factory = default_factory
        self.type = dc.MISSING
        self.value = dc.MISSING


@overload
def attribute(name: str, default: T) -> T: ...
@overload
def attribute(name: str, default_factory: Callable[[], T]) -> T: ...
@overload
def attribute(name: str) -> Any: ...


def attribute(name: str, default=dc.MISSING, default_factory=dc.MISSING):  # type: ignore
    if default is not dc.MISSING and default_factory is not dc.MISSING:
        raise ValueError("cannot specify both default and default_factory")

    return Attribute(name, default=default, default_factory=default_factory)


@dataclass_transform(field_specifiers=(attribute,))
def attribute_list(cls):
    attrs = []
    for name, typ in cls.__annotations__.items():
        attrs.append((name, typ))

    init_params_req = []
    init_params_opt = []
    for name, typ in attrs:
        attr: Attribute = getattr(cls, name)
        attr.type = typ
        if attr.default is dc.MISSING and attr.default_factory is dc.MISSING:
            init_params_req.append(
                Parameter(
                    name,
                    Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=typ,
                )
            )
        elif attr.default is not dc.MISSING:
            init_params_opt.append(
                Parameter(
                    name,
                    Parameter.POSITIONAL_OR_KEYWORD,
                    default=attr.default,
                    annotation=typ,
                )
            )
            attr.value = attr.default
        elif attr.default_factory is not dc.MISSING:
            init_params_opt.append(
                Parameter(
                    name,
                    Parameter.POSITIONAL_OR_KEYWORD,
                    default=attr.default_factory(),
                    annotation=typ,
                )
            )
            attr.value = attr.default_factory()

        setattr(cls, f"_{name}", attr)
        delattr(cls, name)

        def getter(self, name=name):
            attr = getattr(self, f"_{name}")
            return attr.value

        def setter(self, value: Any, name=name):
            attr = getattr(self, f"_{name}")
            attr.value = value

        setattr(cls, name, property(fget=getter, fset=setter))

    params = (
        [Parameter("self", Parameter.POSITIONAL_ONLY)]
        + init_params_req
        + init_params_opt
    )
    sig = Signature(params)

    def __init__(*args, **kwargs) -> None:
        bound = sig.bind(*args, **kwargs)
        self = bound.arguments.pop("self")
        for name, value in bound.arguments.items():
            attr = getattr(self, f"_{name}")
            attr.value = value

    __init__.__signature__ = sig  # type: ignore
    cls.__init__ = __init__

    return cls
