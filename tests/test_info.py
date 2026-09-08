"""Tests for the `info` module."""

import numpy as np

from photonetc import info, utils


def test_camera():
    xax0 = info.CameraAxis0({"Name": np.array(["x"])})
    xax1 = info.CameraAxis1(
        {
            "Coefs": np.zeros(2),
            "Decimals": np.array([0]),
            "Name": np.array(["xpos"]),
            "Unit": np.array(["cm"]),
        }
    )

    xaxis = info.CameraAxis(
        attrs={
            "Coefs": np.zeros(1),
            "Decimals": np.array([0]),
            "Name": np.array(["xpos"]),
            "Unit": np.array(["cm"]),
        },
        _items={"0": xax0, "1": xax1},
    )

    yax0 = info.CameraAxis0({"Name": np.array(["y"])})
    yax1 = info.CameraAxis1(
        {
            "Coefs": np.zeros(1),
            "Decimals": np.array([0]),
            "Name": np.array(["ypos"]),
            "Unit": np.array(["cm"]),
        }
    )

    yaxis = info.CameraAxis(
        attrs={
            "Coefs": np.zeros(1),
            "Decimals": np.array([0]),
            "Name": np.array(["ypos"]),
            "Unit": np.array(["cm"]),
        },
        _items={"0": yax0, "1": yax1},
    )

    dprops = info.CameraDynamicProperties(
        {"ROI Mode": np.array([info.CameraRoiMode.SOFTWARE.value])}
    )

    camera_attrs = info.CameraAttrs(
        {
            "AveragingMode": np.array([info.CameraAveragingMode.NONE.value]),
            "Binning": np.ones(2),
            "BitDepth": np.array([16]),
            "CaptorSize": np.array([2048, 2048]),
            "CoolerSetPoint": np.array(["-"]),
            "DetectorMode": np.array([info.CameraDetectorMode.CONVENTIONAL.value]),
            "GradientOrientation": np.array([0]),
            "Model": np.array(["test_model"]),
            "Name": np.array(["test_name"]),
            "Orientation": np.array([0]),
            "PixelSizeNm": np.array([1]),
            "ReadoutSpeed": np.array(["125"]),
            "RoiSize": np.array([2048, 2048]),
            "RoiStart": np.array([0, 0]),
            "Shutter": np.array([info.CameraShutter.AUTO_NONE.value]),
            "SN": np.array(["test_sn"]),
            "Temperature": np.array(["-10"]),
            "Trigger": np.array([info.CameraTrigger.NONE.value]),
            "VerticalFlip": np.array([0]),
        }
    )
    c = info.Camera(
        attrs=camera_attrs,
        _items={"DynamicProperties": dprops, "XAxis": xaxis, "YAxis": yaxis},
    )

    assert c.attrs["Name"] == "test_name"
    assert c["DynamicProperties"].attrs["ROI Mode"] == info.CameraRoiMode.SOFTWARE
    assert c["XAxis"].attrs["Coefs"][0] == 0
    assert c["XAxis"]["0"].attrs["Name"] == "x"
    assert c["YAxis"]["1"].attrs["Name"] == "ypos"


def test_grating():
    g0_attrs = info.GratingSlotAttrs(
        {
            "BeamSide": np.array([info.GratingBeamSide.RIGHT.value]),
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": np.array(["slot0"]),
            "Type": np.array([info.GratingType.TRANSMISSION.value]),
        }
    )

    g0_cal = info.GratingSlotCalibration(
        info.GratingSlotCalibrationAttrs(
            {
                "Curve": np.array([1.0]),
                "Factor": np.array([1.0]),
                "FocalLengthCoef": np.array([1.0]),
                "FocalLengthUm": np.array([1.0]),
                "Offset": np.array([1.0]),
                "Period": np.array([1.0]),
                "Slope": np.array([1.0]),
                "StageOffset": np.array([1.0]),
                "Temperature": np.array([0.0]),
                "User": np.array(["user"]),
            }
        )
    )

    g0_reg = info.GratingSlotRegistration(
        info.GratingSlotRegistrationAttrs(
            {
                "Scaling_X": np.array([1.0]),
                "Scaling_Y": np.array([1.0]),
                "Translation_X": np.array([0.0]),
                "Translation_Y": np.array([0.0]),
            }
        )
    )

    g0 = info.GratingSlot(
        attrs=g0_attrs,
        _items={
            "Calibration": g0_cal,
            "Registration": {"0": g0_reg},
        },
    )

    g1 = info.GratingSlotEmpty(
        info.GratingSlotEmptyAttrs(
            {
                "FWHM": np.array([1.0]),
                "MaxWavelength": np.array([1000.0]),
                "MinWavelength": np.array([500.0]),
                "Name": np.array(["slot1"]),
                "Type": np.array([info.GratingType.STATIC.value]),
            }
        )
    )

    emptys = [
        info.GratingSlotEmpty(
            info.GratingSlotEmptyAttrs(
                {
                    "FWHM": np.array([idx * 1.0]),
                    "MaxWavelength": np.array([idx * 200.0]),
                    "MinWavelength": np.array([idx * 100.0]),
                    "Name": np.array([f"slot{idx}"]),
                    "Type": np.array([info.GratingType.STATIC.value]),
                }
            )
        )
        for idx in range(2, 9)
    ]

    g = info.Grating(
        {
            "0": g0,
            "1": g1,
            "2": emptys[0],
            "3": emptys[1],
            "4": emptys[2],
            "5": emptys[3],
            "6": emptys[4],
            "7": emptys[5],
            "8": emptys[6],
        }
    )

    g0 = g["0"]
    g1 = g["1"]
    g8 = g["8"]
    assert isinstance(g0, info.GratingSlot)
    assert isinstance(g1, info.GratingSlotEmpty)
    assert isinstance(g8, info.GratingSlotEmpty)
    assert g0.attrs["BeamSide"] == info.GratingBeamSide.RIGHT
    assert g1.attrs["Name"] == "slot1"
    assert g8.attrs["Name"] == "slot8"


def test_optics():
    o = info.Optics(
        info.OpticsAttrs({"FocusStatus": np.array([1]), "Objective": np.array(["o1"])})
    )

    assert o.attrs["Objective"] == "o1"


def test_system():
    s = info.System(
        info.SystemAttrs(
            {
                "SN": np.array(["test_sn"]),
                "SoftwareVersion": np.array(["0.0.0"]),
                "Type": np.array([info.SystemType.SYSTEM.value]),
            }
        )
    )

    assert s.attrs["Type"] == info.SystemType.SYSTEM
    assert s.attrs["SN"] == "test_sn"
    assert s.attrs["SoftwareVersion"] == "0.0.0"


def test_info():
    i = info.Info(
        {
            "Camera": utils.info_camera_default(),
            "Cube": utils.info_cube_default(),
            "Grating": utils.info_grating_default(),
            "Misc": utils.info_misc_default(),
            "Optics": utils.info_optics_default(),
            "System": utils.info_system_default(),
        }
    )

    assert i["Camera"]
    assert i["Grating"]
    assert i["Optics"]
    assert i["System"]
