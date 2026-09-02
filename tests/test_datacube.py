import pathlib

import h5py
import numpy as np
import pytest

import photonetc as pe

from . import utils

DATA_PATH_SPECTRALCUBE = pathlib.Path(__file__).parent.parent / "data/spectralcube.h5"
DATA_PATH_TEMPORALCUBE_BROADBAND = (
    pathlib.Path(__file__).parent.parent / "data/temporalcube-broadband.h5"
)
DATA_PATH_TEMPORALCUBE_BANDPASS = (
    pathlib.Path(__file__).parent.parent / "data/temporalcube-bandpass.h5"
)


def test_temporalcube_bandpass_from_file():
    f = h5py.File(DATA_PATH_TEMPORALCUBE_BANDPASS)
    c = pe.datacube.TemporalCube.from_file(f)

    FRAMES = 21
    assert c["Angle"].shape[0] == FRAMES
    assert c["Images"].shape[0] == FRAMES
    assert c["TimeExposure"].shape[0] == FRAMES
    assert c["Timestamp"].shape[0] == FRAMES

    assert c.band_type is pe.datacube.Bandtype.Bandpass
    assert c["GratingID"] is not None
    assert c["GratingID"].shape[0] == FRAMES  # pyright: ignore[reportOptionalMemberAccess]
    assert c["Wavelength"] is not None
    assert c["Wavelength"].shape[0] == FRAMES  # pyright: ignore[reportOptionalMemberAccess]

    assert c["Info"]["System"].attrs["Type"] == pe.info.SystemType.SYSTEM
    assert c["Info"]["Misc"]["Z-Stage"].attrs["Position"] == np.array([110.75])
    assert c["Info"]["Misc"]["Illumination"] is None
    assert c["Info"]["Cube"]["ZAxis"].attrs["Key"] == np.array(
        [pe.info.CubeZAxisKey.INDEX.value]
    )
    assert c["Info"]["Cube"].attrs["AcqMode"] == np.array(
        [pe.info.CubeAcqMode.VIDEO.value]
    )
    assert c["Info"]["Cube"].attrs["BroadBand"] == np.array([0])
    assert c["Info"]["Cube"].attrs["Type"] == np.array([pe.info.CubeDatatype.I16])
    assert c["Info"]["Cube"].attrs["FixedTimeExposure"] is None
    assert c["Info"]["Cube"].attrs["LaserNm"] is None
    assert c["Info"]["Cube"].attrs["LowerWavelength"] is None
    assert c["Info"]["Cube"].attrs["UpperWavelength"] is None
    assert c["Info"]["Cube"].attrs["WavelengthStep"] is None


def test_temporalcube_broadband_from_file():
    f = h5py.File(DATA_PATH_TEMPORALCUBE_BROADBAND)
    c = pe.datacube.TemporalCube.from_file(f)

    FRAMES = 18
    assert c["Angle"].shape[0] == FRAMES
    assert c["Images"].shape[0] == FRAMES
    assert c["TimeExposure"].shape[0] == FRAMES
    assert c["Timestamp"].shape[0] == FRAMES

    assert c.band_type is pe.datacube.Bandtype.Broadband
    assert c["GratingID"] is None
    assert c["Wavelength"] is None

    assert c["Info"]["System"].attrs["Type"] == pe.info.SystemType.SYSTEM
    assert c["Info"]["Misc"]["Z-Stage"].attrs["Position"] == np.array(
        [-21.200000000000003]
    )
    assert c["Info"]["Misc"]["Illumination"].attrs["Source"] == np.array(
        [pe.info.IlluminationState.DISABLED.value]
    )
    assert c["Info"]["Cube"]["ZAxis"].attrs["Key"] == np.array(
        [pe.info.CubeZAxisKey.INDEX.value]
    )
    assert c["Info"]["Cube"].attrs["AcqMode"] == np.array(
        [pe.info.CubeAcqMode.VIDEO.value]
    )
    assert c["Info"]["Cube"].attrs["BroadBand"] == np.array([1])
    assert c["Info"]["Cube"].attrs["Type"] == np.array([pe.info.CubeDatatype.I16])
    assert c["Info"]["Cube"].attrs["FixedTimeExposure"] is None
    assert c["Info"]["Cube"].attrs["LaserNm"] == np.array([385.0])
    assert c["Info"]["Cube"].attrs["LowerWavelength"] is None
    assert c["Info"]["Cube"].attrs["UpperWavelength"] is None
    assert c["Info"]["Cube"].attrs["WavelengthStep"] is None


