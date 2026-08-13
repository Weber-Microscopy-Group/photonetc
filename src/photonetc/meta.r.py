import h5py
from typing import TypedDict, is_typeddict, TypeVar
from dataclasses import is_dataclass
from inspect import Parameter, Signature

T = TypeVar("T")

ATTRS_NAME = "attrs"


# Based off `typing._TypedDictMeta`.
class _GroupMeta(type):
    def __new__(cls, name, bases, ns):
        gp_dict = type.__new__(_GroupMeta, name, (dict,), ns)
        annotations = {}
        own_annotations = ns.get("__annotations__", {})
        annotations.update(own_annotations)

        required_keys = set()
        optional_keys = set()
        readonly_keys = set()
        mutable_keys = set()
        for annotation_key, _annotation_type in own_annotations.items():
            required_keys.add(annotation_key)

        gp_dict.__annotations__ = annotations
        gp_dict.__required_keys__ = frozenset(required_keys)
        gp_dict.__optional_keys__ = frozenset(optional_keys)
        gp_dict.__readonly_keys__ = frozenset(readonly_keys)
        gp_dict.__mutable_keys__ = frozenset(mutable_keys)
        return gp_dict

    __call__ = dict


def GroupT(typename, fields):
    ns = {"__annotations__": dict(fields)}
    gd = _GroupMeta(typename, (), ns)
    return gd


_GroupT = type.__new__(_GroupMeta, "GroupT", (), {})
GroupT.__mro_entries__ = lambda bases: (_GroupT,)


def group2(cls):
    print(cls)
    return cls


@group2
class Test(TypedDict):
    a: int


t = Test(a=1)
t[""]


def Group(cls):
    attrs_typ = None
    fields = []
    for name, typ in cls.__annotations__.items():
        if name == ATTRS_NAME:
            attrs_typ = typ
        else:
            fields.append((name, typ))

    init_params_req = []
    if attrs_typ is not None:
        init_params_req.append(
            Parameter(
                ATTRS_NAME,
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=attrs_typ,
            )
        )

    for name, typ in fields:
        init_params_req.append(
            Parameter(
                name,
                Parameter.POSITIONAL_OR_KEYWORD,
                annotation=typ,
            )
        )
        required_keys.add(name)

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
    cls.__required_keys__ = frozenset(required_keys)

    return cls


def load_group(grp: h5py.Group, cls: type[T]) -> T:
    assert is_dataclass(cls)
    vals = {}
    for key, typ in cls.__annotations__.items():
        if key == ATTRS_NAME:
            assert is_typeddict(typ)
            attrs = {}
            for name in typ.__annotations__:
                attrs[name] = grp.attrs[name]
            vals[ATTRS_NAME] = attrs
            continue

        val = grp[key]
        if isinstance(val, h5py.Group):
            vals[key] = load_group(val, typ)
        elif isinstance(val, h5py.Dataset):
            # TODO
            vals[key] = None
        else:
            raise TypeError(f"unknown type at {key}")

    return cls(vals)
