from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, Literal, TypeAlias, TypedDict, overload

import numpy as np

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
class CameraDynamicProperties:
    attrs: CameraDynamicPropertiesAttrs

class CameraAxis0Attrs(TypedDict):
    Name: Annotated[NDArrayStr, Literal[1]]

@dataclass
class CameraAxis0:
    attrs: CameraAxis0Attrs

class CameraAxis1Attrs(TypedDict):
    Coefs: Annotated[NDArrayF64, Literal[2]]
    Decimals: Annotated[NDArrayI32, Literal[1]]
    Name: Annotated[NDArrayStr, Literal[1]]
    Unit: Annotated[NDArrayStr, Literal[1]]

@dataclass
class CameraAxis1:
    attrs: CameraAxis1Attrs

class CameraAxisAttrs(TypedDict):
    Coefs: Annotated[NDArrayF64, Literal[2]]
    Decimals: Annotated[NDArrayI32, Literal[1]]
    Name: Annotated[NDArrayStr, Literal[1]]
    Unit: Annotated[NDArrayStr, Literal[1]]

CameraAxisItems = TypedDict("CameraAxisItems", {"0": CameraAxis0, "1": CameraAxis1})

class CameraAxis:
    attrs: CameraAxisAttrs

    def __init__(self, attrs: CameraAxisAttrs, _items: CameraAxisItems): ...
    @overload
    def __getitem__(self, key: Literal["0"]) -> CameraAxis0: ...
    @overload
    def __getitem__(self, key: Literal["1"]) -> CameraAxis1: ...

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

class Camera:
    attrs: CameraAttrs

    def __init__(self, attrs: CameraAttrs, _items: CameraItems): ...
    @overload
    def __getitem__(self, key: Literal["XAxis"]) -> CameraAxis: ...
    @overload
    def __getitem__(self, key: Literal["YAxis"]) -> CameraAxis: ...
    @overload
    def __getitem__(
        self, key: Literal["DynamicProperties"]
    ) -> CameraDynamicProperties: ...

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
class GratingSlotCalibration:
    attrs: GratingSlotCalibrationAttrs

class GratingSlotRegistrationAttrs(TypedDict):
    Scaling_X: Annotated[NDArrayF64, Literal[5]]
    Scaling_Y: Annotated[NDArrayF64, Literal[5]]
    Translation_X: Annotated[NDArrayF64, Literal[5]]
    Translation_Y: Annotated[NDArrayF64, Literal[5]]

@dataclass
class GratingSlotRegistration:
    attrs: GratingSlotRegistrationAttrs

class GratingType(StrEnum):
    TRANSMISSION = "Transmission"
    STATIC = "Static Filter"

class GratingBeamSide(StrEnum):
    RIGHT = "Right"

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

class GratingSlot:
    attrs: GratingSlotAttrs

    def __init__(self, attrs: GratingSlotAttrs, _items: GratingSlotItems): ...
    @overload
    def __getitem__(self, key: Literal["Calibration"]) -> GratingSlotCalibration: ...
    @overload
    def __getitem__(self, key: Literal["Registration"]) -> GratingSlotRegistration: ...

class GratingSlotEmptyAttrs(TypedDict):
    FWHM: Annotated[NDArrayF64, Literal[1]]
    MaxWavelength: Annotated[NDArrayF64, Literal[1]]
    MinWavelength: Annotated[NDArrayF64, Literal[1]]
    Name: Annotated[NDArrayStr, Literal[1]]
    Type: Annotated[NDArrayStr, Literal[1]]

@dataclass
class GratingSlotEmpty:
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

class Grating:
    def __init__(self, _items: GratingItems): ...
    @overload
    def __getitem__(self, key: Literal["0"]) -> GratingSlot | GratingSlotEmpty: ...
    @overload
    def __getitem__(self, key: Literal["1"]) -> GratingSlot | GratingSlotEmpty: ...
    @overload
    def __getitem__(self, key: Literal["2"]) -> GratingSlot | GratingSlotEmpty: ...
    @overload
    def __getitem__(self, key: Literal["3"]) -> GratingSlot | GratingSlotEmpty: ...
    @overload
    def __getitem__(self, key: Literal["4"]) -> GratingSlot | GratingSlotEmpty: ...
    @overload
    def __getitem__(self, key: Literal["5"]) -> GratingSlot | GratingSlotEmpty: ...
    @overload
    def __getitem__(self, key: Literal["6"]) -> GratingSlot | GratingSlotEmpty: ...
    @overload
    def __getitem__(self, key: Literal["7"]) -> GratingSlot | GratingSlotEmpty: ...
    @overload
    def __getitem__(self, key: Literal["8"]) -> GratingSlot | GratingSlotEmpty: ...

class OpticsAttrs(TypedDict):
    FocusStatus: Annotated[NDArrayI32, Literal[1]]
    Objective: Annotated[NDArrayStr, Literal[1]]

@dataclass
class Optics:
    attrs: OpticsAttrs

class SystemType(StrEnum):
    SYSTEM = "System"

class SystemAttrs(TypedDict):
    SN: Annotated[NDArrayStr, Literal[1]]
    SoftwareVersion: Annotated[NDArrayStr, Literal[1]]
    Type: Annotated[NDArrayStr, Literal[1]]

@dataclass
class System:
    attrs: SystemAttrs

class MiscZStageAttrs(TypedDict):
    Position: Annotated[NDArrayF64, Literal[1]]

@dataclass
class MiscZStage:
    attrs: MiscZStageAttrs

class IlluminationState(StrEnum):
    ENABLED = "Enabled"
    DISABLED = "Disabled"

class MiscIlluminationAttrs(TypedDict):
    Intensity: Annotated[NDArrayF64, Literal[1]]
    Mode: Annotated[NDArrayStr, Literal[1]]
    Source: Annotated[IlluminationState, Literal[1]]

@dataclass
class MiscIllumination:
    attrs: MiscIlluminationAttrs

MiscItems = TypedDict(
    "MiscItems",
    {
        "Illumination": MiscIllumination | None,
        "Z-Stage": MiscZStage,
    },
)

class Misc:
    def __init__(self, _items: MiscItems): ...
    @overload
    def __getitem__(self, key: Literal["Illumination"]) -> MiscIllumination: ...
    @overload
    def __getitem__(self, key: Literal["Z-Stage"]) -> MiscZStage: ...

class CubeZAxisKey(StrEnum):
    INDEX = "Index"

class CubeZAxisAttrs(TypedDict):
    Key: Annotated[NDArrayStr, Literal[1]]

@dataclass
class CubeZAxis:
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

class Cube:
    attrs: CubeAttrs

    def __init__(self, attrs: CubeAttrs, _items: CubeItems): ...
    def __getitem__(self, key: Literal["ZAxis"]) -> CubeZAxis: ...

class InfoItems(TypedDict):
    Camera: Camera
    Cube: Cube
    Grating: Grating
    Misc: Misc
    Optics: Optics
    System: System

class Info:
    def __init__(self, _items: InfoItems): ...
    @overload
    def __getitem__(self, key: Literal["Camera"]) -> Camera: ...
    @overload
    def __getitem__(self, key: Literal["Grating"]) -> Grating: ...
    @overload
    def __getitem__(self, key: Literal["Optics"]) -> Optics: ...
    @overload
    def __getitem__(self, key: Literal["System"]) -> System: ...
    @overload
    def __getitem__(self, key: Literal["Cube"]) -> Cube: ...
    @overload
    def __getitem__(self, key: Literal["Misc"]) -> Misc: ...
