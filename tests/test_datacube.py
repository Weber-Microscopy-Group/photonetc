import pathlib

import h5py
import numpy as np
import pytest

import photonetc as pe

TEST_DIR = pathlib.Path(__file__).parent
DATA_PATH_SPECTRALCUBE = TEST_DIR.joinpath("data/spectralcube.h5")
DATA_PATH_TEMPORALCUBE_BROADBAND = TEST_DIR.joinpath("data/temporalcube-broadband.h5")
DATA_PATH_TEMPORALCUBE_BANDPASS = TEST_DIR.joinpath("data/temporalcube-bandpass.h5")


def test_temporalcube_bandpass_from_h5():
    f = h5py.File(DATA_PATH_TEMPORALCUBE_BANDPASS)
    c = pe.datacube.TemporalCube.from_h5(f)

    FRAMES = 21
    assert c["Angle"].shape[0] == FRAMES
    assert c["Images"].shape[0] == FRAMES
    assert c["TimeExposure"].shape[0] == FRAMES
    assert c["Timestamp"].shape[0] == FRAMES

    assert c.band_type is pe.datacube.Bandtype.Bandpass
    assert c["GratingID"] is not None
    assert c["GratingID"].shape[0] == FRAMES  # pyright: ignore[reportOptionalMemberAccess]
    assert (
        # a legacy bug saved gratings as strings, which should be converted
        c["GratingID"].dtype == np.int32  # pyright: ignore[reportOptionalMemberAccess]
    )
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
    assert c["Info"]["Cube"].attrs["Type"] == np.array([pe.info.CubeDatatype.I16])

    assert "BroadBand" in c["Info"]["Cube"].attrs
    assert "FixedTimeExposure" in c["Info"]["Cube"].attrs
    assert "LaserNm" in c["Info"]["Cube"].attrs
    assert "LowerWavelength" in c["Info"]["Cube"].attrs
    assert "UpperWavelength" in c["Info"]["Cube"].attrs
    assert "WavelengthStep" in c["Info"]["Cube"].attrs
    assert c["Info"]["Cube"].attrs["BroadBand"] == np.array([0])
    assert c["Info"]["Cube"].attrs["FixedTimeExposure"] is None
    assert c["Info"]["Cube"].attrs["LaserNm"] is None
    assert c["Info"]["Cube"].attrs["LowerWavelength"] is None
    assert c["Info"]["Cube"].attrs["UpperWavelength"] is None
    assert c["Info"]["Cube"].attrs["WavelengthStep"] is None


def test_temporalcube_broadband_from_h5():
    f = h5py.File(DATA_PATH_TEMPORALCUBE_BROADBAND)
    c = pe.datacube.TemporalCube.from_h5(f)

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
    assert c["Info"]["Cube"].attrs["Type"] == np.array([pe.info.CubeDatatype.I16])

    assert "BroadBand" in c["Info"]["Cube"].attrs
    assert "FixedTimeExposure" in c["Info"]["Cube"].attrs
    assert "LaserNm" in c["Info"]["Cube"].attrs
    assert "LowerWavelength" in c["Info"]["Cube"].attrs
    assert "UpperWavelength" in c["Info"]["Cube"].attrs
    assert "WavelengthStep" in c["Info"]["Cube"].attrs
    assert c["Info"]["Cube"].attrs["BroadBand"] == np.array([1])
    assert c["Info"]["Cube"].attrs["FixedTimeExposure"] is None
    assert c["Info"]["Cube"].attrs["LaserNm"] == np.array([385.0])
    assert c["Info"]["Cube"].attrs["LowerWavelength"] is None
    assert c["Info"]["Cube"].attrs["UpperWavelength"] is None
    assert c["Info"]["Cube"].attrs["WavelengthStep"] is None


def test_spectralcube_from_h5():
    f = h5py.File(DATA_PATH_SPECTRALCUBE)
    c = pe.datacube.SpectralCube.from_h5(f)

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

    assert "FixedTimeExposure" in c["Info"]["Cube"].attrs
    assert "LowerWavelength" in c["Info"]["Cube"].attrs
    assert "UpperWavelength" in c["Info"]["Cube"].attrs
    assert "WavelengthStep" in c["Info"]["Cube"].attrs
    assert c["Info"]["Cube"].attrs["FixedTimeExposure"] == np.array([1])
    assert c["Info"]["Cube"].attrs["LowerWavelength"] == np.array([750.0])
    assert c["Info"]["Cube"].attrs["UpperWavelength"] == np.array([402.0])
    assert c["Info"]["Cube"].attrs["WavelengthStep"] == np.array([4.0])


