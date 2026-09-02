"""Shared resources for data cubes."""

from abc import ABC
from enum import Enum
from types import UnionType
from typing import Any, TypeAlias, TypedDict

import h5py
import numpy as np

from . import info, meta

NDArrayF64: TypeAlias = np.typing.NDArray[np.float64]
NDArrayI32: TypeAlias = np.typing.NDArray[np.int32]
NDArrayStr: TypeAlias = np.typing.NDArray[np.str_]

ROOT_NAME = "Cube"
_IGNORE_NAMES = ["Display", "Processing"]


class DatacubeItems(TypedDict):
    Images: NDArrayF64
    Info: info.Info
    TimeExposure: NDArrayF64


class Datacube(ABC):
    _items: Any

    def __post_init__(self):
        i_frames = self._items["Images"].shape[0]
        t_frames = self._items["TimeExposure"].shape[0]
        if i_frames != t_frames:
            raise ValueError("Image and TimeExposure shapes are incompatible")

    @classmethod
    def from_file(cls: type, f: h5py.File) -> "Datacube":
        root = f[ROOT_NAME]
        if not isinstance(root, h5py.Group):
            raise TypeError(f"{ROOT_NAME} has invalid type, expect h5py.Group")

        all = getattr(cls, meta._ITEMS, None)
        if all is None:
            raise TypeError(f"{cls.__name__} is not a photonetc.meta.group")

        all = all[1].__annotations__
        keys_expected = list(all.keys())
        keys_required = getattr(cls, meta._REQUIRED_ITEMS)
        keys_present = list(filter(lambda key: key not in _IGNORE_NAMES, root.keys()))
        keys_expected.sort()
        keys_present.sort()
        missing = []
        for key in keys_required:
            if key not in keys_required:
                missing.append(key)
        if len(missing) > 0:
            raise ValueError(f"Missing requried keys {missing}")

        values = {}
        for key, typ in all.items():
            is_required = key in keys_required
            try:
                val = root[key]
            except KeyError:
                if is_required:
                    raise
                else:
                    values[key] = None
                    continue

            if isinstance(val, h5py.Group):
                if not meta.is_group(typ):
                    raise TypeError(f"expected group at {key}, found {typ}")

                path = ROOT_NAME + f"/{key}"
                values[key] = typ.from_group(val, path)

            elif isinstance(val, h5py.Dataset):
                if is_required and not meta.is_ndarray_annotation(typ):
                    raise TypeError(f"expected dataset at {key}, found {typ}")

                values[key] = val[()]

            else:
                raise TypeError(f"unhandled type {typ} at {key}")

        return cls(values)

    @property
    def elapsed(self) -> NDArrayF64:
        """
        Returns:
            np.ndarray: Elapsed time of each frame.
        """
        return np.cumsum(self["TimeExposure"])  # type: ignore


class SpectralCubeItems(DatacubeItems):
    GratingID: NDArrayI32
    Translation_X: NDArrayF64
    Translation_Y: NDArrayF64
    Wavelength: NDArrayF64


@meta.group
class SpectralCube(Datacube):
    _items: SpectralCubeItems

    def __post_init__(self):
        super().__post_init__()

        i_frames = self._items["Images"].shape[0]
        g_frames = self._items["GratingID"].shape[0]
        x_frames = self._items["Translation_X"].shape[0]
        y_frames = self._items["Translation_Y"].shape[0]
        w_frames = self._items["Wavelength"].shape[0]

        invalid = []
        if g_frames != i_frames:
            invalid.append("GratingID")
        if x_frames != i_frames:
            invalid.append("Translation_X")
        if y_frames != i_frames:
            invalid.append("Translation_Y")
        if w_frames != i_frames:
            invalid.append("Wavelength")

        if len(invalid) > 0:
            names = ", ".join(invalid)
            raise ValueError(f"{names} and Image shapes are incompatible")


class Bandtype(Enum):
    Broadband = 0
    Bandpass = 1


class TemporalCubeItems(DatacubeItems):
    Angle: NDArrayF64
    GratingID: NDArrayI32 | None
    Timestamp: NDArrayStr
    Wavelength: NDArrayF64 | None


@meta.group
class TemporalCube(Datacube):
    _items: TemporalCubeItems

    def __post_init__(self):
        super().__post_init__()

        if (
            self._items["GratingID"] is None and self._items["Wavelength"] is not None
        ) or (
            self._items["GratingID"] is not None and self._items["Wavelength"] is None
        ):
            raise ValueError(
                "`GratingID` and `Wavelength` must either both be present or both be absent"
            )

        i_frames = self._items["Images"].shape[0]
        a_frames = self._items["Angle"].shape[0]
        t_frames = self._items["Timestamp"].shape[0]
        g_frames = None
        w_frames = None
        if self._items["GratingID"] is not None:
            g_frames = self._items["GratingID"].shape[0]
        if self._items["Wavelength"] is not None:
            w_frames = self._items["Wavelength"].shape[0]

        invalid = []
        if g_frames is not None and g_frames != i_frames:
            invalid.append("GratingID")
        if a_frames != i_frames:
            invalid.append("Angle")
        if t_frames != i_frames:
            invalid.append("Timestamp")
        if w_frames is not None and w_frames != i_frames:
            invalid.append("Wavelength")

        if len(invalid) > 0:
            names = ", ".join(invalid)
            raise ValueError(f"{names} and Image shapes are incompatible")

    @property
    def band_type(self) -> Bandtype:
        if self["GratingID"] is None and self["Wavelength"] is None:  # type: ignore
            return Bandtype.Broadband
        if self["GratingID"] is not None and self["Wavelength"] is not None:  # type: ignore
            return Bandtype.Bandpass

        raise ValueError("invalid band type state")


def load_spectral_cube(file: h5py.File):
    root = file[ROOT_NAME]
