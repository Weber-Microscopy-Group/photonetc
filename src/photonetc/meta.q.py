# %%
from typing import TypedDict
from inspect import Parameter, Signature
import h5py
import dataclasses


# %%
class _MISSING_TYPE:
    pass


MISSING = _MISSING_TYPE()

ATTRS_NAME = "attrs"


def group(cls):
    attrs = None
    children = []
    for name, typ in cls.__annotations__.items():
        if name == ATTRS_NAME:
            if attrs is None:
                attrs = typ
                continue
            else:
                raise ValueError("attrs defined multiple times")

        children.append((name, typ))

    init_params_req = []
    required_keys = set()
    if attrs is not None:
        init_params_req.append(
            Parameter(ATTRS_NAME, Parameter.POSITIONAL_OR_KEYWORD, annotation=attrs)
        )
    for name, typ in children:
        init_params_req.append(
            Parameter(name, Parameter.POSITIONAL_OR_KEYWORD, annotation=typ)
        )

    params = [Parameter("self", Parameter.POSITIONAL_ONLY)] + init_params_req
    sig = Signature(params)

    def __init__(*args, **kwargs) -> None:
        bound = sig.bind(*args, **kwargs)
        self = bound.arguments.pop("self")
        for name, value in bound.arguments.items():
            attr = getattr(self, f"_{name}")
            attr.value = value

    __init__.__signature__ = sig  # type: ignore
    cls.__init__ = __init__

    def getitem(self, key: str):
        return 5

    cls.__getitem__ = getitem

    cls.__required_keys__ = frozenset(required_keys)

    return cls


# %%
class ChildAttrs(TypedDict):
    one: int
    two: int


class Child:
    attrs: ChildAttrs


class TestAttrs(TypedDict):
    a: int
    b: str


@group
class Test:
    attrs: TestAttrs
    child: Child


# %%
t = Test()
t.attrs["a"]
c = t[""]
