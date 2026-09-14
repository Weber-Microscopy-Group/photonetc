"""Create test data for the temporal to spectral script."""

import argparse
import datetime as dt
import os
import warnings

import h5py
import numpy as np

from photonetc import SpectralCube, TemporalCube, info, utils


def strftime(datetime: dt.datetime) -> str:
    """Format datetime for datacube.

    Args:
        datetime (dt.datetime): Datetime.

    Returns:
        str: Formatted string.
    """
    TIMESTAMP_FMT = "%Y/%m/%d %H:%M:%S.%f"
    return datetime.strftime(TIMESTAMP_FMT)[:-3]


def save_cube(cube, outdir: str = ".", overwrite: bool = False):
    mode = "x"
    if overwrite:
        mode = "w"

    cname = cube["Info"]["Cube"].attrs["Name"][0]
    fname = f"{cname}.h5"
    path = os.path.join(outdir, fname)

    with h5py.File(path, mode=mode) as f:
        cube.to_h5(f)


def create_reference_cube_info(
    wavelengths: np.ndarray,
    width: int = 1024,
    height: int = 1024,
    prefix: str = "",
) -> info.Info:
    wdiff = np.diff(wavelengths)
    assert np.all(np.isclose(wdiff, wdiff[0]))

    cinfo = utils.info_default()
    roi_size = np.array([width, height], dtype=np.int32)
    roi_start = np.floor((cinfo["Camera"].attrs["CaptorSize"] - roi_size) / 2).astype(
        np.int32
    )
    cinfo["Camera"].attrs["RoiSize"] = roi_size
    cinfo["Camera"].attrs["RoiStart"] = roi_start
    cinfo["Cube"].set_attr("Name", "reference")
    cinfo["Cube"].set_attr("AcqMode", info.CubeAcqMode.HYPERSPECTRAL.value)
    cinfo["Cube"].set_attr("FixedTimeExposure", 1)
    cinfo["Cube"].set_attr("LowerWavelength", wavelengths[0])
    cinfo["Cube"].set_attr("UpperWavelength", wavelengths[-1])
    cinfo["Cube"].set_attr("WavelengthStep", wdiff[0])
    cinfo["Cube"]["ZAxis"] = info.CubeZAxis(
        {"Key": np.array([info.CubeZAxisKey.INDEX])}
    )

    return cinfo


def create_reference_cube(
    now: dt.datetime,
    wavelengths: np.ndarray,
    exposures: np.ndarray,
    width: int = 1024,
    height: int = 1024,
    prefix: str = "",
) -> SpectralCube:
    cinfo = create_reference_cube_info(wavelengths, width, height, prefix)
    return SpectralCube(
        {
            "GratingID": np.full(wavelengths.shape, 0, dtype=np.int32),
            "Images": np.zeros((wavelengths.shape[0], width, height)),
            "Info": cinfo,
            "TimeExposure": exposures,
            "Translation_X": np.full(wavelengths.shape, 0),
            "Translation_Y": np.full(wavelengths.shape, 0),
            "Wavelength": wavelengths,
        }
    )


def create_oracle(
    exposures: int,
    wavelengths: int,
    width: int,
    height: int,
) -> np.ndarray:
    """Creates a datacube representing the values of each pixel in a temporally and spectrally resolved cube.

    Args:
        exposures (int): Number of exposures.
        wavelengths (int): Number of wavelengths.
        width (int): Image width.
        height (int): Image height.

    Returns:
        np.ndarray: Cube whose values are non-overlappng so the index can be found from its value.
        Values are calculated as `e * exposure_scale + w * wavelength_scale + i * width + j` where
        an element is indexed by `(e, w, i, j)`, `e` is the exposure index, `w` is the wavelength index, `i` is the
        image column index, and `j` is the image row index. `wavelength_scale` is `10^N` where `N` is `ceil(log10(width * height))`
        and `exposure_scale` is `10^M` where `M` is `ceil(log10(width * height * wavelengths))`.
    """
    k_scale = width
    j_scale = np.ceil(np.log10(width * height))
    i_scale = np.ceil(np.log10(width * height * wavelengths))
    i_scale = max(i_scale, j_scale + 1)
    j_scale = int(10**j_scale)
    i_scale = int(10**i_scale)
    return np.fromfunction(
        lambda i, j, k, l: i * i_scale + j * j_scale + k * k_scale + l,
        (exposures, wavelengths, width, height),
    )


