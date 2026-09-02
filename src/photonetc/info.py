"""Cube info. i.e. Things inside cube["Cube"]["Info"]."""

from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, Literal, TypeAlias, TypedDict

import h5py
import numpy as np

from .meta import Group, group

NDArrayF64: TypeAlias = np.typing.NDArray[np.float64]
NDArrayI32: TypeAlias = np.typing.NDArray[np.int32]
NDArrayStr: TypeAlias = np.typing.NDArray[np.str_]


class CameraRoiMode(StrEnum):
    SOFTWARE = "Software"
    HARDWARE = "Hardware"


CameraDynamicPropertiesAttrs = TypedDict(
    "CameraDynamicPropertiesAttrs", {"ROI Mode": Annotated[NDArrayStr, Literal[1]]}
)


@dataclass
class CameraDynamicProperties(Group):
    attrs: CameraDynamicPropertiesAttrs


class CameraAxis0Attrs(TypedDict):
    Name: Annotated[NDArrayStr, Literal[1]]


@dataclass
class CameraAxis0(Group):
    attrs: CameraAxis0Attrs


class CameraAxis1Attrs(TypedDict):
    Coefs: Annotated[NDArrayF64, Literal[2]]
    Decimals: Annotated[NDArrayI32, Literal[1]]
    Name: Annotated[NDArrayStr, Literal[1]]
    Unit: Annotated[NDArrayStr, Literal[1]]


@dataclass
class CameraAxis1(Group):
    attrs: CameraAxis1Attrs


class CameraAxisAttrs(TypedDict):
    Coefs: Annotated[NDArrayF64, Literal[2]]
    Decimals: Annotated[NDArrayI32, Literal[1]]
    Name: Annotated[NDArrayStr, Literal[1]]
    Unit: Annotated[NDArrayStr, Literal[1]]


CameraAxisItems = TypedDict("CameraAxisItems", {"0": CameraAxis0, "1": CameraAxis1})


@group
class CameraAxis(Group):
    attrs: CameraAxisAttrs
    _items: CameraAxisItems


class CameraDetectorMode(StrEnum):
    CONVENTIONAL = "Conventional"


class CameraAveragingMode(StrEnum):
    NONE = "None"


class CameraShutter(StrEnum):
    AUTO_NONE = "Auto/None"


class CameraTrigger(StrEnum):
    NONE = "None"


class CameraAttrs(TypedDict):
    AveragingMode: Annotated[NDArrayStr, Literal[1]]
    Binning: Annotated[NDArrayF64, Literal[2]]
    BitDepth: Annotated[NDArrayI32, Literal[1]]
    CaptorSize: Annotated[NDArrayI32, Literal[2]]
    CoolerSetPoint: Annotated[NDArrayStr, Literal[1]]
    DetectorMode: Annotated[NDArrayStr, Literal[1]]
    GradientOrientation: Annotated[NDArrayI32, Literal[1]]
    Model: Annotated[NDArrayStr, Literal[1]]
    Name: Annotated[NDArrayStr, Literal[1]]
    Orientation: Annotated[NDArrayI32, Literal[1]]
    PixelSizeNm: Annotated[NDArrayF64, Literal[1]]
    ReadoutSpeed: Annotated[NDArrayStr, Literal[1]]
    RoiSize: Annotated[NDArrayI32, Literal[2]]
    RoiStart: Annotated[NDArrayI32, Literal[2]]
    Shutter: Annotated[NDArrayStr, Literal[1]]
    SN: Annotated[NDArrayStr, Literal[1]]
    Temperature: Annotated[NDArrayStr, Literal[1]]
    Trigger: Annotated[NDArrayStr, Literal[1]]
    VerticalFlip: Annotated[NDArrayI32, Literal[1]]


class CameraItems(TypedDict):
    XAxis: CameraAxis
    YAxis: CameraAxis
    DynamicProperties: CameraDynamicProperties


@group
class Camera(Group):
    attrs: CameraAttrs
    _items: CameraItems


class GratingSlotCalibrationAttrs(TypedDict):
    Curve: Annotated[NDArrayF64, Literal[1]]
    Factor: Annotated[NDArrayF64, Literal[1]]
    FocalLengthCoef: Annotated[NDArrayF64, Literal[1]]
    FocalLengthUm: Annotated[NDArrayF64, Literal[1]]
    Offset: Annotated[NDArrayF64, Literal[1]]
    Period: Annotated[NDArrayF64, Literal[1]]
    Slope: Annotated[NDArrayF64, Literal[1]]
    StageOffset: Annotated[NDArrayF64, Literal[1]]
    Temperature: Annotated[NDArrayF64, Literal[1]]
    User: Annotated[NDArrayStr, Literal[1]]


@dataclass
class GratingSlotCalibration(Group):
    attrs: GratingSlotCalibrationAttrs


class GratingSlotRegistrationAttrs(TypedDict):
    Scaling_X: Annotated[NDArrayF64, Literal[5]]
    Scaling_Y: Annotated[NDArrayF64, Literal[5]]
    Translation_X: Annotated[NDArrayF64, Literal[5]]
    Translation_Y: Annotated[NDArrayF64, Literal[5]]


@dataclass
class GratingSlotRegistration(Group):
    attrs: GratingSlotRegistrationAttrs


class GratingType(StrEnum):
    TRANSMISSION = "Transmission"
    STATIC = "Static Filter"


class GratingBeamSide(StrEnum):
    RIGHT = "Right"
    LEFT = "Left"


class GratingSlotAttrs(TypedDict):
    BeamSide: Annotated[NDArrayStr, Literal[1]]
    FWHM: Annotated[NDArrayF64, Literal[1]]
    MaxWavelength: Annotated[NDArrayF64, Literal[1]]
    MinWavelength: Annotated[NDArrayF64, Literal[1]]
    Name: Annotated[NDArrayStr, Literal[1]]
    Type: Annotated[NDArrayStr, Literal[1]]


