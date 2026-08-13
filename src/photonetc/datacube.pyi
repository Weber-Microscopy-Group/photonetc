from abc import ABC
from enum import Enum
from typing import Any, Literal, TypeAlias, TypedDict, overload

import h5py
import numpy as np

from . import info

NDArrayF64: TypeAlias = np.typing.NDArray[np.float64]
NDArrayI32: TypeAlias = np.typing.NDArray[np.int32]
NDArrayStr: TypeAlias = np.typing.NDArray[np.str_]

class DatacubeItems(TypedDict):
    Images: NDArrayF64
    Info: info.Info
    TimeExposure: NDArrayF64

class Datacube(ABC):
    _items: Any
    elapsed: NDArrayF64

    @overload
    def __getitem__(self, key: Literal["Images"]) -> NDArrayF64: ...
    @overload
    def __getitem__(self, key: Literal["Info"]) -> info.Info: ...
    @overload
    def __getitem__(self, key: Literal["TimeExposure"]) -> NDArrayF64: ...
    @classmethod
    def from_file(cls, f: h5py.File) -> Datacube: ...

class SpectralCubeItems(DatacubeItems):
    GratingID: NDArrayI32
    Translation_X: NDArrayF64
    Translation_Y: NDArrayF64
    Wavelength: NDArrayF64

class SpectralCube(Datacube):
    def __init__(self, _items: SpectralCubeItems): ...
    @overload
    def __getitem__(self, key: Literal["Images"]) -> NDArrayF64: ...
    @overload
    def __getitem__(self, key: Literal["Info"]) -> info.Info: ...
    @overload
    def __getitem__(self, key: Literal["TimeExposure"]) -> NDArrayF64: ...
    @overload
    def __getitem__(self, key: Literal["GratingID"]) -> NDArrayI32: ...
    @overload
    def __getitem__(self, key: Literal["Translation_X"]) -> NDArrayF64: ...
    @overload
    def __getitem__(self, key: Literal["Translation_Y"]) -> NDArrayF64: ...
    @overload
    def __getitem__(self, key: Literal["Wavelength"]) -> NDArrayF64: ...
    @classmethod
    def from_file(cls, f: h5py.File) -> SpectralCube: ...

class Bandtype(Enum):
    Broadband = 0
    Bandpass = 1

class TemporalCubeItems(DatacubeItems):
    Angle: NDArrayF64
    GratingID: NDArrayI32 | None
    Timestamp: NDArrayStr
    Wavelength: NDArrayF64 | None

class TemporalCube(Datacube):
    def __init__(self, _items: TemporalCubeItems): ...
    @overload
    def __getitem__(self, key: Literal["Images"]) -> NDArrayF64: ...
    @overload
    def __getitem__(self, key: Literal["Info"]) -> info.Info: ...
    @overload
    def __getitem__(self, key: Literal["TimeExposure"]) -> NDArrayF64: ...
    @overload
    def __getitem__(self, key: Literal["Angle"]) -> NDArrayF64: ...
    @overload
    def __getitem__(self, key: Literal["GratingID"]) -> NDArrayI32 | None: ...
    @overload
    def __getitem__(self, key: Literal["Timestamp"]) -> NDArrayStr: ...
    @overload
    def __getitem__(self, key: Literal["Wavelength"]) -> NDArrayF64 | None: ...
    @classmethod
    def from_file(cls, f: h5py.File) -> TemporalCube: ...
    def band_type(self) -> Bandtype: ...
