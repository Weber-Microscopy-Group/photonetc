"""A temporally resolved data cube."""

from dataclasses import dataclass, field
import numpy as np
import datetime as dt
from .cube_info import Camera, Grating, Optics, System, MiscZStage


@dataclass
class InfoCube:
    AcqMode: str
    Broadband: np.ndarray
    Name: str
    Type: str
    CreationDate: str = field(
        default_factory=lambda: dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    )


@dataclass
class InfoMiscIllumination:
    Intensity: np.ndarray
    Mode: str
    Source: str


@dataclass
class InfoMisc:
    Illumination: InfoMiscIllumination
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
class TemporalCube:
    Angle: np.ndarray
    Images: np.ndarray
    Info: Info
    TimeExposure: np.ndarray
    Timestamp: np.ndarray