def test_spectralcube_from_file():
    f = h5py.File(DATA_PATH_SPECTRALCUBE)
    c = pe.datacube.SpectralCube.from_file(f)

    FRAMES = 88
    assert c["Images"].shape[0] == FRAMES
    assert c["GratingID"].shape[0] == FRAMES
    assert c["TimeExposure"].shape[0] == FRAMES
    assert c["Translation_X"].shape[0] == FRAMES
    assert c["Translation_Y"].shape[0] == FRAMES
    assert c["Wavelength"].shape[0] == FRAMES
    assert c["Info"]["System"].attrs["Type"] == pe.info.SystemType.SYSTEM
    assert c["Info"]["Cube"]["ZAxis"] is None
    assert c["Info"]["Cube"].attrs["AcqMode"] == np.array(
        [pe.info.CubeAcqMode.HYPERSPECTRAL.value]
    )
    assert c["Info"]["Cube"].attrs["FixedTimeExposure"] == np.array([1])
    assert c["Info"]["Cube"].attrs["LowerWavelength"] == np.array([750.0])
    assert c["Info"]["Cube"].attrs["UpperWavelength"] == np.array([402.0])
    assert c["Info"]["Cube"].attrs["WavelengthStep"] == np.array([4.0])


def test_spectralcube():
    c = pe.datacube.SpectralCube(
        _items={
            "Images": np.zeros(1),
            "TimeExposure": np.zeros(1),
            "Info": utils.info_default(),
            "GratingID": np.zeros(1, dtype=np.int32),
            "Translation_X": np.zeros(1),
            "Translation_Y": np.zeros(1),
            "Wavelength": np.zeros(1),
        }
    )

    assert c["GratingID"][0] == 0
    assert c["Images"][0] == 0
    assert c["Info"]["System"].attrs["SoftwareVersion"] == "0.0.0"
    assert c["TimeExposure"][0] == 0
    assert c["Translation_X"][0] == 0
    assert c["Translation_Y"][0] == 0
    assert c["Wavelength"][0] == 0


def test_datacube_invalid_shape():
    with pytest.raises(ValueError) as err:
        pe.datacube.SpectralCube(
            _items={
                "Images": np.zeros((1, 1)),
                "TimeExposure": np.zeros(2),
                "Info": utils.info_default(),
                "GratingID": np.zeros(1, dtype=np.int32),
                "Translation_X": np.zeros(1),
                "Translation_Y": np.zeros(1),
                "Wavelength": np.zeros(1),
            }
        )

    assert "TimeExposure" in str(err.value)


def test_spectralcube_invalid_shape():
    with pytest.raises(ValueError) as err:
        pe.datacube.SpectralCube(
            _items={
                "Images": np.zeros((1, 1)),
                "TimeExposure": np.zeros(1),
                "Info": utils.info_default(),
                "GratingID": np.zeros(2, dtype=np.int32),
                "Translation_X": np.zeros(2),
                "Translation_Y": np.zeros(2),
                "Wavelength": np.zeros(2),
            }
        )

    assert "GratingID" in str(err.value)
    assert "Translation_X" in str(err.value)
    assert "Translation_Y" in str(err.value)
    assert "Wavelength" in str(err.value)


def test_temporalcube():
    c = pe.datacube.TemporalCube(
        _items={
            "Images": np.zeros(1),
            "TimeExposure": np.zeros(1),
            "Info": utils.info_default(),
            "Angle": np.zeros(1),
            "GratingID": np.zeros(1, dtype=np.int32),
            "Timestamp": np.array(["2000/01/01 00:00:00.000"]),
            "Wavelength": np.zeros(1),
        }
    )

    assert c["GratingID"] is not None
    assert c["GratingID"][0] == 0  # type: ignore
    assert c["Images"][0] == 0
    assert c["Info"]["System"].attrs["SoftwareVersion"] == "0.0.0"
    assert c["TimeExposure"][0] == 0
    assert c["Angle"][0] == 0
    assert c["Timestamp"][0] == "2000/01/01 00:00:00.000"
    assert c["Wavelength"][0] == 0  # pyright: ignore[reportOptionalSubscript]


