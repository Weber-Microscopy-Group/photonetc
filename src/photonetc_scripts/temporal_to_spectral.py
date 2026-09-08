"""Convert a series of temporal cubes, each taken at a certain wavelength,
To a series of spectral cubes each representing a certain time.
This requires a reference cube that is spectrally resolved across the same wavelengths
the temporal cubes cover."""

from __future__ import annotations

import argparse
import os
from glob import glob

import h5py
import numpy as np

from photonetc import SpectralCube, TemporalCube, info


def _temporal_wavelength(cube: TemporalCube) -> float:
    x = cube["Wavelength"]
    assert x is not None
    return float(x[0])


def _temporal_grating(cube: TemporalCube) -> int:
    x = cube["GratingID"]
    assert x is not None
    return int(x[0])


def validate_reference_settings(
    reference: SpectralCube, cubes: list[TemporalCube], wavelength_threshold: float
) -> None | list[tuple[int, float]]:
    """Validates the reference cube wavelengths-grating settings match those of the cubes,
    and that each setting pair only exists once.

    Saftey:
        Assumes data cubes have already been validated.

    Args:
        reference (SpectralCube): Reference cube.
        cubes (list[TemporalCube]): Data cubes. Each cube should only represent one wavelength.
        wavelength_threshold (float): Threshold in nm for wavelengths that are considered the same.

    Returns:
        None | list[tuple[int, float]]: Missing reference grating-wavelengths pairs or `None` if all valid.

    Raises:
        ValueError: Reference cube has a duplicated setting.
    """
    # SAFETY: `validate_wavelength` ensures wavelengths are all present and single valued
    # SAFETY: `validate_gratings` ensures gratings are all present and single valued
    cube_gratings = [_temporal_grating(cube) for cube in cubes]
    cube_wavelengths = [_temporal_wavelength(cube) for cube in cubes]
    ref_gratings = reference["GratingID"]
    ref_wavelengths = reference["Wavelength"]

    invalid = []
    for grating, wavelength in zip(cube_gratings, cube_wavelengths):
        diff_wavelength = np.abs(wavelength - ref_wavelengths)
        valid_wavelength = diff_wavelength <= wavelength_threshold
        valid_grating = ref_gratings == grating
        valid = valid_wavelength & valid_grating
        valid_count = np.count_nonzero(valid)
        if valid_count == 0:
            invalid.append((int(grating), wavelength))
        if valid_count > 1:
            raise ValueError(
                "Invalid reference cube; duplicated grating-wavelength setting"
            )

    if len(invalid) == 0:
        return None
    else:
        return invalid


def validate_cube_settings_duplication(
    cubes: list[TemporalCube], wavelength_threshold: float
) -> None | list[list[int]]:
    """Validates data cube wavelengths-grating settings are not duplicated.

    Saftey:
        Assumes data cubes have already been validated.

    Args:
        reference (SpectralCube): Reference cube.
        cubes (list[TemporalCube]): Data cubes. Each cube should only represent one wavelength.
        wavelength_threshold (float): Threshold in nm for wavelengths that are considered the same.

    Returns:
        None | list[list[int]]: Groups of duplicated cube settings, or None if all valid.

    Notes:
        + It may be that wavelength groups are split up. e.g. For threshold 1,
        it could be that wavelengths [1, 2, 3] are split into two groups.
        This occurs if 1 is keyed first. Then 2 will be included in the group, but 3 will not.
    """
    # SAFETY: `validate_wavelength` ensures wavelengths are all present and single valued
    # SAFETY: `validate_gratings` ensures gratings are all present and single valued
    gratings = [_temporal_grating for cube in cubes]
    wavelengths = [_temporal_wavelength for cube in cubes]

    settings = {}
    for idx in range(len(gratings)):
        grating = gratings[idx]
        wavelength = wavelengths[idx]
        key = (grating, wavelength)
        match = False
        for key_grating, key_wavelength in settings:
            if (
                key_grating == grating
                and abs(wavelength - key_wavelength) <= wavelength_threshold
            ):
                settings[key].append(idx)
                match = True
        if not match:
            settings[key] = [idx]

    invalid = [idx for idx in settings.values() if len(idx) > 1]
    if len(invalid) == 0:
        return None
    else:
        return invalid