def create_temporalcube_bandpass_info(
    wavelength: float,
    width: int = 1024,
    height: int = 1024,
    prefix: str = "",
) -> info.Info:
    cinfo = utils.info_default()
    name_wavelength = f"{wavelength:.2f}"
    name_wavelength = name_wavelength.replace(".", "_")
    name = f"{prefix}{name_wavelength}nm"
    roi_size = np.array([width, height], dtype=np.int32)
    roi_start = np.floor((cinfo["Camera"].attrs["CaptorSize"] - roi_size) / 2).astype(
        np.int32
    )
    cinfo["Camera"].attrs["RoiSize"] = roi_size
    cinfo["Camera"].attrs["RoiStart"] = roi_start
    cinfo["Cube"].set_attr("Name", name)
    cinfo["Cube"].set_attr("AcqMode", info.CubeAcqMode.VIDEO.value)
    cinfo["Cube"].set_attr("BroadBand", 0)
    cinfo["Cube"]["ZAxis"] = info.CubeZAxis(
        {"Key": np.array([info.CubeZAxisKey.INDEX])}
    )

    return cinfo


def create_temporalcube(
    idx: int,
    oracle: np.ndarray,
    now: dt.datetime,
    wavelength: float,
    exposures: np.ndarray,
    prefix: str = "",
) -> TemporalCube:
    assert oracle.shape[0] == exposures.shape[0]

    (width, height) = oracle.shape[-2:]
    images = oracle[:, idx]
    timestamp = np.array(
        [strftime(now + dt.timedelta(seconds=diff)) for diff in np.cumsum(exposures)]
    )
    cinfo = create_temporalcube_bandpass_info(
        wavelength, width=width, height=height, prefix=prefix
    )

    return TemporalCube(
        {
            "Angle": np.zeros(exposures.shape),
            "GratingID": np.full(exposures.shape, 0, dtype=np.int32),
            "Images": images,
            "Info": cinfo,
            "TimeExposure": exposures,
            "Timestamp": timestamp,
            "Wavelength": np.full(exposures.shape, wavelength),
        }
    )


def create_spectralcube_info(
    elapsed: float,
    wavelengths: np.ndarray,
    width: int = 1024,
    height: int = 1024,
    prefix: str = "",
) -> info.Info:
    cinfo = utils.info_default()
    wdiff = np.diff(wavelengths)
    assert np.all(np.isclose(wdiff, wdiff[0]))

    cinfo = utils.info_default()
    roi_size = np.array([width, height], dtype=np.int32)
    roi_start = np.floor((cinfo["Camera"].attrs["CaptorSize"] - roi_size) / 2).astype(
        np.int32
    )
    cinfo["Camera"].attrs["RoiSize"] = roi_size
    cinfo["Camera"].attrs["RoiStart"] = roi_start
    cinfo["Cube"].set_attr("Name", f"{prefix}{elapsed:.2f}s")
    cinfo["Cube"].set_attr("AcqMode", info.CubeAcqMode.HYPERSPECTRAL.value)
    cinfo["Cube"].set_attr("FixedTimeExposure", 1)
    cinfo["Cube"].set_attr("LowerWavelength", wavelengths[0])
    cinfo["Cube"].set_attr("UpperWavelength", wavelengths[-1])
    cinfo["Cube"].set_attr("WavelengthStep", wdiff[0])
    cinfo["Cube"]["ZAxis"] = info.CubeZAxis(
        {"Key": np.array([info.CubeZAxisKey.INDEX])}
    )
    return cinfo


def create_spectralcube(
    idx: int,
    oracle: np.ndarray,
    now: dt.datetime,
    elapsed: float,
    exposure: float,
    wavelengths: np.ndarray,
    prefix: str = "",
) -> SpectralCube:
    assert oracle.shape[1] == wavelengths.shape[0]

    (width, height) = oracle.shape[-2:]
    images = oracle[idx]
    cinfo = create_spectralcube_info(
        elapsed, wavelengths, width=width, height=height, prefix=prefix
    )
    return SpectralCube(
        {
            "GratingID": np.full(wavelengths.shape, 0, dtype=np.int32),
            "Images": images,
            "Info": cinfo,
            "TimeExposure": np.full(wavelengths.shape, exposure),
            "Translation_X": np.zeros(wavelengths.shape),
            "Translation_Y": np.zeros(wavelengths.shape),
            "Wavelength": wavelengths,
        }
    )


