"""Convert a series of temporal cubes, each taken at a certain wavelength,
To a series of spectral cubes each representing a certain time.
This requires a reference cube that is spectrally resolved across the same wavelengths
the temporal cubes cover."""

from typing import Union
from glob import glob
import argparse
from photonetc import TemporalCube, SpectralCube, spectralcube
import numpy as np


def validate_reference(
    reference: SpectralCube, cubes: list[TemporalCube]
) -> Union[None, list[float]]:
    """Validates the reference cube contains required wavelengths for the cubes.
    Assumes data cubes have already been validated.

    Args:
        reference (SpectralCube): Reference cube.
        cubes (list[TemporalCube]): Data cubes. Each cube should only represent one wavelength.

    Returns:
        None | list[float]]: Missing reference wavelengths or `None` if all valid.
    """
    wavelengths_cubes = [cube.wavelengths[0] for cube in cubes]
    wavelength_ref = reference.wavelengths
    invalid = []
    for wavelength in wavelengths_cubes:
        if not np.isin(wavelength, wavelength_ref):
            invalid.append(wavelength)

    if len(invalid) == 0:
        return None
    else:
        return invalid


def validate_shapes(cubes: list[TemporalCube]) -> Union[None, list[int]]:
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
            if cube.data.shape == cubes[group[0]].data.shape:
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
) -> Union[None, list[int]]:
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


def validate_wavelengths(cubes: list[TemporalCube]) -> Union[None, list[int]]:
    """Validate all wavelengths in a temporal cube are the same.

    Args:
        cubes (list[TemporalCube]): Cubes to validate.

    Returns:
        None | list[int]: Indices of invalid cubes or `None` if all valid.
    """
    invalid = []
    for idx, cube in enumerate(cubes):
        wavelengths = cube.wavelengths
        if wavelengths is None:
            invalid.append(idx)
            continue

        if not np.ptp(wavelengths[()]) == 0:
            invalid.append(idx)

    if len(invalid) == 0:
        return None
    else:
        return invalid


def validate_gratings(cubes: list[TemporalCube]) -> Union[None, list[int]]:
    """Validate all grating ids in a temporal cube are the same.

    Args:
        cubes (list[TemporalCube]): Cubes to validate.

    Returns:
        None | list[int]: Indices of invalid cubes or `None` if all valid.
    """
    invalid = []
    for idx, cube in enumerate(cubes):
        gratings = cube.grating_ids
        if gratings is None:
            invalid.append(idx)
            continue

        if not np.ptp(gratings[()]) == 0:
            invalid.append(idx)

    if len(invalid) == 0:
        return None
    else:
        return invalid


def temporal_to_spectral(
    reference: SpectralCube, temporal: list[TemporalCube], prefix: str
) -> tuple[list[spectralcube.SpectralCube], np.ndarray]:
    """Convert a list of temporal cubes to a list of stpectral cubes.

    Args:
        reference (SpectralCube): Referernce spectral cube.
        temporal (list[TemporalCube]): Temporal cubes to convert.
        prefix (str): Name prefix.

    Returns:
        tuple[list[spectralcube.SpectralCube], np.ndarray]: tuple of `(spectral cubes, times)`
    """
    temporal.sort(key=lambda cube: cube.wavelengths[0])

    wavelengths = np.array([cube.wavelengths[0] for cube in temporal])
    gratings = np.array([cube.grating_ids[0] for cube in temporal])
    times = np.cumulative_sum(temporal[0].exposure_times)

    wavelengths_ref = reference.wavelengths
    translation_x_ref = reference["Translation_X"]
    translation_y_ref = reference["Translation_Y"]
    w_idx = np.where(np.isin(wavelengths_ref, wavelengths))[0]
    translation_x = translation_x_ref[w_idx]
    translation_y = translation_y_ref[w_idx]

    data = [t.data for t in temporal]
    hypercube = np.stack(data)
    hypercube = np.transpose(hypercube, (1, 0, 2, 3))
    spectral = [hypercube[idx] for idx in range(hypercube.shape[0])]

    ref_data = temporal[0].to_abstract()
    info_ref = ref_data.Info
    cubes = []
    for idx, images in enumerate(spectral):
        info_cube = spectralcube.Cube(
            AcqMode=info_ref.Cube.AcqMode,
            LowerWavelength=wavelengths[0],
            UpperWavelength=wavelengths[-1],
            Name=prefix + str(times[idx]),
            Type=info_ref.Cube.Type,
        )
        info_misc = spectralcube.Misc(ZStage=info_ref.Misc.ZStage)
        info = spectralcube.Info(
            Camera=info_ref.Camera,
            Cube=info_cube,
            Grating=info_ref.Grating,
            Misc=info_misc,
            Optics=info_ref.Optics,
            System=info_ref.System,
        )

        cube = spectralcube.SpectralCube(
            GratingId=gratings,
            Images=images,
            Info=info,
            TimeExposure=times,
            Translation_X=translation_x,
            Translation_Y=translation_y,
            Wavelength=wavelengths,
        )

        cubes.append(cube)

    return (cubes, times)


