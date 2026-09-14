"""Utilities to develop this library. Intended for internal use only."""

import dataclasses as dc
from abc import ABC
from types import UnionType
from typing import (
    Any,
    NotRequired,
    Union,
    get_args,
    get_origin,
    Annotated,
    Literal,
    TypedDict,
)
import numbers

import h5py
import numpy as np

_ITEMS = "__group_items__"
_STORE = "__items__"
_REQUIRED_ATTRS = "__required_attrs__"
_OPTIONAL_ATTRS = "__optional_attrs__"
_REQUIRED_ITEMS = "__required_items__"
_OPTIONAL_ITEMS = "__optional_items__"


def _process_group(cls: type, items_name: str):
    items = None
    for name, typ in cls.__annotations__.items():
        if name == items_name:
            items = (name, typ)
            break

    if items is not None:
        required = []
        optional = []
        for name, typ in items[1].__annotations__.items():
            if is_optional(typ):
                optional.append(name)
            else:
                required.append(name)
        required.sort()
        optional.sort()

        setattr(cls, _REQUIRED_ITEMS, required)
        setattr(cls, _OPTIONAL_ITEMS, optional)
        setattr(cls, _ITEMS, items)
        orig_post_init = getattr(cls, "__post_init__", None)

        def getitem(self, name: str):
            return self.__items__[name]

        def setitem(self, name: str, value: Any):
            self.__items__[name] = value

        def post_init(self):
            if orig_post_init is not None:
                orig_post_init(self)

            setattr(self, _STORE, getattr(self, items_name))
            delattr(self, items_name)

        cls.__getitem__ = getitem
        cls.__setitem__ = setitem
        cls.__post_init__ = post_init

    return dc.dataclass(cls)


def group(cls=None, /, *, items_name="_items"):
    """Creates a class whose attributes act as normal except if named as `item_names`.
    Object in the `item_names` attribute are accessed as items
    (i.e. Using dictionary notation `grp["item"]`).

    Used to mimic an hdf5 group object where attriubtes are access via `.attrs`
    and subgroups and datasets are accessed vis dictionary notation.

    Items are merged when inherited.

    Args:
        items_name (str, optional): Name of items attribute. Defaults to "_items".

    Returns:
        type: Modified class.

    Examples:
        class ChildAttrs(TypedDict):
            strval: str
            intval: int

        @dataclass
        class Child:
            attrs: ChildAttrs

        class ParentAttrs(TypedDict):
            strval: str
            boolval: bool

        class ParentItems(TypedDict):
            child: Child

        @group
        class Parent:
            attrs: ParentAttrs
            _items: ParentItems

        c = Child(attrs={"strval": "child", "intval": 0})
        p = Parent(attrs={"strval": "parent", "boolval": True}, _items={"child": c})

        assert p.attrs["strval"] == "parent"
        assert p["child"].attrs["strval"] == "child"

    Notes:
        + Treats the in put class as a modified `dataclass` where the attribute
        with name `item_names` is removed.
    """

    def wrap(cls):
        return _process_group(cls, items_name)

    if cls is None:
        return wrap
    else:
        return wrap(cls)


