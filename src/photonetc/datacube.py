"""Hypercube data backed by a file."""

from __future__ import annotations
from photonetc.cube_info import Camera
from typing import TYPE_CHECKING
import datetime as dt
import itertools
import numpy as np
import h5py
from . import cube_info as cinfo, spectralcube, temporalcube

if TYPE_CHECKING:
    import os


class CameraInfo:
    """Camera info."""

    def __init__(self, data: h5py.Group):
        """Create a new Camera info object.

        Args:
            data (h5py.Group): Group representing camera info.
                (`file["Cube"]["Info"]["Camera"]`)
        """
        self._data = data
        self._validate()

    def __getitem__(self, name):
        return self._data[name]

    @property
    def roi_size(self) -> np.ndarray:
        """Region of interest size in physical pixels. (`file["Cube"]["Info"]["Camera"].RoiSize`)

        Raises:
            ValueError: Data is invalid.

        Returns:
            np.ndarray: Region of interest size in physical pixels; `[width, height]`.
        """
        KEY = "RoiSize"
        data = self._data.attrs[KEY]
        if not isinstance(data, np.ndarray):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an ndarray.")

        return data

    @property
    def roi_start(self) -> np.ndarray:
        """Start of region of interest in physical pixels. (`file["Cube"]["Info"]["Camera"].RoiStart`)

        Raises:
            ValueError: Data is invalid.

        Returns:
            np.ndarray: Start of region of interest in physical pixels; `[x, y]`.
        """
        KEY = "RoiStart"
        data = self._data.attrs[KEY]
        if not isinstance(data, np.ndarray):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an ndarray.")

        return data

    @property
    def roi(self) -> np.ndarray:
        """Region of interest.

        Returns:
            np.ndarray: Region of interest; `[x, y, width, height]`
        """
        start = self.roi_start
        size = self.roi_size
        return np.concat([start, size])

    @property
    def binning(self) -> np.ndarray:
        """Pixel binning. (`file["Cube"]["Info"]["Camera"].Binning`)

        Raises:
            ValueError: Data is invalid.

        Returns:
            np.ndarray: Pixel binning; `[width, height]`.
        """
        KEY = "Binning"
        data = self._data.attrs[KEY]
        if not isinstance(data, np.ndarray):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an ndarray.")

        return data

    @property
    def pixel_size(self) -> float:
        """Pixel size in nanometers. (`file["Cube"]["Info"]["Camera"].PixelSizeNm`)

        Raises:
            ValueError: Data is invalid.

        Returns:
            int: Pixel size in nanometers. Pixel is assumed square.
        """
        KEY = "PixelSizeNm"
        data = self._data.attrs[KEY]
        if not isinstance(data, np.ndarray):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an ndarray.")

        return float(data[0])

    def _validate(self):
        """Validate data has the correct shape."""
        self.roi_size
        self.roi_start
        self.binning
        self.pixel_size

    def to_abstract(self) -> cinfo.Camera:
        data_x_axis = self._data["XAxis"]
        if not isinstance(data_x_axis, h5py.Group):
            raise ValueError('`data["XAxis"]` is not a group')

        data_x_axis_0 = data_x_axis["0"]
        if not isinstance(data_x_axis_0, h5py.Group):
            raise ValueError('`data["XAxis"]["0"]` is not a group')

        data_x_axis_1 = data_x_axis["1"]
        if not isinstance(data_x_axis_1, h5py.Group):
            raise ValueError('`data["XAxis"]["1"]` is not a group')

        data_y_axis = self._data["YAxis"]
        if not isinstance(data_y_axis, h5py.Group):
            raise ValueError('`data["YAxis"]` is not a group')

        data_y_axis_0 = data_y_axis["0"]
        if not isinstance(data_y_axis_0, h5py.Group):
            raise ValueError('`data["YAxis"]["0"]` is not a group')

        data_y_axis_1 = data_y_axis["1"]
        if not isinstance(data_y_axis_1, h5py.Group):
            raise ValueError('`data["YAxis"]["1"]` is not a group')

        data_dynamic_properties = self._data["DynamicProperties"]
        if not isinstance(data_dynamic_properties, h5py.Group):
            raise ValueError('`data["DynamicProperties"]` is not a group')

        x_axis_0 = cinfo.CameraAxis0(Name=data_x_axis_0.attrs["Name"])
        x_axis_1 = cinfo.CameraAxis1(
            Coefs=data_x_axis_1.attrs["Coefs"],
            Decimals=data_x_axis_1.attrs["Decimals"],
            Name=data_x_axis_1.attrs["Name"],
            Unit=data_x_axis_1.attrs["Unit"],
        )
        x_axis = cinfo.CameraAxis(
            axis_0=x_axis_0,
            axis_1=x_axis_1,
            Coefs=data_x_axis.attrs["Coefs"],
            Decimals=data_x_axis.attrs["Decimals"],
            Name=data_x_axis.attrs["Name"],
            Unit=data_x_axis.attrs["Unit"],
        )

        y_axis_0 = cinfo.CameraAxis0(Name=data_y_axis_0.attrs["Name"])
        y_axis_1 = cinfo.CameraAxis1(
            Coefs=data_y_axis_1.attrs["Coefs"],
            Decimals=data_y_axis_1.attrs["Decimals"],
            Name=data_y_axis_1.attrs["Name"],
            Unit=data_y_axis_1.attrs["Unit"],
        )
        y_axis = cinfo.CameraAxis(
            axis_0=y_axis_0,
            axis_1=y_axis_1,
            Coefs=data_y_axis.attrs["Coefs"],
            Decimals=data_y_axis.attrs["Decimals"],
            Name=data_y_axis.attrs["Name"],
            Unit=data_y_axis.attrs["Unit"],
        )

        dynamic_properties = cinfo.CameraDynamicProperties(
            ROIMode=data_dynamic_properties.attrs["ROI Mode"],
        )

        return cinfo.Camera(
            XAxis=x_axis,
            YAxis=y_axis,
            DynamicProperties=dynamic_properties,
            BitDepth=self._data.attrs["BitDepth"],
            CaptorSize=self._data.attrs["CaptorSize"],
            CoolerSetPoint=self._data.attrs["CoolerSetPoint"],
            DetectorMode=self._data.attrs["DetectorMode"],
            GradientOrientation=self._data.attrs["GradientOrientation"],
            Model=self._data.attrs["Model"],
            Name=self._data.attrs["Name"],
            PixelSizeNm=self._data.attrs["PixelSizeNm"],
            ReadoutSpeed=self._data.attrs["ReadoutSpeed"],
            RoiSize=self._data.attrs["RoiSize"],
            SN=self._data.attrs["SN"],
            Temperature=self._data.attrs["Temperature"],
            VerticalFlip=self._data.attrs["VerticalFlip"],
            AveragingMode=self._data.attrs["AveragingMode"],
            Binning=self._data.attrs["Binning"],
            Orientation=self._data.attrs["Orientation"],
            RoiStart=self._data.attrs["RoiStart"],
            Shutter=self._data.attrs["Shutter"],
            Trigger=self._data.attrs["Trigger"],
        )


