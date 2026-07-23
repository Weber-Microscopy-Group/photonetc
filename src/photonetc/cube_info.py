"""Shared info between temporal and spectral cubes."""

from typing import Union, TYPE_CHECKING
from dataclasses import dataclass, field
import numpy as np

if TYPE_CHECKING:
    import h5py


@dataclass
class CameraAxis0:
    Name: str

    def to_h5(self, group: h5py.Group):
        group.attrs["Name"] = self.Name


@dataclass
class CameraAxis1:
    Coefs: np.ndarray
    Decimals: np.ndarray
    Name: str
    Unit: str

    def to_h5(self, group: h5py.Group):
        group.attrs["Coefs"] = self.Coefs
        group.attrs["Decimals"] = self.Decimals
        group.attrs["Name"] = self.Name
        group.attrs["Unit"] = self.Unit


@dataclass
class CameraAxis:
    axis_0: CameraAxis0
    axis_1: CameraAxis1
    Coefs: np.ndarray
    Decimals: np.ndarray
    Name: str
    Unit: str

    def to_h5(self, group: h5py.Group):
        axis_0 = group.create_group("0")
        axis_1 = group.create_group("1")
        self.axis_0.to_h5(axis_0)
        self.axis_1.to_h5(axis_1)

        group.attrs["Coefs"] = self.Coefs
        group.attrs["Decimals"] = self.Decimals
        group.attrs["Name"] = self.Name
        group.attrs["Unit"] = self.Unit


@dataclass
class CameraDynamicProperties:
    ROIMode: str

    def to_h5(self, group: h5py.Group):
        group.attrs["ROI Mode"] = self.ROIMode


@dataclass
class Camera:
    XAxis: CameraAxis
    YAxis: CameraAxis
    DynamicProperties: CameraDynamicProperties
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

    def to_h5(self, group: h5py.Dataset):
        group.attrs["XAxis"] = self.XAxis
        group.attrs["YAxis"] = self.YAxis
        group.attrs["DynamicProperties"] = self.DynamicProperties
        group.attrs["BitDepth"] = self.BitDepth
        group.attrs["CaptorSize"] = self.CaptorSize
        group.attrs["CoolerSetPoint"] = self.CoolerSetPoint
        group.attrs["DetectorMode"] = self.DetectorMode
        group.attrs["GradientOrientation"] = self.GradientOrientation
        group.attrs["Model"] = self.Model
        group.attrs["Name"] = self.Name
        group.attrs["PixelSizeNm"] = self.PixelSizeNm
        group.attrs["ReadoutSpeed"] = self.ReadoutSpeed
        group.attrs["RoiSize"] = self.RoiSize
        group.attrs["SN"] = self.SN
        group.attrs["Temperature"] = self.Temperature
        group.attrs["VerticalFlip"] = self.VerticalFlip
        group.attrs["AveragingMode"] = self.AveragingMode
        group.attrs["Binning"] = self.Binning
        group.attrs["Orientation"] = self.Orientation
        group.attrs["RoiStart"] = self.RoiStart
        group.attrs["Shutter"] = self.Shutter
        group.attrs["Trigger"] = self.Trigger


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

    def to_h5(self, group: h5py.Group):
        group.attrs["Curve"] = self.Curve
        group.attrs["Factor"] = self.Factor
        group.attrs["FocalLengthCoef"] = self.FocalLengthCoef
        group.attrs["FocalLengthUm"] = self.FocalLengthUm
        group.attrs["Offset"] = self.Offset
        group.attrs["Period"] = self.Period
        group.attrs["Slope"] = self.Slope
        group.attrs["StageOffset"] = self.StageOffset
        group.attrs["Temperature"] = self.Temperature
        group.attrs["User"] = self.User


@dataclass
class GratingSlotRegistration:
    Scaling_X: np.ndarray
    Scaling_Y: np.ndarray
    Translation_X: np.ndarray
    Translation_Y: np.ndarray

    def to_h5(self, group: h5py.Group):
        group.attrs["Scaling_X"] = self.Scaling_X
        group.attrs["Scaling_Y"] = self.Scaling_Y
        group.attrs["Translation_X"] = self.Translation_X
        group.attrs["Translation_Y"] = self.Translation_Y


@dataclass
class GratingSlot:
    Calibration: GratingSlotCalibration
    BeamSide: str
    FWHM: np.ndarray
    MaxWavelength: np.ndarray
    MinWavelength: np.ndarray
    Name: str
    Type: str
    Registration: dict[str, GratingSlotRegistration] = field(default_factory=dict)

    def to_h5(self, group: h5py.Group):
        group.attrs["Calibration"] = self.Calibration
        group.attrs["BeamSide"] = self.BeamSide
        group.attrs["FWHM"] = self.FWHM
        group.attrs["MaxWavelength"] = self.MaxWavelength
        group.attrs["MinWavelength"] = self.MinWavelength
        group.attrs["Name"] = self.Name
        group.attrs["Type"] = self.Type
        group.attrs["Registration"] = self.Registration


@dataclass
class GratingSlotEmpty:
    FWHM: np.ndarray
    MaxWavelength: np.ndarray
    MinWavelength: np.ndarray
    Name: str
    Type: str = "Static Filter"

    def to_h5(self, group: h5py.Group):
        group.attrs["FWHM"] = self.FWHM
        group.attrs["MaxWavelength"] = self.MaxWavelength
        group.attrs["MinWavelength"] = self.MinWavelength
        group.attrs["Name"] = self.Name
        group.attrs["Type"] = self.Type


class Grating:
    def __init__(self, gratings: dict[str, Union[GratingSlot, GratingSlotEmpty]] = {}):
        self.gratings = gratings

    def to_h5(self, group: h5py.Group):
        for key, grating in self.gratings.items():
            grp = group.create_group(key)
            grating.to_h5(grp)


@dataclass
class Optics:
    FocusStatus: np.ndarray
    Objective: str

    def to_h5(self, group: h5py.Group):
        group.attrs["FocusState"] = self.FocusStatus
        group.attrs["Objective"] = self.Objective


@dataclass
class System:
    SN: str
    SoftwareVersion: str
    Type: str = "System"

    def to_h5(self, group: h5py.Group):
        group.attrs["SN"] = self.SN
        group.attrs["SoftwareVersion"] = self.SoftwareVersion
        group.attrs["Type"] = self.Type


@dataclass
class MiscZStage:
    Position: np.ndarray = field(default_factory=lambda: np.zeros((1,)))

    def to_h5(self, group: h5py.Group):
        group.attrs["Position"] = self.Position
