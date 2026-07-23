"""Temporally resolved data cube."""

from dataclasses import dataclass, field
import numpy as np
import datetime as dt
from .cube_info import Camera, Grating, Optics, System, MiscZStage


@dataclass
class CubeZaxis:
    Key: str


@dataclass
class Cube:
    AcqMode: str
    BroadBand: np.ndarray
    LaserNm: np.ndarray
    Name: str
    Type: str
    ZAxis: CubeZaxis
    CreationDate: str = field(
        default_factory=lambda: dt.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    )


@dataclass
class MiscIllumination:
    Intensity: np.ndarray
    Mode: str
    Source: str


@dataclass
class Misc:
    Illumination: MiscIllumination
    ZStage: MiscZStage = field(default_factory=MiscZStage)


@dataclass
class Info:
    Camera: Camera
    Cube: Cube
    Grating: Grating
    Misc: Misc
    Optics: Optics
    System: System


@dataclass
class TemporalCube:
    Angle: np.ndarray
    Images: np.ndarray
    Info: Info
    TimeExposure: np.ndarray
    Timestamp: np.ndarray