class OpticsInfo:
    """Optics info."""

    def __init__(self, data: h5py.Group):
        """Create a new Optics info object.

        Args:
            data (h5py.Group): Group representing optics info.
                (`file["Cube"]["Info"]["Optics"]`)
        """
        self._data = data
        self._validate()

    def __getitem__(self, name):
        return self._data[name]

    @property
    def objective(self) -> str:
        """Objective label. (`file["Cube"]["Info"]["Optics"].Objective`)

        Raises:
            ValueError: Data is invalid.

        Returns:
            str: Objective label.
        """
        KEY = "Objective"
        data = self._data.attrs[KEY]
        if not isinstance(data, np.ndarray):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an ndarray.")

        return data[0]

    @property
    def magnification(self) -> float:
        """Magnification of the objective.
        Extracted from the objective label.

        Returns:
            float: Magnification power of the objective.
        """
        objective_label = self.objective
        objective_power_idx = objective_label.find("x")
        return float(objective_label[:objective_power_idx])

    def _validate(self):
        """Validate data has the correct shape."""
        self.objective

    def to_abstract(self) -> cinfo.Optics:
        return cinfo.Optics(
            FocusStatus=self._data.attrs["FocusStatus"],
            Objective=self._data.attrs["Objective"],
        )


class Info:
    """Info. (`file["Cube"]["Info"]`)"""

    def __init__(self, data: h5py.Group) -> None:
        camera = data["Camera"]
        if not isinstance(camera, h5py.Group):
            raise ValueError("Invalid dataset. 'Camera' is not an h5 group.")

        optics = data["Optics"]
        if not isinstance(optics, h5py.Group):
            raise ValueError("Invalid dataset. 'Optics' is not an h5 group.")

        self._data = data
        self._camera = CameraInfo(camera)
        self._optics = OpticsInfo(optics)

    def __getitem__(self, name):
        return self._data[name]

    @property
    def camera(self) -> CameraInfo:
        return self._camera

    @property
    def optics(self) -> OpticsInfo:
        return self._optics