def validate_cube_settings(
    reference: SpectralCube, cubes: list[TemporalCube], wavelength_threshold: float
) -> None | list[tuple[int, float]]:
    """Validates the data cubes cover the expected wavelengths-grating settings of the reference cube,
    and that each setting pair only exists once.

    Saftey:
        Assumes data cubes have already been validated.

    Args:
        reference (SpectralCube): Reference cube.
        cubes (list[TemporalCube]): Data cubes. Each cube should only represent one wavelength.
        wavelength_threshold (float): Threshold in nm for wavelengths that are considered the same.

    Returns:
        None | list[]: Missing reference grating-wavelengths pairs or `None` if all valid.

    Raises:
        ValueError: Reference cube has a duplicated setting.
    """
    # SAFETY: `validate_wavelength` ensures wavelengths are all present and single valued
    # SAFETY: `validate_gratings` ensures gratings are all present and single valued
    cube_gratings = np.array([_temporal_grating(cube) for cube in cubes])
    cube_wavelengths = np.array([_temporal_wavelength(cube) for cube in cubes])
    ref_gratings = reference["GratingID"]
    ref_wavelengths = reference["Wavelength"]

    invalid = []
    for grating, wavelength in zip(ref_gratings, ref_wavelengths):
        diff_wavelength = np.abs(wavelength - cube_wavelengths)
        valid_wavelength = diff_wavelength <= wavelength_threshold
        valid_grating = cube_gratings == grating
        valid = valid_wavelength & valid_grating
        valid_count = np.count_nonzero(valid)
        if valid_count == 0:
            invalid.append((grating, wavelength))
        if valid_count > 1:
            raise ValueError(
                "Invalid data cubes; duplicated grating-wavelength setting"
            )

    if len(invalid) == 0:
        return None
    else:
        return invalid


def validate_shapes(cubes: list[TemporalCube]) -> None | list[int]:
    """Validates all cubes have the same shape.

    Args:
        cubes (list[TemporalCube]): Cubes to validate.

    Returns:
        None | list[int]: Indices of invalid cubes or `None` if all valid.
    """
    shapes: list[list[int]] = []
    for idx, cube in enumerate(cubes):
        grouped = False
        for group in shapes:
            if cube["Images"].shape == cubes[group[0]]["Images"].shape:
                group.append(idx)
                grouped = True
                break

        if not grouped:
            shapes.append([idx])

    if len(shapes) > 1:
        longest = (-1, 0)
        for idx, group in enumerate(shapes):
            if len(group) > longest[1]:
                longest = (idx, len(group))

        return [idx for gdx, group in enumerate(shapes) for idx in group if gdx]
    else:
        return None


def validate_timestamps(
    cubes: list[TemporalCube], threshold: float
) -> None | list[int]:
    """Validate all cubes have the same frame exposures.

    Args:
        cubes (list[TemporalCube]): Cubes to validate.
        threshold (float): Time threshold in seconds.

    Returns:
        None | list[int]: Indices of invalid cubes or `None` if all valid.
    """
    times: list[list[int]] = []
    for idx, cube in enumerate(cubes):
        grouped = False
        for group in times:
            diff = np.abs(cube.elapsed - cubes[group[0]].elapsed)
            if np.all(diff <= threshold):
                group.append(idx)
                grouped = True
                break

        if not grouped:
            times.append([idx])

    if len(times) > 1:
        longest = (-1, 0)
        for idx, group in enumerate(times):
            if len(group) > longest[1]:
                longest = (idx, len(group))

        return [idx for gdx, group in enumerate(times) for idx in group if gdx]
    else:
        return None


def validate_wavelengths(cubes: list[TemporalCube]) -> None | list[int]:
    """Validate all wavelengths in a temporal cube are the same.

    Args:
        cubes (list[TemporalCube]): Cubes to validate.

    Returns:
        None | list[int]: Indices of invalid cubes or `None` if all valid.
    """
    invalid = []
    for idx, cube in enumerate(cubes):
        wavelengths = cube["Wavelength"]
        if wavelengths is None:
            invalid.append(idx)
            continue

        wavelength_min = np.min(wavelengths)
        wavelength_max = np.max(wavelengths)
        if wavelength_min != wavelength_max:
            invalid.append(idx)

    if len(invalid) == 0:
        return None
    else:
        return invalid


def validate_gratings(cubes: list[TemporalCube]) -> None | list[int]:
    """Validate all grating ids in a temporal cube are the same.

    Args:
        cubes (list[TemporalCube]): Cubes to validate.

    Returns:
        None | list[int]: Indices of invalid cubes or `None` if all valid.
    """
    invalid = []
    for idx, cube in enumerate(cubes):
        gratings = cube["GratingID"]
        if gratings is None:
            invalid.append(idx)
            continue

        grating_min = np.min(gratings)
        grating_max = np.max(gratings)
        if grating_min != grating_max:
            invalid.append(idx)

    if len(invalid) == 0:
        return None
    else:
        return invalid


