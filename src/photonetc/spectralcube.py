"""A spectrally resolved data cube."""

from dataclasses import dataclass, field
import numpy as np
from .cube_info import MiscZStage, System, Optics, Grating, Camera
import datetime as dt


@dataclass
class InfoCube:
    AcqMode: str
    LowerWavelength: np.ndarray
    Name: str
    Type: str
    UpperWavelength: np.ndarray
    WavelengthStep: np.ndarray
    CreationDate: str = field(
        default_factory=lambda: dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    )
    FixedTimeExposure: np.ndarray = field(default_factory=lambda: np.ones((1,)))


@dataclass
class InfoMisc:
    ZStage: MiscZStage = field(default_factory=MiscZStage)


@dataclass
class Info:
    Camera: Camera
    Cube: InfoCube
    Grating: Grating
    Misc: InfoMisc
    Optics: Optics
    System: System


@dataclass
class SpectralCube:
    GratingId: np.ndarray
    Images: np.ndarray
    Info: Info
    TimeExposure: np.ndarray
    Translation_X: np.ndarray
    Translation_Y: np.ndarray
    Wavelength: np.ndarray