class Group(ABC):
    @classmethod
    def from_group(cls: type, group: h5py.Group, path: str = ""):
        attrs = None
        if "attrs" in cls.__annotations__:
            cls_attrs = cls.__annotations__["attrs"].__annotations__
            attrs = {}
            missing = []
            for key, typ in cls_attrs.items():
                try:
                    val = group.attrs[key]
                except KeyError:
                    if is_optional:
                        val = None
                    else:
                        missing.append(key)
                        continue

                attrs[key] = val

            if len(missing) > 0:
                raise ValueError(f"missing group attributes {missing} for {path}")
        cls_items = getattr(cls, _ITEMS, None)
        items = None
        if cls_items is not None:
            missing = []
            expected = cls_items[1].__annotations__
            for key, typ in expected.items():
                if key not in group and not is_optional(typ):
                    missing.append(key)

            if len(missing) > 0:
                raise ValueError(f"missing groups {missing} from {cls.__name__}")

            items = {}
            for key, typ in expected.items():
                cpath = path + f"/{key}"
                try:
                    child = group[key]
                except KeyError:
                    items[key] = None
                    continue

                ctyp = typ
                if is_optional(typ):
                    if get_origin(typ) is NotRequired:
                        (base,) = get_args(typ)
                        ctyp = base
                    else:
                        styps = get_args(typ)
                        if len(styps) == 2:
                            for styp in styps:
                                if styp is type(None):
                                    continue
                                ctyp = styp
                        else:
                            raise NotImplementedError(
                                f"unhandled annotation type {typ}"
                            )

                if isinstance(child, h5py.Group) and is_ndarray_annotation(ctyp):
                    raise TypeError(f"expected dataset for {cpath}, but found group")
                if isinstance(child, h5py.Dataset) and not is_ndarray_annotation(ctyp):
                    raise TypeError(f"expected group for {cpath}, but found dataset")

                try:
                    items[key] = ctyp.from_group(child, cpath)
                except AttributeError as err:
                    raise AttributeError(f"[{ctyp}] {err}")

        if attrs is not None and items is None:
            return cls(attrs)
        if attrs is None and items is not None:
            return cls(items)
        if attrs is not None and items is not None:
            return cls(attrs, items)

        raise ValueError(f"neither of attrs nor items present at {path}")

    def to_h5(self, group: h5py.Group, path: str = ""):
        attrs = getattr(self, "attrs", None)
        items = getattr(self, _STORE, None)
        if attrs is not None:
            try:
                attrs_dict_to_h5(group, attrs)
            except Exception as err:
                err.add_note(f"at group {path}")
                raise
        if items is not None:
            for name, value in items.items():
                gpath = name
                if path != "":
                    gpath = f"{path}/{gpath}"

                if isinstance(value, np.ndarray):
                    if is_numpy_string_dtype(value.dtype):
                        value = value.astype(h5py.string_dtype())
                    group.create_dataset(name, data=value)
                elif isinstance(value, Group) or is_group(value):
                    grp = group.create_group(name)
                    value.to_h5(grp, gpath)
                else:
                    raise TypeError(f"unknown object at {gpath}: {type(value)}")

    def set_attr(self, name: str, value: Any):
        """Set an attribute, coercing the value into the field's value.

        Args:
            name (str): Attribute name.
            value (Any): Value.

        Raises:
            AttributeError: Attribute with name does not exist.
            ValueError: Value is incompatible with expected type.
        """
        typ = self.__annotations__["attrs"]
        base = typ.__annotations__[name]
        if get_origin(base) is not Annotated:
            raise TypeError(f"field {name} is not annotated")

        try:
            (arr, shape) = get_args(base)
        except ValueError:
            raise TypeError(
                f"field {name} annotation is invalid, expected two arguments"
            )
        if not is_ndarray_annotation(arr):
            raise TypeError(f"field {name} is not a numpy array")
        if get_origin(shape) is not Literal:
            raise TypeError(f"field {name} is missing a shape annotation")
        shape = get_args(shape)

        try:
            (_, dtype) = get_args(arr)
        except ValueError:
            raise TypeError(
                f"field {name} annotation is invalid, numpy array is missing data type"
            )
        (dtype,) = get_args(dtype)

        attrs: dict = self.attrs  # type: ignore
        if isinstance(value, np.ndarray):
            if len(value.shape) != len(shape):
                raise ValueError(
                    f"incorrect number of dimensions, expected {shape} found {value.shape}"
                )
            for expected, actual in zip(shape, value.shape):
                if expected != actual:
                    raise ValueError(
                        f"incorrect shape, expected {shape} found {value.shape}"
                    )

            try:
                attrs[name] = value.astype(dtype)  # pyright: ignore[reportIndexIssue]
            except ValueError as err:
                err.add_note(f"field {name}")
                raise
        elif isinstance(value, list):
            if len(shape) != 1:
                raise ValueError(
                    "can not use lists for complex attributes, use a numpy array instead"
                )
            if len(value) != shape[0]:
                raise ValueError(
                    f"incorrect shape, expected {shape} found {(len(value),)}"
                )

            try:
                val = np.array(value, dtype=dtype)
            except ValueError as err:
                err.add_note(f"field {name}")
                raise

            attrs[name] = val  # pyright: ignore[reportIndexIssue]
        elif isinstance(value, numbers.Number):
            if len(shape) != 1 or shape[0] != 1:
                raise ValueError(f"expected array-like with shape {shape}")
            if not np.isdtype(dtype, "numeric"):
                raise ValueError(f"expected {dtype} type")

            try:
                val = np.array([value], dtype=dtype)
            except ValueError as err:
                err.add_note(f"field {name}")
                raise

            attrs[name] = val  # pyright: ignore[reportIndexIssue]
        elif isinstance(value, str):
            if len(shape) != 1 or shape[0] != 1:
                raise ValueError(f"expected array-like with shape {shape}")
            if dtype is not np.str_:
                raise ValueError(f"expected {dtype} type")

            try:
                val = np.array([value], dtype=dtype)
            except ValueError as err:
                err.add_note(f"field {name}")
                raise

            attrs[name] = val  # pyright: ignore[reportIndexIssue]
        else:
            raise TypeError(f"unhandled type {type(value)}")


def attrs_dict_to_h5(group: h5py.Group, attrs):
    for name, value in attrs.items():
        if isinstance(value, np.ndarray) and is_numpy_string_dtype(value.dtype):
            value = value.astype(h5py.string_dtype())
        try:
            group.attrs[name] = value
        except Exception as err:
            err.add_note(f"occured while assigning attribue `{name}`")
            raise


def is_union(typ: type) -> bool:
    return get_origin(typ) in (Union, UnionType)


def is_optional(typ: type) -> bool:
    orig = get_origin(typ)
    if orig is NotRequired:
        return True
    if not is_union(typ):
        return False

    return type(None) in get_args(typ)


def is_group(obj) -> bool:
    return hasattr(obj, _ITEMS)


def is_ndarray_annotation(annotation) -> bool:
    return get_origin(annotation) is np.ndarray or (
        isinstance(annotation, type) and issubclass(annotation, np.ndarray)
    )


def is_numpy_string_dtype(dtype: np.dtype) -> bool:
    if isinstance(dtype, np.dtypes.StringDType):
        return True

    return dtype.kind in {"U", "S"}
