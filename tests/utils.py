from photonetc import info
import numpy as np


def info_camera_default() -> info.Camera:
    xax0 = info.CameraAxis0({"Name": "x"})
    xax1 = info.CameraAxis1(
        {"Coefs": np.zeros(2), "Decimals": np.array([0]), "Name": "xpos", "Unit": "cm"}
    )

    xaxis = info.CameraAxis(
        attrs={
            "Coefs": np.zeros(1),
            "Decimals": np.array([0]),
            "Name": "xpos",
            "Unit": "cm",
        },
        _items={"0": xax0, "1": xax1},
    )

    yax0 = info.CameraAxis0({"Name": "y"})
    yax1 = info.CameraAxis1(
        {"Coefs": np.zeros(1), "Decimals": np.array([0]), "Name": "ypos", "Unit": "cm"}
    )

    yaxis = info.CameraAxis(
        attrs={
            "Coefs": np.zeros(1),
            "Decimals": np.array([0]),
            "Name": "ypos",
            "Unit": "cm",
        },
        _items={"0": yax0, "1": yax1},
    )

    dprops = info.CameraDynamicProperties(
        attrs={"ROI Mode": info.CameraRoiMode.SOFTWARE}
    )

    camera_attrs = info.CameraAttrs(
        {
            "AveragingMode": info.CameraAveragingMode.NONE,
            "Binning": np.ones(2),
            "BitDepth": np.array([16]),
            "CaptorSize": np.array([2048, 2048]),
            "CoolerSetPoint": "-",
            "DetectorMode": info.CameraDetectorMode.CONVENTIONAL,
            "GradientOrientation": np.array([0]),
            "Model": "test_model",
            "Name": "test_name",
            "Orientation": np.array([0]),
            "PixelSizeNm": np.array([1]),
            "ReadoutSpeed": "125",
            "RoiSize": np.array([2048, 2048]),
            "RoiStart": np.array([0, 0]),
            "Shutter": info.CameraShutter.AUTO_NONE,
            "SN": "test_sn",
            "Temperature": "-10",
            "Trigger": info.CameraTrigger.NONE,
            "VerticalFlip": np.array([0]),
        }
    )
    c = info.Camera(
        attrs=camera_attrs,
        _items={"DynamicProperties": dprops, "XAxis": xaxis, "YAxis": yaxis},
    )

    return c


def info_grating_default() -> info.Grating:
    g0_attrs = info.GratingSlotAttrs(
        {
            "BeamSide": info.GratingBeamSide.RIGHT,
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot0",
            "Type": info.GratingType.TRANSMISSION,
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
            "User": "user",
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

    g1_attrs = info.GratingSlotEmptyAttrs(
        {
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot1",
            "Type": info.GratingType.STATIC,
        }
    )
    g1 = info.GratingSlotEmpty(attrs=g1_attrs)

    g2_attrs = info.GratingSlotEmptyAttrs(
        {
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot2",
            "Type": info.GratingType.STATIC,
        }
    )
    g2 = info.GratingSlotEmpty(attrs=g2_attrs)

    g3_attrs = info.GratingSlotEmptyAttrs(
        {
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot3",
            "Type": info.GratingType.STATIC,
        }
    )
    g3 = info.GratingSlotEmpty(attrs=g3_attrs)

    g4_attrs = info.GratingSlotEmptyAttrs(
        {
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot4",
            "Type": info.GratingType.STATIC,
        }
    )
    g4 = info.GratingSlotEmpty(attrs=g4_attrs)

    g5_attrs = info.GratingSlotEmptyAttrs(
        {
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot5",
            "Type": info.GratingType.STATIC,
        }
    )
    g5 = info.GratingSlotEmpty(attrs=g5_attrs)

    g6_attrs = info.GratingSlotEmptyAttrs(
        {
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot6",
            "Type": info.GratingType.STATIC,
        }
    )
    g6 = info.GratingSlotEmpty(attrs=g6_attrs)

    g7_attrs = info.GratingSlotEmptyAttrs(
        {
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot7",
            "Type": info.GratingType.STATIC,
        }
    )
    g7 = info.GratingSlotEmpty(attrs=g7_attrs)

    g8_attrs = info.GratingSlotEmptyAttrs(
        {
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot8",
            "Type": info.GratingType.STATIC,
        }
    )
    g8 = info.GratingSlotEmpty(attrs=g8_attrs)

    g9_attrs = info.GratingSlotEmptyAttrs(
        {
            "FWHM": np.array([1.0]),
            "MaxWavelength": np.array([1000.0]),
            "MinWavelength": np.array([500.0]),
            "Name": "slot9",
            "Type": info.GratingType.STATIC,
        }
    )
    g9 = info.GratingSlotEmpty(attrs=g9_attrs)

    g = info.Grating(
        {
            "0": g0,
            "1": g1,
            "2": g2,
            "3": g3,
            "4": g4,
            "5": g5,
            "6": g6,
            "7": g7,
            "8": g8,
            "9": g9,
        }
    )

    return g


def info_optics_default() -> info.Optics:
    attrs = info.OpticsAttrs({"FocusStatus": np.array([1]), "Objective": "o1"})
    o = info.Optics(attrs=attrs)
    return o


def info_system_default() -> info.System:
    attrs = info.SystemAttrs(
        {"SN": "test_sn", "SoftwareVersion": "0.0.0", "Type": info.SystemType.SYSTEM}
    )
    s = info.System(attrs=attrs)
    return s


def info_default() -> info.Info:
    return info.Info(
        _items={
            "Camera": info_camera_default(),
            "Grating": info_grating_default(),
            "Optics": info_optics_default(),
            "System": info_system_default(),
        }
    )