def create_all_cubes(
    now: dt.datetime,
    exposures: np.ndarray,
    wavelengths: np.ndarray,
    width: int = 1024,
    height: int = 1024,
    prefix: str = "",
) -> tuple[SpectralCube, list[TemporalCube], list[SpectralCube]]:
    oracle = create_oracle(exposures.shape[0], wavelengths.shape[0], width, height)
    ref = create_reference_cube(
        now,
        wavelengths,
        exposures,
        width=width,
        height=height,
    )

    temporal = [
        create_temporalcube(
            idx,
            oracle,
            now,
            wavelength,
            exposures,
            prefix=prefix,
        )
        for idx, wavelength in enumerate(wavelengths)
    ]
    spectral = [
        create_spectralcube(
            idx,
            oracle,
            now,
            elapsed,
            exposure,
            wavelengths,
            prefix=prefix,
        )
        for idx, (exposure, elapsed) in enumerate(zip(exposures, np.cumsum(exposures)))
    ]

    return (ref, temporal, spectral)


def run(
    exposures: np.ndarray,
    wavelengths: np.ndarray,
    width: int = 1024,
    height: int = 1024,
    outdir: str = ".",
    prefix: str = "",
    overwrite: bool = False,
    dryrun: bool = False,
):
    """Create test data for the temporal to spectral script.
    Image values scale from 0 to 1, increasing with time and wavelength.

    Args:
        exposures (np.ndarray): Elapsed time for each frame.
        wavelengths (np.ndarray): Cube wavelengths.
        width (int, optional): Image width in pixels. Defaults to 1024.
        height (int, optional): Image height in pixels. Defaults to 1024.
        outdir (str, optional): Output directory of the temporal files. Defaults to ".".
        prefix (str, optional): Prefix for file names. Default to "".
        overwrite(bool, optional): Overwrite files if they exist. Defaults to False.
        dryrun(bool, optional): Do not save cubes. Used for debugging. Defaults to False.
    """
    assert exposures.ndim == 1
    assert wavelengths.ndim == 1

    now = dt.datetime.now().replace(microsecond=0)  # noqa: DTZ005
    (ref, temporal, spectral) = create_all_cubes(
        now,
        exposures,
        wavelengths,
        width=width,
        height=height,
        prefix=prefix,
    )
    if not dryrun:
        save_cube(ref, outdir=outdir, overwrite=overwrite)
        for cube in temporal:
            save_cube(cube, outdir=outdir, overwrite=overwrite)
        for cube in spectral:
            save_cube(cube, outdir=outdir, overwrite=overwrite)


def main():
    parser = argparse.ArgumentParser(
        prog="create_data_temporal_to_spectral",
        description="Create test data for the temporal to spectral script.",
    )
    parser.add_argument(
        "-f", "--frames", type=int, default=10, help="number of frames; defaults to 10"
    )
    parser.add_argument(
        "-w",
        "--wavelengths",
        type=int,
        default=10,
        help="number of wavelengths; defaults to 10",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1024,
        help="pixel width of images; defaults to 1024",
    )
    parser.add_argument(
        "--height",
        type=int,
        default=1024,
        help="pixel height of images; defaults to 1024",
    )
    parser.add_argument(
        "-o",
        "--outdir",
        type=str,
        default=".",
        help="output directory, relative or absoulte path; defaults to current directory",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        default="",
        help='prefix for file names; defaults to ""',
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="overwrite existing files"
    )
    parser.add_argument(
        "--dryrun", action="store_true", help="do not save cubes; used for debugging"
    )
    # TODO: Add grating options and crossover point.
    args = parser.parse_args()

    positive_args = []
    if args.frames < 1:
        positive_args.append("frames")
    if args.wavelengths < 1:
        positive_args.append("wavelengths")
    if args.width < 1:
        positive_args.append("width")
    if args.height < 1:
        positive_args.append("height")
    if len(positive_args) > 0:
        raise ValueError(f"argument(s) {positive_args} must be larger than 0")

    if args.frames < 2 or args.wavelengths < 2:
        warnings.warn("trivial cube")

    exposures = np.full((args.frames,), 1 / args.frames)
    wavelengths = np.linspace(start=400, stop=1000, num=args.wavelengths)

    os.makedirs(args.outdir, exist_ok=True)
    run(
        exposures,
        wavelengths,
        width=args.width,
        height=args.height,
        outdir=args.outdir,
        prefix=args.prefix,
        overwrite=args.overwrite,
        dryrun=args.dryrun,
    )


if __name__ == "__main__":
    main()
