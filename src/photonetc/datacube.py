# # Hypercube

from __future__ import annotations
from typing import TYPE_CHECKING
import datetime as dt
import itertools
import numpy as np
import h5py

if TYPE_CHECKING:
    import os


class CameraInfo:
    """Camera info."""

    def __init__(self, data: h5py.Group):
        self._data = data
        self._validate()

    def __getattr__(self, name):
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


class OpticsInfo:
    """Optics info."""

    def __init__(self, data: h5py.Group):
        self._data = data
        self._validate()

    def __getattr__(self, name):
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


class Info:
    """Info. (`file["Cube"]["Info"]`)"""

    def __init__(self, data: h5py.Group) -> None:
        camera = data["Camera"]
        if not isinstance(camera, h5py.Group):
            raise ValueError(f"Invalid dataset. 'Camera' is not an h5 group.")

        optics = data["Optics"]
        if not isinstance(optics, h5py.Group):
            raise ValueError(f"Invalid dataset. 'Optics' is not an h5 group.")

        self._data = data
        self._camera = CameraInfo(camera)
        self._optics = OpticsInfo(optics)

    def __getattr__(self, name):
        return self._data[name]

    @property
    def camera(self) -> CameraInfo:
        return self._camera

    @property
    def optics(self) -> OpticsInfo:
        return self._optics


class Datacube:
    """Generic data cube."""

    def __init__(self, path: os.PathLike):
        file = h5py.File(path)
        root = file["Cube"]
        if not isinstance(root, h5py.Group):
            raise ValueError(f"Invalid dataset. 'Cube' is not an h5 group.")

        info = root["Info"]
        if not isinstance(info, h5py.Group):
            raise ValueError(f"Invalid dataset. 'Info' is not an h5 group.")

        self._file = file
        self._info = Info(info)
        self._validate()

    def __getattr__(self, name):
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
        """Hypercube data. (`file["Cube"]["Images"]`)

        Raises:
            ValueError: Invalid data.

        Returns:
            h5py.Dataset: Hypercube data.
        """
        KEY = "Images"
        data = self.root[KEY]
        if not isinstance(data, h5py.Dataset):
            raise ValueError(f"Invalid dataset. '{KEY}' is not an h5 dataset.")

        return data

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

    def _validate(self) -> None:
        """Validate dataset has correct shape.

        Raises:
            ValueError: Data is invalid.
        """
        self.root
        self.data
        self.exposure_times


class Hypercube(Datacube):
    """Sprectrally resolved data."""

    def __init__(self, path: os.PathLike):
        super().__init__(path)
        self._validate()

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
        self.wavelengths


class Video(Datacube):
    """Temporally resolved data."""

    def __init__(self, path: os.PathLike):
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