def info_grating_to_abstract(info_grating: h5py.Group) -> cinfo.Grating:
    gratings = {}
    for key, ginfo in info_grating.items():
        if not isinstance(ginfo, h5py.Group):
            raise ValueError(f'`data["Info"]["Grating"]["{key}"]` is not a group.')

        children = ginfo.keys()
        if len(children) == 0:
            slot = cinfo.GratingSlotEmpty(
                FWHM=ginfo.attrs["FWHM"],
                MaxWavelength=ginfo.attrs["MaxWavelength"],
                MinWavelength=ginfo.attrs["MinWavelength"],
                Name=ginfo.attrs["Name"],
                Type=ginfo.attrs["Type"],
            )
            gratings[key] = slot
        elif "Calibration" in children and "Registration" in children:
            calinfo = ginfo["Calibration"]
            if not isinstance(calinfo, h5py.Group):
                raise ValueError(
                    f'`data["Info"]["Grating"]["{key}"]["Calibration"]` is not a group.'
                )

            if not isinstance(ginfo["Registration"], h5py.Group):
                raise ValueError(
                    f'`data["Info"]["Grating"]["{key}"]["Registration"]` is not a group.'
                )

            cal = cinfo.GratingSlotCalibration(
                Curve=calinfo.attrs["Curve"],
                Factor=calinfo.attrs["Factor"],
                FocalLengthCoef=calinfo.attrs["FocalLengthCoef"],
                FocalLengthUm=calinfo.attrs["FocalLengthUm"],
                Offset=calinfo.attrs["Offset"],
                Period=calinfo.attrs["Period"],
                Slope=calinfo.attrs["Slope"],
                StageOffset=calinfo.attrs["StageOffset"],
                Temperature=calinfo.attrs["Temperature"],
                User=calinfo.attrs["User"],
            )

            registrations = {}
            for rkey, reginfo in ginfo["Registration"].items():
                if not isinstance(reginfo, h5py.Group):
                    raise ValueError(
                        f'`data["Info"]["Grating"]["{key}"]["Registration"]["{rkey}"]` is not a group.'
                    )

                reg = cinfo.GratingSlotRegistration(
                    Scaling_X=reginfo.attrs["Scaling_X"],
                    Scaling_Y=reginfo.attrs["Scaling_Y"],
                    Translation_X=reginfo.attrs["Translation_X"],
                    Translation_Y=reginfo.attrs["Translation_Y"],
                )

                registrations[rkey] = reg

            slot = cinfo.GratingSlot(
                Calibration=cal,
                BeamSide=ginfo.attrs["BeamSide"],
                FWHM=ginfo.attrs["FWHM"],
                MaxWavelength=ginfo.attrs["MaxWavelength"],
                MinWavelength=ginfo.attrs["MinWavelength"],
                Name=ginfo.attrs["Name"],
                Type=ginfo.attrs["Type"],
                Registration=registrations,
            )
            gratings[key] = slot
        else:
            raise ValueError(f"unknown grating type for grating {key}")

    return cinfo.Grating(gratings=gratings)


