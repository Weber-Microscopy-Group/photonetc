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
    "CameraDynamicPropertiesAttrs", {"ROI Mode": CameraRoiMode}
)

@dataclass
class CameraDynamicProperties:
    attrs: CameraDynamicPropertiesAttrs

class CameraAxis0Attrs(TypedDict):
    Name: str

@dataclass
class CameraAxis0:
    attrs: CameraAxis0Attrs

class CameraAxis1Attrs(TypedDict):
    Coefs: Annotated[NDArrayF64, Literal[2]]
    Decimals: Annotated[NDArrayI32, Literal[1]]
    Name: str
    Unit: str

@dataclass
class CameraAxis1:
    attrs: CameraAxis1Attrs

class CameraAxisAttrs(TypedDict):
    Coefs: Annotated[NDArrayF64, Literal[2]]
    Decimals: Annotated[NDArrayI32, Literal[1]]
    Name: str
    Unit: str

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
    AveragingMode: CameraAveragingMode
    Binning: Annotated[NDArrayF64, Literal[2]]
    BitDepth: Annotated[NDArrayI32, Literal[1]]
    CaptorSize: Annotated[NDArrayI32, Literal[2]]
    CoolerSetPoint: str
    DetectorMode: CameraDetectorMode
    GradientOrientation: Annotated[NDArrayI32, Literal[1]]
    Model: str
    Name: str
    Orientation: Annotated[NDArrayI32, Literal[1]]
    PixelSizeNm: Annotated[NDArrayF64, Literal[1]]
    ReadoutSpeed: str
    RoiSize: Annotated[NDArrayI32, Literal[2]]
    RoiStart: Annotated[NDArrayI32, Literal[2]]
    Shutter: CameraShutter
    SN: str
    Temperature: str
    Trigger: CameraTrigger
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
    User: str

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
    BeamSide: str
    FWHM: Annotated[NDArrayF64, Literal[1]]
    MaxWavelength: Annotated[NDArrayF64, Literal[1]]
    MinWavelength: Annotated[NDArrayF64, Literal[1]]
    Name: str
    Type: GratingType

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
    Name: str
    Type: str

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
    @overload
    def __getitem__(self, key: Literal["9"]) -> GratingSlot | GratingSlotEmpty: ...

class OpticsAttrs(TypedDict):
    FocusStatus: Annotated[NDArrayI32, Literal[1]]
    Objective: str

@dataclass
class Optics:
    attrs: OpticsAttrs

class SystemType(StrEnum):
    SYSTEM = "System"

class SystemAttrs(TypedDict):
    SN: str
    SoftwareVersion: str
    Type: SystemType

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
    Intensity: NDArrayF64
    Mode: NDArrayStr
    Source: IlluminationState

@dataclass
class MiscIllumination:
    attrs: MiscIlluminationAttrs

MiscItems = TypedDict(
    "MiscItems",
    {
        "Illumination": MiscIllumination,
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
    Key: NDArrayStr

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
    AcqMode: NDArrayStr
    CreationDate: NDArrayStr
    Name: NDArrayStr
    Type: NDArrayStr
    BroadBand: NDArrayI32 | None
    FixedTimeExposure: NDArrayI32 | None
    LaserNm: NDArrayF64 | None
    LowerWavelength: NDArrayF64 | None
    UpperWavelength: NDArrayF64 | None
    WavelengthStep: NDArrayF64 | None

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