def save_cubes(cubes: list[spectralcube.SpectralCube], times: np.ndarray, prefix: str):
    """Save cubes to disk.

    Args:
        cubes (list[spectralcube.SpectralCube]): Cubes to save.
        times (np.ndarray): Times corresponding to each cube.
        prefix (str): Name prefix.
    """
    for idx, cube in enumerate(cubes):
        time = f"{times[idx]:.2e}"
        time = time.replace("+", "")
        time = time.replace(".", "_")
        name = f"{prefix}.{idx}.{time}s.h5"
        f = cube.to_h5(name)
        f.close()


def run(reference: str, input: list[str], output: str, time_threshold: float):
    try:
        ref_cube = SpectralCube(reference)
    except ValueError as err:
        raise RuntimeError(f"Could not open reference cube: {err}")

    temporal = []
    for path in input:
        try:
            cube = TemporalCube(path)
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
        raise RuntimeError(f"Invalid graing: {invalid_paths}")

    invalid = validate_timestamps(temporal, time_threshold)
    if invalid is not None:
        invalid_paths = [input[idx] for idx in invalid]
        raise RuntimeError(f"Invalid timestamps: {invalid_paths}")

    invalid = validate_shapes(temporal)
    if invalid is not None:
        invalid_paths = [input[idx] for idx in invalid]
        raise RuntimeError(f"Invalid data shapes: {invalid_paths}")

    invalid = validate_reference(ref_cube, temporal)
    if invalid is not None:
        raise RuntimeError(
            f"Reference cube does not cover required wavelengths; missing {invalid}"
        )

    cubes, times = temporal_to_spectral(ref_cube, temporal, output)
    save_cubes(cubes, times, output)


def main():
    parser = argparse.ArgumentParser(
        prog="temporal_to_spectral",
        description="Combine temporally resolved videos, each at a single wavelength, into spectrally resolved hypercubes, each at a signle time.",
    )

    parser.add_argument("reference", type=str, help="path to the reference cube")
    parser.add_argument("input", type=str, help="glob pattern to match input files")
    parser.add_argument("output", type=str, help="prefix of output filenames.")
    parser.add_argument(
        "-t",
        "--threshold",
        type=float,
        default=1,
        help='Time threshold in ms. Frames must lie within this threshold to be considered "at the same time".',
    )
    args = parser.parse_args()

    input = glob(args.input)
    if len(input) == 0:
        raise RuntimeError("Input pattern does not match any files")
    if args.threshold < 0:
        raise ValueError("Time threshold must be non-negative")

    input = [p for p in input if p != args.reference]
    run(args.reference, input, args.output, args.threshold)


if __name__ == "__main__":
    main()