class Datacube:
    """Generic data cube."""

    def __init__(self, path: os.PathLike | str | bytes):
        file = h5py.File(path)
        root = file["Cube"]
        if not isinstance(root, h5py.Group):
            raise ValueError("Invalid dataset. 'Cube' is not an h5 group.")

        info = root["Info"]
        if not isinstance(info, h5py.Group):
            raise ValueError("Invalid dataset. 'Info' is not an h5 group.")

        self._file = file
        self._info = Info(info)
        self._validate()

    def __getitem__(self, name):
        return self._file[name]

    @property
    def root(self) -> h5py.Group:
        """Data root. (`file["Cube"]`)

        Raises:
            ValueError: Data is invalid.

        Returns:
            h5py.Group: Data root.
        """
        KEY = "Cube"
        data = self._file[KEY]
        if not isinstance(data, h5py.Group):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an h5 group.")

        return data

    @property
    def data(self) -> h5py.Dataset:
        """Data. (`file["Cube"]["Images"]`)

        Raises:
            ValueError: Invalid data.

        Returns:
            h5py.Dataset: Data.
        """
        KEY = "Images"
        data = self.root[KEY]
        if not isinstance(data, h5py.Dataset):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an h5 dataset.")

        return data

    @property
    def data_array(self) -> np.ndarray:
        """Data as a numpy array.

        Returns:
            np.ndarray: Data.
        """
        return self.data[()]

    @property
    def exposure_times(self) -> h5py.Dataset:
        """Exposure times. (`file["Cube"]["TimeExposure"]`)

        Raises:
            ValueError: Data is invalid.

        Returns:
            np.ndarray: Exposure time of each frame in seconds.
        """
        KEY = "TimeExposure"
        data = self.root[KEY]
        if not isinstance(data, h5py.Dataset):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an h5 dataset.")

        return data

    @property
    def elapsed(self) -> np.ndarray:
        """
        Returns:
            np.ndarray: Elapsed time of each frame.
        """
        data = self.exposure_times[()]
        return np.array(itertools.accumulate(data))

    @property
    def info(self) -> Info:
        """
        Returns:
            Info: Data info.
        """
        return self._info

    @property
    def camera(self) -> CameraInfo:
        """Alias for `self.info.camera`.

        Returns:
            CameraInfo: Camera info.
        """
        return self.info.camera

    @property
    def binning(self) -> np.ndarray:
        """Alias for `self.camera.binning`.

        Returns:
            np.ndarray: Pixel binning.
        """
        return self.camera.binning

    @property
    def optics(self) -> OpticsInfo:
        """Alias for `self.info.optics`.

        Returns:
            OpticsInfo: Optics info.
        """
        return self.info.optics

    @property
    def magnification(self) -> float:
        """Alias for `self.optics.magnification`.

        Returns:
            float: Magnification.
        """
        return self.optics.magnification

    @property
    def pixel_size(self) -> np.ndarray:
        """Calculate the size of each captured image pixel in the dataset.
        This accounts for binning and magnification.

        Returns:
            np.ndarray: `[x, y]` size of a captured pixel in nanometers.
        """
        magnification = self.magnification
        binning = self.binning
        pixel_size = self.camera.pixel_size

        return pixel_size * binning / magnification

    @property
    def wavelengths(self) -> h5py.Dataset:
        """Wavelength of each frame. (`file["Cube"]["Wavelength"]`)

        Raises:
            ValueError: Invalid data.

        Returns:
            h5py.Dataset: Frame wavelengths.
        """
        KEY = "Wavelength"
        data = self.root[KEY]
        if not isinstance(data, h5py.Dataset):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an h5 dataset.")

        return data

    def _validate(self) -> None:
        """Validate dataset has correct shape.

        Raises:
            ValueError: Data is invalid.
        """
        self.root
        self.data
        self.exposure_times
        self.wavelengths


