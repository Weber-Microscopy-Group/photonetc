"""Extract grating and wavelength settings for each frame in a spectral cube.
Useful to know which settings are needed for a temporal measurement from a reference cube.
"""

import argparse

import h5py
import numpy as np

from photonetc import SpectralCube


def run(path: str):
    with h5py.File(path) as f:
        cube = SpectralCube.from_h5(f)
        settings = np.stack([cube["GratingID"], cube["Wavelength"]], axis=1)
        print(settings)


def main():
    parser = argparse.ArgumentParser(
        prog="extract_frame_settings",
        description="Extract grating and wavelength settings from a spectral cube.",
    )
    parser.add_argument("path", type=str, help="path to spectral cube file")
    args = parser.parse_args()
    run(args.path)


if __name__ == "__main__":
    main()
