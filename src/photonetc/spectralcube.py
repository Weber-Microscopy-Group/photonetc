"""Spectrally resolved data cube."""

from dataclasses import dataclass, field
import numpy as np
import datetime as dt
import h5py
from .cube_info import MiscZStage, System, Optics, Grating, Camera


@dataclass
class Cube:
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

    def to_h5(self, group: h5py.Group):
        group.attrs["AcqMode"] = self.AcqMode
        group.attrs["LowerWavelength"] = self.LowerWavelength
        group.attrs["Name"] = self.Name
        group.attrs["Type"] = self.Type
        group.attrs["UpperWavelength"] = self.UpperWavelength
        group.attrs["WavelengthStep"] = self.WavelengthStep
        group.attrs["CreationDate"] = self.CreationDate
        group.attrs["FixedTimeExposure"] = self.FixedTimeExposure


@dataclass
class Misc:
    ZStage: MiscZStage = field(default_factory=MiscZStage)

    def to_h5(self, group: h5py.Group):
        zstage = group.create_group("Z-Stage")
        self.ZStage.to_h5(zstage)


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
class SpectralCube:
    GratingId: np.ndarray
    Images: np.ndarray
    Info: Info
    TimeExposure: np.ndarray
    Translation_X: np.ndarray
    Translation_Y: np.ndarray
    Wavelength: np.ndarray

    def to_h5(self, name: str) -> h5py.File:
        f = h5py.File(name, mode="w")
        root: h5py.Group = f.create_group("Cube")
        root.create_dataset("GratingId", data=self.GratingId)
        root.create_dataset("Images", data=self.Images)
        root.create_dataset("TimeExposure", data=self.TimeExposure)
        root.create_dataset("Translation_X", data=self.Translation_X)
        root.create_dataset("Translation_Y", data=self.Translation_Y)
        root.create_dataset("Wavelength", self.Wavelength)
        info = root.create_group("Info")
        self.Info.to_h5(info)
        return f