class SpectralCube(Datacube):
    """Sprectrally resolved data."""

    def __init__(self, path: os.PathLike | str | bytes):
        super().__init__(path)

    def to_abstract(self) -> spectralcube.SpectralCube:
        grating_id = self.root["GratingID"]
        if not isinstance(grating_id, h5py.Dataset):
            raise ValueError('`data["GratingID"]` is not a dataset.')

        images = self.root["Images"]
        if not isinstance(images, h5py.Dataset):
            raise ValueError('`data["Images"]` is not a dataset.')

        time_exposure = self.root["TimeExposure"]
        if not isinstance(time_exposure, h5py.Dataset):
            raise ValueError('`data["TimeExposure"]` is not a dataset.')

        translation_x = self.root["Translation_X"]
        if not isinstance(translation_x, h5py.Dataset):
            raise ValueError('`data["Translation_X"]` is not a dataset.')

        translation_y = self.root["Translation_Y"]
        if not isinstance(translation_y, h5py.Dataset):
            raise ValueError('`data["Translation_Y"]` is not a dataset.')

        wavelength = self.root["Wavelength"]
        if not isinstance(wavelength, h5py.Dataset):
            raise ValueError('`data["Wavelength"]` is not a dataset.')

        info_cube = self.info["Cube"]
        if not isinstance(info_cube, h5py.Group):
            raise ValueError('`data["Info"]["Cube"]` is not a group.')

        info_grating = self.info["Grating"]
        if not isinstance(info_grating, h5py.Group):
            raise ValueError('`data["Info"]["Grating"]` is not a group.')

        info_misc = self.info["Misc"]
        if not isinstance(info_misc, h5py.Group):
            raise ValueError('`data["Info"]["Misc"]` is not a group.')

        info_misc_zstage = info_misc["Z-Stage"]
        if not isinstance(info_misc_zstage, h5py.Group):
            raise ValueError('`data["Info"]["Misc"]["Z-Stage"]` is not a group.')

        info_system = self.info["System"]
        if not isinstance(info_system, h5py.Group):
            raise ValueError('`data["Info"]["System"]` is not a group.')

        cube = spectralcube.Cube(
            AcqMode=info_cube.attrs["AcqMode"],
            LowerWavelength=info_cube.attrs["LowerWavelength"],
            Name=info_cube.attrs["Name"],
            Type=info_cube.attrs["Type"],
            UpperWavelength=info_cube.attrs["UpperWavelength"],
            WavelengthStep=info_cube.attrs["WavelengthStep"],
            CreationDate=info_cube.attrs["CreationDate"],
            FixedTimeExposure=info_cube.attrs["FixedTimeExposure"],
        )

        grating = info_grating_to_abstract(info_grating)
        misc_zstage = cinfo.MiscZStage(Position=info_misc_zstage.attrs["Position"])
        misc = spectralcube.Misc(ZStage=misc_zstage)

        system = cinfo.System(
            SN=info_system.attrs["SN"],
            SoftwareVersion=info_system.attrs["SoftwareVersion"],
            Type=info_system.attrs["Type"],
        )

        info = spectralcube.Info(
            Camera=self.info.camera.to_abstract(),
            Cube=cube,
            Grating=grating,
            Misc=misc,
            Optics=self.info.optics.to_abstract(),
            System=system,
        )

        return spectralcube.SpectralCube(
            GratingId=grating_id[()],
            Images=images[()],
            Info=info,
            TimeExposure=time_exposure[()],
            Translation_X=translation_x[()],
            Translation_Y=translation_y[()],
            Wavelength=wavelength[()],
        )