def temporal_to_spectral(
    reference: SpectralCube,
    temporal: list[TemporalCube],
    prefix: str,
    wavelength_threshold: float,
) -> tuple[list[SpectralCube], np.ndarray]:
    """Convert a list of temporal cubes to a list of stpectral cubes.

    Args:
        reference (SpectralCube): Referernce spectral cube.
        temporal (list[TemporalCube]): Temporal cubes to convert.
        prefix (str): Name prefix.
        wavelength_threshold (float): Theshold in nm for which wavelengths are considered the same.

    Returns:
        tuple[list[spectralcube.SpectralCube], np.ndarray]: tuple of `(spectral cubes, times)`
    """
    # SAFETY: `validate_wavelength` ensures wavelengths are all present and single valued
    # SAFETY: `validate_gratings` ensures gratings are all present and single valued
    temporal.sort(key=_temporal_wavelength)
    wavelengths = np.array([_temporal_wavelength(cube) for cube in temporal])
    gratings = np.array([_temporal_grating(cube) for cube in temporal])
    times = np.cumulative_sum(temporal[0].elapsed)

    wavelengths_ref = reference["Wavelength"]
    translation_x_ref = reference["Translation_X"]
    translation_y_ref = reference["Translation_Y"]

    wavelength_diff = wavelengths.reshape(-1, 1) - wavelengths_ref
    wavelength_diff = np.abs(wavelength_diff)
    w_udx, w_vdx = np.asarray(wavelength_diff <= wavelength_threshold).nonzero()
    w_idx = np.empty_like(wavelengths)
    for udx, vdx in zip(w_udx, w_vdx):
        w_idx[udx] = [vdx]

    translation_x = translation_x_ref[w_idx]
    translation_y = translation_y_ref[w_idx]

    data = [t["Images"] for t in temporal]
    hypercube = np.stack(data)
    hypercube = np.transpose(hypercube, (1, 0, 2, 3))
    spectral = [hypercube[idx] for idx in range(hypercube.shape[0])]

    info_ref = temporal[0]["Info"]
    cubes = []
    for idx, images in enumerate(spectral):
        info_cube = info.Cube(
            {
                "AcqMode": info_ref["Cube"].attrs["AcqMode"],
                "CreationDate": info_ref["Cube"].attrs["CreationDate"],
                "LowerWavelength": wavelengths[:1],
                "UpperWavelength": wavelengths[-1:],
                "Name": np.array([prefix + str(times[idx])]),
                "Type": info_ref["Cube"].attrs["Type"],
            }
        )
        info_misc = info.Misc({"Z-Stage": info_ref["Misc"]["Z-Stage"]})
        cube_info = info.Info(
            {
                "Camera": info_ref["Camera"],
                "Cube": info_cube,
                "Grating": info_ref["Grating"],
                "Misc": info_misc,
                "Optics": info_ref["Optics"],
                "System": info_ref["System"],
            }
        )

        cube = SpectralCube(
            {
                "GratingID": gratings,
                "Images": images,
                "Info": cube_info,
                "TimeExposure": times,
                "Translation_X": translation_x,
                "Translation_Y": translation_y,
                "Wavelength": wavelengths,
            }
        )

        cubes.append(cube)

    return (cubes, times)


def save_cubes(
    cubes: list[SpectralCube],
    times: np.ndarray,
    outdir: str = ".",
    prefix: str = "",
    overwrite: bool = False,
):
    """Save cubes to disk.

    Args:
        cubes (list[spectralcube.SpectralCube]): Cubes to save.
        times (np.ndarray): Times corresponding to each cube.
        outdir (str, optional): Output directory. Defaults to current directory.
        prefix (str, optional): Name prefix. Defaults to "".
        overwrite (bool, optional): Overwrite existing files. Defaults to False.
    """
    mode = "x"
    if overwrite:
        mode = "w"
    for idx, cube in enumerate(cubes):
        time = f"{times[idx]:.2e}"
        time = time.replace("+", "")
        time = time.replace(".", "_")
        name = f"{idx}.{time}s.h5"
        if prefix != "":
            name = f"{prefix}{name}"

        path = os.path.join(outdir, name)
        with h5py.File(path, mode=mode) as f:
            cube.to_h5(f)