def test_temporalcube_invalid_shape():
    with pytest.raises(ValueError) as err:
        pe.datacube.TemporalCube(
            _items={
                "Images": np.zeros((1, 1)),
                "TimeExposure": np.zeros(1),
                "Info": utils.info_default(),
                "Angle": np.zeros(2),
                "GratingID": np.zeros(2, dtype=np.int32),
                "Timestamp": np.array(
                    ["2000/01/01 00:00:00.000", "2000/01/02 00:00:00.000"]
                ),
                "Wavelength": np.zeros(2),
            }
        )

    assert "Angle" in str(err.value)
    assert "GratingID" in str(err.value)
    assert "Timestamp" in str(err.value)
    assert "Wavelength" in str(err.value)


# def test_datacube_info_cube():
# assert pe.datacube.InfoCube.NAME == "Cube"
# cube = pe.datacube.InfoCube()
# cube = pe.datacube.InfoCube()
# assert cube.children is None


# def test_spectralcube_properties():
#     PX_SIZE_NM = 6500
#     MAGNIFICATION = 20
#     BINS = 4
#     FRAME_COUNT = 88
#     X_COUNT = 1024
#     Y_COUNT = 1024
#     X_START = 512
#     Y_START = 512

#     cube = pe.SpectralCube(DATA_PATH_SPECTRALCUBE)

#     binning = cube.binning
#     assert binning[0] == BINS
#     assert binning[1] == BINS

#     roi_size = cube.camera.roi_size
#     assert roi_size.shape == (2,)
#     assert roi_size[0] == X_COUNT
#     assert roi_size[1] == Y_COUNT

#     roi_start = cube.camera.roi_start
#     assert roi_start.shape == (2,)
#     assert roi_start[0] == X_START
#     assert roi_start[1] == Y_START

#     roi = cube.camera.roi
#     assert roi.shape == (4,)
#     assert roi[0] == X_START
#     assert roi[1] == Y_START
#     assert roi[2] == X_COUNT
#     assert roi[3] == Y_COUNT

#     assert cube.camera.pixel_size == PX_SIZE_NM
#     assert cube.optics.objective == "20x"
#     assert cube.optics.magnification == MAGNIFICATION

#     assert cube.data.shape == (FRAME_COUNT, X_COUNT / BINS, Y_COUNT / BINS)
#     assert cube.wavelengths.shape == (FRAME_COUNT,)
#     assert cube.exposure_times.shape == (FRAME_COUNT,)

#     px_size = cube.pixel_size
#     assert px_size.shape == (2,)
#     assert px_size[0] == PX_SIZE_NM * BINS / MAGNIFICATION
#     assert px_size[1] == PX_SIZE_NM * BINS / MAGNIFICATION


# def test_temporalcube_properties():
#     PX_SIZE_NM = 6500
#     MAGNIFICATION = 20
#     BINS = 4
#     FRAME_COUNT = 18
#     X_COUNT = 1024
#     Y_COUNT = 1024
#     X_START = 512
#     Y_START = 512

#     cube = pe.TemporalCube(DATA_PATH_TEMPORALCUBE)

#     binning = cube.binning
#     assert binning[0] == BINS
#     assert binning[1] == BINS

#     roi_size = cube.camera.roi_size
#     assert roi_size.shape == (2,)
#     assert roi_size[0] == X_COUNT
#     assert roi_size[1] == Y_COUNT

#     roi_start = cube.camera.roi_start
#     assert roi_start.shape == (2,)
#     assert roi_start[0] == X_START
#     assert roi_start[1] == Y_START

#     roi = cube.camera.roi
#     assert roi.shape == (4,)
#     assert roi[0] == X_START
#     assert roi[1] == Y_START
#     assert roi[2] == X_COUNT
#     assert roi[3] == Y_COUNT

#     assert cube.camera.pixel_size == PX_SIZE_NM
#     assert cube.optics.objective == "20x"
#     assert cube.optics.magnification == MAGNIFICATION

#     assert cube.data.shape == (FRAME_COUNT, X_COUNT / BINS, Y_COUNT / BINS)
#     assert len(cube.timestamps) == FRAME_COUNT
#     assert cube.exposure_times.shape == (FRAME_COUNT,)

#     px_size = cube.pixel_size
#     assert px_size.shape == (2,)
#     assert px_size[0] == PX_SIZE_NM * BINS / MAGNIFICATION
#     assert px_size[1] == PX_SIZE_NM * BINS / MAGNIFICATION


# def test_spectralcube_to_abstract():
#     cube = pe.SpectralCube(DATA_PATH_SPECTRALCUBE)
#     cube.to_abstract()


# def test_temporalcube_to_abstract():
#     cube = pe.TemporalCube(DATA_PATH_TEMPORALCUBE)
#     cube.to_abstract()
