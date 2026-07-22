"""Shared info between temporal and spectral cubes."""

from typing import Union
from dataclasses import dataclass, field
import numpy as np


@dataclass
class CameraAxis0:
    Name: str


@dataclass
class CameraAxis1:
    Coefs: np.ndarray
    Decimals: np.ndarray
    Name: str
    Unit: str


@dataclass
class CameraAxis:
    axis_0: CameraAxis0
    axis_1: CameraAxis1
    Coefs: np.ndarray
    Decimals: np.ndarray
    Name: str
    Unit: str


@dataclass
class CameraDynamicProperties:
    ROIMode: str


@dataclass
class Camera:
    XAxis: CameraAxis
    YAxis: CameraAxis
    BitDepth: np.ndarray
    CaptorSize: np.ndarray
    CoolerSetPoint: str
    DetectorMode: str
    GradientOrientation: np.ndarray
    Model: str
    Name: str
    PixelSizeNm: np.ndarray
    ReadoutSpeed: str
    RoiSize: np.ndarray
    SN: str
    Temperature: np.ndarray
    VerticalFlip: np.ndarray = field(
        default_factory=lambda: np.zeros(
            1,
        )
    )
    AveragingMode: str = "None"
    Binning: np.ndarray = field(default_factory=lambda: np.ones((2,)))
    Orientation: np.ndarray = field(default_factory=lambda: np.zeros((1,)))
    RoiStart: np.ndarray = field(
        default_factory=lambda: np.zeros(
            2,
        )
    )
    Shutter: str = "Auto/None"
    Trigger: str = "None"


@dataclass
class GratingSlotCalibration:
    Curve: np.ndarray
    Factor: np.ndarray
    FocalLengthCoef: np.ndarray
    FocalLengthUm: np.ndarray
    Offset: np.ndarray
    Period: np.ndarray
    Slope: np.ndarray
    StageOffset: np.ndarray
    Temperature: np.ndarray
    User: str = "Photon Etc."


@dataclass
class GratingSlotRegistration:
    Scaling_X: np.ndarray
    Scaling_Y: np.ndarray
    Translation_X: np.ndarray
    Translation_Y: np.ndarray


@dataclass
class GratingSlot:
    Calibration: GratingSlotCalibration
    Registration: list[GratingSlotRegistration] = field(default_factory=list)


@dataclass
class GratingSlotEmpty:
    FWHM: np.ndarray
    MaxWavelength: np.ndarray
    MinWavelength: np.ndarray
    Name: str
    Type: str = "Static Filter"


class Grating:
    def init(self, gratings: list[Union[GratingSlot, GratingSlotEmpty]] = []):
        self.gratings = gratings


@dataclass
class Optics:
    FocusStatus: np.ndarray
    Objective: str


@dataclass
class System:
    SN: str
    SoftwareVersion: str
    Type: str = "System"


@dataclass
class MiscZStage:
    Position: np.ndarray = field(default_factory=lambda: np.zeros((1,)))
