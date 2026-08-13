"""Tests for the `meta` module."""

import pathlib
import dataclasses as dc
import h5py
import photonetc as pe
import numpy as np
from typing import TypedDict

DATA_PATH_SPECTRALCUBE = pathlib.Path(__file__).parent.parent / "data/spectralcube.h5"
DATA_PATH_TEMPORALCUBE = pathlib.Path(__file__).parent.parent / "data/temporalcube.h5"


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

    c = Child(attrs={"strval": "child", "intval": 0})
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
    ax0 = pe.info.CameraAxis0({"Name": "x"})
    ax1 = pe.info.CameraAxis1(
        {"Coefs": np.zeros(1), "Decimals": np.zeros(1), "Name": "y", "Unit": "cm"}
    )

    axis_items = pe.info.CameraAxisItems({"0": ax0, "1": ax1})
    axis = pe.info.CameraAxis(
        attrs={
            "Coefs": np.zeros(1),
            "Decimals": np.zeros(1),
            "Name": "y",
            "Unit": "cm",
        },
        _items={"0": ax0, "1": ax1},
    )

    assert axis.attrs["Coefs"][0] == 0
    assert axis["0"].attrs["Name"] == "x"
    assert axis["1"].attrs["Name"] == "y"
