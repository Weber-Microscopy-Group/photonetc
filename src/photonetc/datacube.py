"""Shared resources for data cubes."""

from typing import Generic, TypeVar

import h5py
import numpy as np

from .meta import attribute, attribute_list

T = TypeVar("T")
A = TypeVar("A")


# @group("Cube")
# class InfoCube:
#     NAME: str  # from `group`
#     acq_mode = Attribute("AcqMode", str)
#     name = Attribute("Name", str)
#     type = Attribute("Type", str)
#     creation_date = Attribute(
#         "CreationDate",
#         str,
#         lambda: dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
#     )


# @group("Info")
# class Info:
#     cube: InfoCube


class Group(Generic[A, T]):
    attrs: A
    children: T


class Dataset(Generic[A, T]):
    attrs: A
    data: T


@attribute_list
class InfoCubeAttrs:
    acq_mode: str = attribute("AcqMode")
    name: str = attribute("Name")
    type: str = attribute("Type")
    creation_date: str = attribute(
        "CreationDate",
        default_factory=lambda: dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    )


class Test:
    val: str = attribute("Name")


class InfoCube(Group[InfoCubeAttrs, None]):
    pass