class TemporalCube(Datacube):
    """Temporally resolved data."""

    def __init__(self, path: os.PathLike | str | bytes):
        super().__init__(path)
        self._validate()

    @property
    def timestamps(self) -> list[dt.datetime]:
        """Timestamp of each frame. (`file["Cube"]["Timestamp"]`)

        Returns:
            list[dt.datetime]: Timestamps of each frame.
        """
        KEY = "Timestamp"
        data = self.root[KEY]
        if not isinstance(data, h5py.Dataset):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an h5 dataset.")

        return [
            dt.datetime.strptime(time.decode(), "%Y/%m/%d %H:%M:%S.%f") for time in data
        ]

    def _validate(self) -> None:
        """Validate dataset has correct shape.

        Raises:
            ValueError: Data is invalid.
        """
        self.timestamps

    def to_abstract(self) -> temporalcube.TemporalCube:
        angle = self.root["Angle"]
        if not isinstance(angle, h5py.Dataset):
            raise ValueError('`data["Angle"] is not a dataset.')

        images = self.root["Images"]
        if not isinstance(images, h5py.Dataset):
            raise ValueError('`data["Images"] is not a dataset.')

        time_exposure = self.root["TimeExposure"]
        if not isinstance(time_exposure, h5py.Dataset):
            raise ValueError('`data["TimeExposure"] is not a dataset.')

        timestamp = self.root["Timestamp"]
        if not isinstance(timestamp, h5py.Dataset):
            raise ValueError('`data["Timestamp"] is not a dataset.')

        info_cube = self.info["Cube"]
        if not isinstance(info_cube, h5py.Group):
            raise ValueError('`data["Info"]["Cube"]` is not a group.')

        info_cube_zaxis = info_cube["ZAxis"]
        if not isinstance(info_cube_zaxis, h5py.Group):
            raise ValueError('`data["Info"]["Cube"]["ZAxis"]` is not a group.')

        info_grating = self.info["Grating"]
        if not isinstance(info_grating, h5py.Group):
            raise ValueError('`data["Info"]["Grating"]` is not a group.')

        info_misc = self.info["Misc"]
        if not isinstance(info_misc, h5py.Group):
            raise ValueError('`data["Info"]["Misc"]` is not a group.')

        info_misc_zstage = info_misc["Z-Stage"]
        if not isinstance(info_misc_zstage, h5py.Group):
            raise ValueError('`data["Info"]["Misc"]["Z-Stage"]` is not a group.')

        info_misc_ill = info_misc["Illumination"]
        if not isinstance(info_misc_ill, h5py.Group):
            raise ValueError('`data["Info"]["Misc"]["Illumination"]` is not a group.')

        info_system = self.info["System"]
        if not isinstance(info_system, h5py.Group):
            raise ValueError('`data["Info"]["System"]` is not a group.')

        cube_zaxis = temporalcube.CubeZaxis(Key=info_cube_zaxis.attrs["Key"])
        cube = temporalcube.Cube(
            AcqMode=info_cube.attrs["AcqMode"],
            BroadBand=info_cube.attrs["BroadBand"],
            LaserNm=info_cube.attrs["LaserNm"],
            Name=info_cube.attrs["Name"],
            Type=info_cube.attrs["Type"],
            ZAxis=cube_zaxis,
            CreationDate=info_cube.attrs["CreationDate"],
        )

        grating = info_grating_to_abstract(info_grating)

        misc_zstage = cinfo.MiscZStage(Position=info_misc_zstage.attrs["Position"])
        misc_zstage_ill = temporalcube.MiscIllumination(
            Intensity=info_misc_ill.attrs["Intensity"],
            Mode=info_misc_ill.attrs["Mode"],
            Source=info_misc_ill.attrs["Source"],
        )
        misc = temporalcube.Misc(
            Illumination=misc_zstage_ill,
            ZStage=misc_zstage,
        )

        system = cinfo.System(
            SN=info_system.attrs["SN"],
            SoftwareVersion=info_system.attrs["SoftwareVersion"],
            Type=info_system.attrs["Type"],
        )

        info = temporalcube.Info(
            Camera=self.camera.to_abstract(),
            Cube=cube,
            Grating=grating,
            Misc=misc,
            Optics=self.info.optics.to_abstract(),
            System=system,
        )

        return temporalcube.TemporalCube(
            Angle=angle,
            Images=images[()],
            Info=info,
            TimeExposure=time_exposure[()],
            Timestamp=timestamp,
        )
