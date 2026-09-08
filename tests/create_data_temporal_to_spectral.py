"""Create test data for the temporal to spectral script."""

import argparse
import datetime as dt
import os
import warnings

import h5py
import numpy as np

from photonetc import TemporalCube, info, utils


def create_temporalcube_bandpass_info(
    wavelength: float, width: int = 1024, height: int = 1024, prefix: str = ""
) -> info.Info:
    cinfo = utils.info_default()
    name_wavelength = f"{wavelength:.2f}"
    name = f"{prefix}{name_wavelength}nm"
    name = name.replace(".", "_")
    roi_size = np.array([width, height], dtype=np.int32)
    roi_start = np.floor((cinfo["Camera"].attrs["CaptorSize"] - roi_size) / 2).astype(
        np.int32
    )
    cinfo["Camera"].attrs["RoiSize"] = roi_size
    cinfo["Camera"].attrs["RoiStart"] = roi_start
    cinfo["Cube"].attrs["Name"] = np.array([name], dtype=h5py.string_dtype())
    cinfo["Cube"].attrs["AcqMode"] = np.array([info.CubeAcqMode.VIDEO.value])
    cinfo["Cube"].attrs["BroadBand"] = np.array([0])
    cinfo["Cube"]["ZAxis"] = info.CubeZAxis(
        {"Key": np.array([info.CubeZAxisKey.INDEX])}
    )

    return cinfo


def create_temporalcube(
    now: dt.datetime,
    wavelength: float,
    exposures: np.ndarray,
    width: int = 1024,
    height: int = 1024,
    prefix: str = "",
) -> TemporalCube:
    TIMESTAMP_FMT = "%Y/%m/%d %H:%M:%S.%f"
    timestamp = np.array(
        [
            (now + dt.timedelta(seconds=diff)).strftime(TIMESTAMP_FMT)[:-3]
            for diff in np.cumsum(exposures)
        ]
    )

    images = np.zeros((exposures.shape[0], width, height))
    info = create_temporalcube_bandpass_info(
        wavelength, width=width, height=height, prefix=prefix
    )

    return TemporalCube(
        {
            "Angle": np.zeros(exposures.shape),
            "GratingID": np.full(exposures.shape, "0"),
            "Images": images,
            "Info": info,
            "TimeExposure": exposures,
            "Timestamp": timestamp,
            "Wavelength": np.full(exposures.shape, wavelength),
        }
    )


def save_cube(cube: TemporalCube, outdir: str = ".", overwrite: bool = False):
    mode = "x"
    if overwrite:
        mode = "w"

    cname = cube["Info"]["Cube"].attrs["Name"][0]
    fname = f"{cname}.h5"
    path = os.path.join(outdir, fname)

    with h5py.File(path, mode=mode) as f:
        cube.to_h5(f)


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
    for wavelength in wavelengths:
        cube = create_temporalcube(
            now,
            wavelength,
            exposures,
            width=width,
            height=height,
        )
        if not dryrun:
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

    exposures = np.empty(args.frames)
    exposures.fill(1 / args.frames)
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
