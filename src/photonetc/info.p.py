"""Cube info. i.e. Things inside cube["Cube"]["Info"]."""

import datetime as dt
from dataclasses import dataclass, field

import numpy as np

from .meta import Group, attribute, attribute_list, field, group


@attribute_list
class CameraDynamicPropertiesAttrs:
    roi_mode: str = attribute("ROI Mode")


@dataclass
class CameraDynamicProperties(Group):
    attrs: CameraDynamicPropertiesAttrs


@attribute_list
class CameraAxis0Attrs:
    name: str = attribute("Name")


@dataclass
class CameraAxis0(Group):
    attrs: CameraAxis0Attrs


@attribute_list
class CameraAxis1Attrs:
    coefs: np.ndarray = attribute("Coefs")
    decimals: np.ndarray = attribute("Decimals")
    name: str = attribute("Name")
    unit: str = attribute("Unit")


class CameraAxis1(Group):
    attrs: CameraAxis1Attrs


@attribute_list
class CameraAxisAttrs:
    coefs: np.ndarray = attribute("Coefs")
    decimals: np.ndarray = attribute("Decimals")
    name: str = attribute("Name")
    unit: str = attribute("Unit")


@group
class CameraAxis(Group):
    attrs: CameraAxisAttrs
    axis_0: CameraAxis0 = field("0")
    axis_1: CameraAxis1 = field("1")


@attribute_list
class CameraAttrs:
    bit_depth: np.ndarray = attribute("BitDepth")
    captor_size: np.ndarray = attribute("CaptorSize")
    cooler_set_point: str = attribute("CoolerSetPoint")
    detector_mode: str = attribute("DetectorMode")
    gradient_orientation: np.ndarray = attribute("GradientOrientation")
    model: str = attribute("Model")
    name: str = attribute("Name")
    pixel_size_nm: np.ndarray = attribute("PixelSizeNm")
    readout_speed: str = attribute("ReadoutSpeed")
    roi_size: np.ndarray = attribute("RoiSize")
    sn: str = attribute("SN")
    temperature: np.ndarray = attribute("Temperature")
    vertical_flip: np.ndarray = attribute(
        "VerticalFlip",
        default_factory=lambda: np.zeros(
            1,
        ),
    )
    averaging_mode: str = attribute("AveragingMode", "None")
    binning: np.ndarray = attribute("Binning", default_factory=lambda: np.ones((2,)))
    orientation: np.ndarray = attribute(
        "Orientation", default_factory=lambda: np.zeros((1,))
    )
    roi_start: np.ndarray = attribute(
        "RoiStart",
        default_factory=lambda: np.zeros(
            2,
        ),
    )
    shutter: str = attribute("Shutter", default="Auto/None")
    trigger: str = attribute("Trigger", default="None")


@dataclass
class Camera:
    attrs: CameraAttrs


@attribute_list
class CubeAttrs:
    acq_mode: str = attribute("AcqMode")
    name: str = attribute("Name")
    type: str = attribute("Type")
    creation_date: str = attribute(
        "CreationDate",
        default_factory=lambda: dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S"),
    )


@dataclass
class Cube(Group):
    attrs: CubeAttrs


@attribute_list
class GratingSlotCalibrationAttrs:
    curve: np.ndarray = attribute("Curve")
    factor: np.ndarray = attribute("Factor")
    focal_length_coef: np.ndarray = attribute("FocalLengthCoef")
    focal_length_um: np.ndarray = attribute("FocalLengthUm")
    offset: np.ndarray = attribute("Offset")
    period: np.ndarray = attribute("Period")
    slope: np.ndarray = attribute("Slope")
    stage_offset: np.ndarray = attribute("StageOffset")
    temperature: np.ndarray = attribute("Temperature")
    user: str = attribute("User", default="Photon Etc.")


class GratingSlotCalibration(Group):
    attrs: GratingSlotCalibrationAttrs


@attribute_list
class GratingSlotRegistrationAttrs:
    scaling_x: np.ndarray = attribute("Scaling_X")
    scaling_y: np.ndarray = attribute("Scaling_Y")
    translation_x: np.ndarray = attribute("Translation_X")
    translation_y: np.ndarray = attribute("Translation_Y")


@dataclass
class GratingSlotRegistration(Group):
    attrs: GratingSlotRegistrationAttrs


@dataclass
class GratingSlot(Group):
    Calibration: GratingSlotCalibration
    BeamSide: str
    FWHM: np.ndarray
    MaxWavelength: np.ndarray
    MinWavelength: np.ndarray
    Name: str
    Type: str
    Registration: dict[str, GratingSlotRegistration] = field(default_factory=dict)


@attribute_list
class GratingSlotEmptyAttrs:
    fwhm: np.ndarray = attribute("FWHM")
    max_wavelength: np.ndarray = attribute("MaxWavelength")
    min_wavelength: np.ndarray = attribute("MinWavelength")
    name: str = attribute("Name")
    type: str = attribute("Type", default="Static Filter")


@dataclass
class GratingSlotEmpty(Group):
    attrs: GratingSlotEmptyAttrs


class Grating(Group):
    def __init__(
        self, gratings: dict[str, GratingSlot | GratingSlotEmpty] | None = None
    ):
        if gratings is None:
            gratings = {}
        self._gratings = gratings

    def __getitem__(self, key: str):
        return self._gratings.get(key)

    def __setitem__(self, key: str, value):
        self._gratings[key] = value


@attribute_list
class OpticsAttrs:
    focus_status: np.ndarray = attribute("FocusStatus")
    objective: str = attribute("Objective")


@dataclass
class Optics(Group):
    attrs: OpticsAttrs


@attribute_list
class SystemAtts:
    SN: str = attribute("SN")
    SoftwareVersion: str = attribute("SoftwareVersion")
    Type: str = attribute("Type", default="System")


@dataclass
class System(Group):
    attrs: SystemAtts


@attribute_list
class MiscIlluminationAttrs:
    intensity: np.ndarray = attribute("Intensity")
    mode: str = attribute("Mode")
    source: str = attribute("Source")


@dataclass
class MiscIllumination:
    attrs: MiscIlluminationAttrs


@attribute_list
class MiscZStageAttrs:
    position: np.ndarray = attribute("Position", default_factory=lambda: np.zeros((1,)))


@dataclass
class MiscZStage(Group):
    attrs: MiscZStageAttrs


@group
class Misc(Group):
    z_stage: MiscZStage = field("Z-Stage")
    illumination: None | MiscIllumination = field("Illumination", default=None)


@group
class Info(Group):
    camera: Camera = field("Camera")
    cube: Cube = field("Cube")
    grating: Grating = field("Grating")
    misc: Misc = field("Misc")
    optics: Optics = field("Optics")
    system: System = field("System")
