"""Tests for the `meta` module."""

import dataclasses as dc
from typing import Annotated, Literal, TypedDict

import numpy as np

import photonetc as pe


def test_group_set_attr():
    class Attrs(TypedDict):
        a_float: Annotated[pe.info.NDArrayF64, Literal[1]]
        a_int: Annotated[pe.info.NDArrayI32, Literal[1]]
        a_str: Annotated[pe.info.NDArrayStr, Literal[1]]
        a_list_int: Annotated[pe.info.NDArrayI32, Literal[3]]
        a_list_str: Annotated[pe.info.NDArrayStr, Literal[3]]

    @dc.dataclass
    class Grp(pe.meta.Group):
        attrs: Attrs

    g = Grp(
        {
            "a_float": np.array([0]),
            "a_int": np.array([0], dtype=np.int32),
            "a_str": np.array(["a"]),
            "a_list_int": np.array([0, 0, 0], dtype=np.int32),
            "a_list_str": np.array(["a", "a", "a"]),
        }
    )

    g.set_attr("a_float", 1)
    g.set_attr("a_int", 1)
    g.set_attr("a_str", "b")
    g.set_attr("a_list_int", [1, 1, 1])
    g.set_attr("a_list_str", ["b", "b", "b"])
    assert (g.attrs["a_float"] == np.array([1])).all()
    assert (g.attrs["a_int"] == np.array([1], dtype=np.int32)).all()
    assert (g.attrs["a_str"] == np.array(["b"])).all()
    assert (g.attrs["a_list_int"] == np.array([1, 1, 1])).all()
    assert (g.attrs["a_list_str"] == np.array(["b", "b", "b"])).all()


def test_group():
    """Test that the `photonetc.meta.group` decorator is working correclty functionally.
    + `__init__` arguments will not be linted as expected.
    + Item keys and types will not be known.
    + Attributes should lint correctly.
    """

    class ChildAttrs(TypedDict):
        strval: str
        intval: int

    @dc.dataclass
    class Child:
        attrs: ChildAttrs

    class ParentAttrs(TypedDict):
        strval: str
        boolval: bool

    class ParentItems(TypedDict):
        child: Child

    @pe.meta.group
    class Parent:
        attrs: ParentAttrs
        _items: ParentItems

    c = Child({"strval": "child", "intval": 0})
    p = Parent(attrs={"strval": "parent", "boolval": True}, _items={"child": c})  # type: ignore

    assert p.attrs["strval"] == "parent"
    assert p["child"].attrs["strval"] == "child"  # type: ignore


def test_group_typing():
    """Test that typing from the stub file is working correctly.
    + Item keys should be autocompleted.
    + Item value types should be known.
    + Attributes should be autocompleted.
    + Should not create linting errors.
    """
    ax0 = pe.info.CameraAxis0({"Name": np.array(["x"])})
    ax1 = pe.info.CameraAxis1(
        {
            "Coefs": np.zeros(1),
            "Decimals": np.zeros(1, dtype=np.int32),
            "Name": np.array(["y"]),
            "Unit": np.array(["cm"]),
        }
    )

    axis = pe.info.CameraAxis(
        attrs={
            "Coefs": np.zeros(1),
            "Decimals": np.zeros(1, dtype=np.int32),
            "Name": np.array(["y"]),
            "Unit": np.array(["cm"]),
        },
        _items={"0": ax0, "1": ax1},
    )

    assert axis.attrs["Coefs"][0] == 0
    assert axis["0"].attrs["Name"] == "x"
    assert axis["1"].attrs["Name"] == "y"