def run(
    reference: str,
    input: list[str],
    time_threshold: float,
    wavelength_threshold: float,
    outdir: str = ".",
    prefix: str = "",
    overwrite: bool = False,
):
    """Transform a spectral set of temporal cubes into a temporal set of spectral cubes.

    Args:
        reference (str): Path to the reference cube. This should be a spectral cube covering the same wavelengths as the temporal cubes.
        input (list[str]): Paths to the temporal cubes.
        output (str): Path of the directory in which to save the output spectral cubes.
        time_threshold (float): Threshold at which to consider cubes to have been taken at the same time, in ms.
        wavelength_threshold (float): Threshold at which to consider wavelngths to be the name. in nm.

    Raises:
        RuntimeError: Reference or data cubes could not be openend.
        RuntimeError: Wavelengths are invalid.
        RuntimeError: Gratings, timestamps, or data shapes are invalid.
        RuntimeError: Duplicate cubes are found.
        RuntimeError: Reference and data cubes do not match.
        ValueError: Time or wavelength threshold are invalid.
    """
    try:
        ref_cube = SpectralCube(reference)
    except ValueError as err:
        raise RuntimeError(f"Could not open reference cube: {err}")

    temporal = []
    for path in input:
        with h5py.File(path) as f:
            try:
                cube = TemporalCube.from_file(f)
                temporal.append(cube)
            except ValueError as err:
                raise RuntimeError(f"[{path}] {err}")

    invalid = validate_wavelengths(temporal)
    if invalid is not None:
        invalid_paths = [input[idx] for idx in invalid]
        raise RuntimeError(f"Invalid wavelengths: {invalid_paths}")

    invalid = validate_gratings(temporal)
    if invalid is not None:
        invalid_paths = [input[idx] for idx in invalid]
        raise RuntimeError(f"Invalid grating: {invalid_paths}")

    invalid = validate_timestamps(temporal, time_threshold)
    if invalid is not None:
        invalid_paths = [input[idx] for idx in invalid]
        raise RuntimeError(f"Invalid timestamps: {invalid_paths}")

    invalid = validate_shapes(temporal)
    if invalid is not None:
        invalid_paths = [input[idx] for idx in invalid]
        raise RuntimeError(f"Invalid data shapes: {invalid_paths}")

    invalid = validate_cube_settings_duplication(temporal, wavelength_threshold)
    if invalid is not None:
        invalid_paths = [[input[jdx] for jdx in idx] for idx in invalid]
        raise RuntimeError(
            f"Data cubes with duplicate grating-wavelength settings found: {invalid_paths}"
        )

    invalid = validate_reference_settings(ref_cube, temporal, wavelength_threshold)
    if invalid is not None:
        invalid = np.sort(invalid, axis=0)
        raise RuntimeError(
            f"Reference cube does not cover required grating-wavelength settings; missing {invalid}"
        )

    invalid = validate_cube_settings(ref_cube, temporal, wavelength_threshold)
    if invalid is not None:
        invalid = np.sort(invalid, axis=0)
        raise RuntimeError(
            f"Data cubes do not cover expected grating-wavelength settings; missing {invalid}"
        )

    if not isinstance(ref_cube["Translation_X"], h5py.Dataset):
        raise ValueError("Reference data 'Translation_X' is invalid")  # noqa: TRY004

    if not isinstance(ref_cube["Translation_Y"], h5py.Dataset):
        raise ValueError("Reference data 'Translation_X' is invalid")  # noqa: TRY004

    cubes, times = temporal_to_spectral(
        ref_cube, temporal, outdir, wavelength_threshold
    )
    save_cubes(cubes, times, outdir, prefix, overwrite)


def main():
    parser = argparse.ArgumentParser(
        prog="temporal_to_spectral",
        description="Combine temporally resolved videos, each at a single wavelength, into spectrally resolved hypercubes, each at a signle time.",
    )

    parser.add_argument("reference", type=str, help="path to the reference cube")
    parser.add_argument("input", type=str, help="glob pattern to match input files")
    parser.add_argument(
        "-o",
        "--out",
        type=str,
        default=".",
        help="output directory, relative or absoulte path",
    )
    parser.add_argument(
        "-p", "--prefix", type=str, default="", help="prefix of output filenames."
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="overwrite existing files"
    )
    parser.add_argument(
        "-t",
        "--time-threshold",
        type=float,
        default=1,
        help='Time threshold in ms. Frames must lie within this threshold to be considered "at the same time".',
    )
    parser.add_argument(
        "-w",
        "--wavelength-threshold",
        type=float,
        default=0.01,
        help="Wavelength threshold in nm. Reference cube wavelengths and temporal cube wavelengths must be within this value to be considered the same.",
    )
    args = parser.parse_args()

    input = glob(args.input)
    if len(input) == 0:
        raise RuntimeError("Input pattern does not match any files")
    if args.time_threshold < 0:
        raise ValueError("Time threshold must be non-negative")
    if args.wavelength_threshold < 0:
        raise ValueError("Wavelength threshold must be non-negative")

    input = [p for p in input if p != args.reference]
    run(
        args.reference,
        input,
        args.time_threshold,
        args.wavelength_threshold,
        args.outdir,
        args.prefix,
        args.overwrite,
    )


if __name__ == "__main__":
    main()
