from glob import glob
import argparse
from photonetc import  TemporalCube, spectralcube
import numpy as np


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
            if cube.data.shape == cubes[group[0]].data.shape:
                group.append(idx)
                grouped = True
                break

        if not grouped:
            shapes.append([idx])

    if len(shapes) <= 1:
        return None

    longest = (-1, 0)
    for idx, group in enumerate(shapes):
        if len(group) > longest[1]:
            longest = (idx, len(group))

    return [idx for gdx, group in enumerate(shapes) for idx in group if gdx]


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

    if len(times) <= 1:
        return None

    longest = (-1, 0)
    for idx, group in enumerate(times):
        if len(group) > longest[1]:
            longest = (idx, len(group))

    return [idx for gdx, group in enumerate(times) for idx in group if gdx]


def validate_wavelengths(cubes: list[TemporalCube]) -> None | list[int]:
    """Validate all wavelengths in a temporal cube are the same.

    Args:
        cubes (list[TemporalCube]): Cubes to validate.

    Returns:
        None | list[int]: Indices of invalid cubes or `None` if all valid.
    """
    invalid = []
    for idx, cube in enumerate(cubes):
        if not np.ptp(cube.wavelengths) == 0:
            invalid.append(idx)

    if len(invalid) == 0:
        return None
    else:
        return invalid


def temporal_to_spectral(temporal: list[TemporalCube], prefix: str):
    temporal.sort(key=lambda cube: cube.wavelengths[0])
    data = [t.data for t in temporal]
    hypercube = np.stack(data)
    hypercube = np.transpose(hypercube, (1, 0, 2, 3))
    wavelengths = [cube.wavelengths[0] for cube in temporal]
    times = np.cumulative_sum(temporal[0].exposure_times)
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
        info_misc = spectralcube.Misc(
                ZStage=info_ref.Misc.ZStage
        )
        info = spectralcube.Info(
                Camera=info_ref.Camera,
                Cube=info_cube,
                Grating=info_ref.Grating,
                Misc=info_misc,
                Optics=info_ref.Optics,
                System=info_ref.System,
        )

        cube = spectralcube.SpectralCube(
                GratingId=,
                Images=images,
                Info=info,
                Translation_X=,
                Translation_Y=,
                Wavelength=,
        )


    return cubes

def run(input: list[str], output: str, time_threshold: float):
    temporal = []
    for path in input:
        try:
            cube = TemporalCube(path)
            temporal.append(cube)
        except ValueError as err:
            raise RuntimeError(f"[{path}] {err}")

    invalid = validate_shapes(temporal)
    if invalid is not None:
        invalid_paths = [input[idx] for idx in invalid]
        raise RuntimeError(f"Invalid data shapes: {invalid_paths}")

    invalid = validate_timestamps(temporal, time_threshold)
    if invalid is not None:
        invalid_paths = [input[idx] for idx in invalid]
        raise RuntimeError(f"Invalid timestamps: {invalid_paths}")

    invalid = validate_wavelengths(temporal)
    if invalid is not None:
        invalid_paths = [input[idx] for idx in invalid]
        raise RuntimeError(f"Invalid wavelengths: {invalid_paths}")

    temporal_to_spectral(temporal, output)


def main():
    parser = argparse.ArgumentParser(
        prog="temporal_to_spectral",
        description="Combine temporally resolved videos, each at a single wavelength, into spectrally resolved hypercubes, each at a signle time.",
    )

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

    run(input, args.output, args.threshold)


if __name__ == "__main__":
    main()
