import numpy as np

from photonetc import info


def info_camera_default() -> info.Camera:
    xax0 = info.CameraAxis0({"Name": np.array(["x"])})
    xax1 = info.CameraAxis1(
        {
            "Coefs": np.zeros(2),
            "Decimals": np.array([0], dtype=np.int32),
            "Name": np.array(["xpos"]),
            "Unit": np.array(["cm"]),
        }
    )

    xaxis = info.CameraAxis(
        attrs={
            "Coefs": np.zeros(1),
            "Decimals": np.array([0], dtype=np.int32),
            "Name": np.array(["xpos"]),
            "Unit": np.array(["cm"]),
        },
        _items={"0": xax0, "1": xax1},
    )

    yax0 = info.CameraAxis0({"Name": np.array(["y"])})
    yax1 = info.CameraAxis1(
        {
            "Coefs": np.zeros(1),
            "Decimals": np.array([0], dtype=np.int32),
            "Name": np.array(["ypos"]),
            "Unit": np.array(["cm"]),
        }
    )

    yaxis = info.CameraAxis(
        attrs={
            "Coefs": np.zeros(1),
            "Decimals": np.array([0], np.int32),
            "Name": np.array(["ypos"]),
            "Unit": np.array(["cm"]),
        },
        _items={"0": yax0, "1": yax1},
    )

    dprops = info.CameraDynamicProperties(
        attrs={"ROI Mode": np.array([info.CameraRoiMode.SOFTWARE.value])}
    )

    camera_attrs = info.CameraAttrs(
        {
            "AveragingMode": np.array([info.CameraAveragingMode.NONE.value]),
            "Binning": np.ones(2, dtype=np.int32),
            "BitDepth": np.array([16], dtype=np.int32),
            "CaptorSize": np.array([2048, 2048], dtype=np.int32),
            "CoolerSetPoint": np.array(["-"]),
            "DetectorMode": np.array(
                [info.CameraDetectorMode.CONVENTIONAL.value],
            ),
            "GradientOrientation": np.array([0], dtype=np.int32),
            "Model": np.array(["test_model"]),
            "Name": np.array(["test_name"]),
            "Orientation": np.array([0], dtype=np.int32),
            "PixelSizeNm": np.array([1]),
            "ReadoutSpeed": np.array(["125"]),
            "RoiSize": np.array([2048, 2048], dtype=np.int32),
            "RoiStart": np.array([0, 0], dtype=np.int32),
            "Shutter": np.array([info.CameraShutter.AUTO_NONE.value]),
            "SN": np.array(["test_sn"]),
            "Temperature": np.array(["-10"]),
            "Trigger": np.array([info.CameraTrigger.NONE.value]),
            "VerticalFlip": np.array([0], dtype=np.int32),
        }
    )
    return info.Camera(
        attrs=camera_attrs,
        _items={"DynamicProperties": dprops, "XAxis": xaxis, "YAxis": yaxis},
    )


def info_grating_default() -> info.Grating:
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

    g0_cal_attrs = info.GratingSlotCalibrationAttrs(
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
    g0_cal = info.GratingSlotCalibration(attrs=g0_cal_attrs)

    g0_reg_attrs = info.GratingSlotRegistrationAttrs(
        {
            "Scaling_X": np.array([1.0]),
            "Scaling_Y": np.array([1.0]),
            "Translation_X": np.array([0.0]),
            "Translation_Y": np.array([0.0]),
        }
    )
    g0_reg = info.GratingSlotRegistration(attrs=g0_reg_attrs)

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

    empty = [
        info.GratingSlotEmpty(
            info.GratingSlotEmptyAttrs(
                {
                    "FWHM": np.array([0]),
                    "MaxWavelength": np.array([0]),
                    "MinWavelength": np.array([0]),
                    "Name": np.array([f"slot{idx}"]),
                    "Type": np.array([info.GratingType.STATIC.value]),
                }
            )
        )
        for idx in range(2, 9)
    ]

    return info.Grating(
        {
            "0": g0,
            "1": g1,
            "2": empty[0],
            "3": empty[1],
            "4": empty[2],
            "5": empty[3],
            "6": empty[4],
            "7": empty[5],
            "8": empty[6],
        }
    )


def info_optics_default() -> info.Optics:
    attrs = info.OpticsAttrs(
        {"FocusStatus": np.array([1]), "Objective": np.array(["o1"])}
    )
    return info.Optics(attrs)


def info_system_default() -> info.System:
    return info.System(
        info.SystemAttrs(
            {
                "SN": np.array(["test_sn"]),
                "SoftwareVersion": np.array(["0.0.0"]),
                "Type": np.array([info.SystemType.SYSTEM.value]),
            }
        )
    )


def info_cube_default() -> info.Cube:
    return info.Cube(
        info.CubeAttrs(
            {
                "AcqMode": np.array([info.CubeAcqMode.HYPERSPECTRAL.value]),
                "CreationDate": np.array(["2000/01/01 12:00:00"]),
                "Name": np.array(["name"]),
                "Type": np.array([info.CubeDatatype.I16.value]),
            }
        )
    )


def info_misc_default() -> info.Misc:
    """
    # Notes
    + `Illumination` is `None`.
    """
    zstage = info.MiscZStage(info.MiscZStageAttrs({"Position": np.array([0.0])}))
    return info.Misc({"Z-Stage": zstage})


def info_default() -> info.Info:
    return info.Info(
        {
            "Camera": info_camera_default(),
            "Grating": info_grating_default(),
            "Optics": info_optics_default(),
            "System": info_system_default(),
            "Cube": info_cube_default(),
            "Misc": info_misc_default(),
        }
    )
