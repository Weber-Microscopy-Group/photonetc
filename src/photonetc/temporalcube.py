"""Temporally resolved data cube."""

from typing import TYPE_CHECKING
from dataclasses import dataclass, field
import numpy as np
import datetime as dt
from .cube_info import Camera, Grating, Optics, System, MiscZStage

if TYPE_CHECKING:
    import h5py


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

    def to_h5(self, group: h5py.Group):
        group.attrs["AcqMode"] = self.AcqMode
        group.attrs["BroadBand"] = self.BroadBand
        group.attrs["LaserNm"] = self.LaserNm
        group.attrs["Name"] = self.Name
        group.attrs["Type"] = self.Type
        group.attrs["ZAxis"] = self.ZAxis
        group.attrs["CreationDate"] = self.CreationDate


@dataclass
class MiscIllumination:
    Intensity: np.ndarray
    Mode: str
    Source: str

    def to_h5(self, group: h5py.Group):
        group.attrs["Intensity"] = self.Intensity
        group.attrs["Mode"] = self.Mode
        group.attrs["Source"] = self.Source


@dataclass
class Misc:
    Illumination: MiscIllumination
    ZStage: MiscZStage = field(default_factory=MiscZStage)

    def to_h5(self, group: h5py.Group):
        group.attrs["Illumination"] = self.Illumination
        group.attrs["ZStage"] = self.ZStage


@dataclass
class Info:
    Camera: Camera
    Cube: Cube
    Grating: Grating
    Misc: Misc
    Optics: Optics
    System: System

    def to_h5(self, group: h5py.Group):
        camera = group.create_group("Camera")
        cube = group.create_group("Cube")
        grating = group.create_group("Grating")
        misc = group.create_group("Misc")
        optics = group.create_group("Optics")
        system = group.create_group("System")
        self.Camera.to_h5(camera)
        self.Cube.to_h5(cube)
        self.Grating.to_h5(grating)
        self.Misc.to_h5(misc)
        self.Optics.to_h5(optics)
        self.System.to_h5(system)


@dataclass
class TemporalCube:
    Angle: np.ndarray
    Images: np.ndarray
    Info: Info
    TimeExposure: np.ndarray
    Timestamp: np.ndarray

    def to_h5(self, name: str) -> h5py.File:
        f = h5py.File(name, mode="w")
        root: h5py.Group = f.create_group("Cube")
        root.create_dataset("Angle", data=self.Angle)
        root.create_dataset("Images", data=self.Images)
        root.create_dataset("TimeExposure", data=self.TimeExposure)
        root.create_dataset("Timestamp", self.Timestamp)
        info = root.create_group("Info")
        self.Info.to_h5(info)
        return f