def test_spectralcube():
    info = pe.utils.info_default()
    c = pe.datacube.SpectralCube(
        {
            "Images": np.zeros((1, *info["Camera"].attrs["RoiSize"])),
            "TimeExposure": np.zeros(1),
            "Info": info,
            "GratingID": np.array([0], dtype=np.int32),
            "Translation_X": np.zeros(1),
            "Translation_Y": np.zeros(1),
            "Wavelength": np.zeros(1),
        }
    )

    assert c["GratingID"][0] == 0
    assert c["Images"][0, 0, 0] == 0
    assert c["Info"]["System"].attrs["SoftwareVersion"] == "0.0.0"
    assert c["TimeExposure"][0] == 0
    assert c["Translation_X"][0] == 0
    assert c["Translation_Y"][0] == 0
    assert c["Wavelength"][0] == 0


def test_datacube_invalid_shape():
    with pytest.raises(ValueError) as err:
        pe.datacube.SpectralCube(
            {
                "Images": np.zeros((1, 1, 1)),
                "TimeExposure": np.zeros(2),
                "Info": pe.utils.info_default(),
                "GratingID": np.array([0], dtype=np.int32),
                "Translation_X": np.zeros(1),
                "Translation_Y": np.zeros(1),
                "Wavelength": np.zeros(1),
            }
        )

    assert "TimeExposure" in str(err.value)


def test_spectralcube_invalid_shape():
    with pytest.raises(ValueError) as err:
        info = pe.utils.info_default()
        pe.datacube.SpectralCube(
            {
                "Images": np.zeros((1, *info["Camera"].attrs["RoiSize"])),
                "TimeExposure": np.zeros(1),
                "Info": info,
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
    info = pe.utils.info_default()
    info["Cube"].attrs["AcqMode"] = np.array([pe.info.CubeAcqMode.VIDEO])
    c = pe.datacube.TemporalCube(
        {
            "Images": np.zeros((1, *info["Camera"].attrs["RoiSize"])),
            "TimeExposure": np.zeros(1),
            "Info": info,
            "Angle": np.zeros(1),
            "GratingID": np.array([0], dtype=np.int32),
            "Timestamp": np.array(["2000/01/01 00:00:00.000"]),
            "Wavelength": np.zeros(1),
        }
    )

    assert c["GratingID"] is not None
    assert c["GratingID"][0] == 0  # pyright: ignore[reportOptionalSubscript]
    assert c["Images"][0, 0, 0] == 0
    assert c["Info"]["System"].attrs["SoftwareVersion"] == "0.0.0"
    assert c["TimeExposure"][0] == 0
    assert c["Angle"][0] == 0
    assert c["Timestamp"][0] == "2000/01/01 00:00:00.000"
    assert c["Wavelength"][0] == 0  # pyright: ignore[reportOptionalSubscript]


def test_temporalcube_invalid_shape():
    with pytest.raises(ValueError) as err:
        info = pe.utils.info_default()
        info["Cube"].attrs["AcqMode"] = np.array([pe.info.CubeAcqMode.VIDEO])
        pe.datacube.TemporalCube(
            {
                "Images": np.zeros((1, *info["Camera"].attrs["RoiSize"])),
                "TimeExposure": np.zeros(1),
                "Info": info,
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


def test_temporalcube_invalid_acqmode():
    with pytest.raises(ValueError) as err:
        info = pe.utils.info_default()
        info["Cube"].attrs["AcqMode"] = np.array([pe.info.CubeAcqMode.HYPERSPECTRAL])
        pe.datacube.TemporalCube(
            {
                "Images": np.zeros((1, *info["Camera"].attrs["RoiSize"])),
                "TimeExposure": np.zeros(1),
                "Info": info,
                "Angle": np.zeros(1),
                "GratingID": np.array([0], dtype=np.int32),
                "Timestamp": np.array(["2000/01/01 00:00:00.000"]),
                "Wavelength": np.zeros(1),
            }
        )

    assert "Info/Cube.AcqMode" in str(err.value)


def test_spectralcube_invalid_acqmode():
    with pytest.raises(ValueError) as err:
        info = pe.utils.info_default()
        info["Cube"].attrs["AcqMode"] = np.array([pe.info.CubeAcqMode.VIDEO])
        pe.datacube.SpectralCube(
            {
                "Images": np.zeros((1, *info["Camera"].attrs["RoiSize"])),
                "TimeExposure": np.zeros(1),
                "Info": info,
                "GratingID": np.array([0], dtype=np.int32),
                "Translation_X": np.zeros(1),
                "Translation_Y": np.zeros(1),
                "Wavelength": np.zeros(1),
            }
        )

    assert "Info/Cube.AcqMode" in str(err.value)