class GratingSlotItems(TypedDict):
    Calibration: GratingSlotCalibration
    Registration: dict[str, GratingSlotRegistration]


@group
class GratingSlot:
    attrs: GratingSlotAttrs
    _items: GratingSlotItems

    @classmethod
    def from_group(cls: type, group: h5py.Group, path: str = ""):
        attrs = {key: val for key, val in group.attrs.items()}
        calibration = GratingSlotCalibration.from_group(
            group["Calibration"],  # type: ignore
            f"{path}/Calibration",
        )

        registration = {}
        for key, reg in group["Registration"].items():  # type: ignore
            registration[key] = GratingSlotRegistration.from_group(
                reg, f"{path}/Registration"
            )

        return cls(attrs, {"Calibration": calibration, "Registration": registration})


class GratingSlotEmptyAttrs(TypedDict):
    FWHM: Annotated[NDArrayF64, Literal[1]]
    MaxWavelength: Annotated[NDArrayF64, Literal[1]]
    MinWavelength: Annotated[NDArrayF64, Literal[1]]
    Name: Annotated[NDArrayStr, Literal[1]]
    Type: Annotated[NDArrayStr, Literal[1]]


@dataclass
class GratingSlotEmpty(Group):
    attrs: GratingSlotEmptyAttrs


GratingItems = TypedDict(
    "GratingItems",
    {
        "0": GratingSlot | GratingSlotEmpty,
        "1": GratingSlot | GratingSlotEmpty,
        "2": GratingSlot | GratingSlotEmpty,
        "3": GratingSlot | GratingSlotEmpty,
        "4": GratingSlot | GratingSlotEmpty,
        "5": GratingSlot | GratingSlotEmpty,
        "6": GratingSlot | GratingSlotEmpty,
        "7": GratingSlot | GratingSlotEmpty,
        "8": GratingSlot | GratingSlotEmpty,
    },
)


@group
class Grating:
    _items: GratingItems

    @classmethod
    def from_group(cls: type, group: h5py.Group, path: str = ""):
        slots = {}
        for key, slot in group.items():
            spath = path + f"/{key}"
            if "Calibration" in slot and "Registration" in slot:
                slots[key] = GratingSlot.from_group(slot, spath)
            elif "Calibration" not in slot and "Registration" not in slot:
                slots[key] = GratingSlotEmpty.from_group(slot, spath)
            else:
                raise ValueError(f"unknown grating slot state at {spath}")

        return cls(slots)


class OpticsAttrs(TypedDict):
    FocusStatus: Annotated[NDArrayI32, Literal[1]]
    Objective: Annotated[NDArrayStr, Literal[1]]


@dataclass
class Optics(Group):
    attrs: OpticsAttrs


class SystemType(StrEnum):
    SYSTEM = "System"


class SystemAttrs(TypedDict):
    SN: Annotated[NDArrayStr, Literal[1]]
    SoftwareVersion: Annotated[NDArrayStr, Literal[1]]
    Type: Annotated[NDArrayStr, Literal[1]]


@dataclass
class System(Group):
    attrs: SystemAttrs


class MiscZStageAttrs(TypedDict):
    Position: Annotated[NDArrayF64, Literal[1]]


@dataclass
class MiscZStage(Group):
    attrs: MiscZStageAttrs


class IlluminationState(StrEnum):
    ENABLED = "Enabled"
    DISABLED = "Disabled"


class MiscIlluminationAttrs(TypedDict):
    Intensity: Annotated[NDArrayF64, Literal[1]]
    Mode: Annotated[NDArrayStr, Literal[1]]
    Source: Annotated[IlluminationState, Literal[1]]


@dataclass
class MiscIllumination(Group):
    attrs: MiscIlluminationAttrs


MiscItems = TypedDict(
    "MiscItems",
    {
        "Illumination": MiscIllumination | None,
        "Z-Stage": MiscZStage,
    },
)


@group
class Misc(Group):
    _items: MiscItems


class CubeZAxisKey(StrEnum):
    INDEX = "Index"


class CubeZAxisAttrs(TypedDict):
    Key: Annotated[NDArrayStr, Literal[1]]


@dataclass
class CubeZAxis(Group):
    attrs: CubeZAxisAttrs


class CubeItems(TypedDict):
    ZAxis: CubeZAxis | None


class CubeAcqMode(StrEnum):
    HYPERSPECTRAL = "Hyperspectral Acquisition"
    VIDEO = "Video Record"


class CubeDatatype(StrEnum):
    I16 = "INT-16"


class CubeAttrs(TypedDict):
    AcqMode: Annotated[NDArrayStr, Literal[1]]
    CreationDate: Annotated[NDArrayStr, Literal[1]]
    Name: Annotated[NDArrayStr, Literal[1]]
    Type: Annotated[NDArrayStr, Literal[1]]
    BroadBand: Annotated[NDArrayI32, Literal[1]] | None
    FixedTimeExposure: Annotated[NDArrayI32, Literal[1]] | None
    LaserNm: Annotated[NDArrayF64, Literal[1]] | None
    LowerWavelength: Annotated[NDArrayF64, Literal[1]] | None
    UpperWavelength: Annotated[NDArrayF64, Literal[1]] | None
    WavelengthStep: Annotated[NDArrayF64, Literal[1]] | None


@group
class Cube(Group):
    attrs: CubeAttrs
    _items: CubeItems


class InfoItems(TypedDict):
    Camera: Camera
    Cube: Cube
    Grating: Grating
    Misc: Misc
    Optics: Optics
    System: System


@group
class Info(Group):
    _items: InfoItems
