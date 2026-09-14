import datetime as dt

import numpy as np

import photonetc_scripts.temporal_to_spectral as transform

from . import create_data_temporal_to_spectral as create


def test_create_data():
    EXPOSURES = 2
    WAVELENGTHS = 2
    WIDTH = 2
    HEIGHT = 2

    oracle = create.create_oracle(EXPOSURES, WAVELENGTHS, WIDTH, HEIGHT)
    assert oracle.shape == (EXPOSURES, WAVELENGTHS, WIDTH, HEIGHT)
    assert oracle[0, 0, 0, 0] == 0
    assert oracle[0, 0, 0, 1] == 1
    assert oracle[0, 0, 1, 0] == 2
    assert oracle[0, 0, 1, 1] == 3
    assert oracle[0, 1, 0, 0] == 10
    assert oracle[0, 1, 0, 1] == 11
    assert oracle[0, 1, 1, 0] == 12
    assert oracle[0, 1, 1, 1] == 13
    assert oracle[1, 0, 0, 0] == 100
    assert oracle[1, 0, 0, 1] == 101
    assert oracle[1, 0, 1, 0] == 102
    assert oracle[1, 0, 1, 1] == 103
    assert oracle[1, 1, 0, 0] == 110
    assert oracle[1, 1, 0, 1] == 111
    assert oracle[1, 1, 1, 0] == 112
    assert oracle[1, 1, 1, 1] == 113

    now = dt.datetime.now()  # noqa: DTZ005
    wavelengths = np.linspace(100, 1000, WAVELENGTHS)
    exposures = np.full((EXPOSURES,), 1 / EXPOSURES)
    reference = create.create_reference_cube(
        now, wavelengths, exposures, width=WIDTH, height=HEIGHT
    )
    assert reference["Images"].shape == (WAVELENGTHS, WIDTH, HEIGHT)

    IDX = 0
    temporal = create.create_temporalcube(IDX, oracle, now, wavelengths[IDX], exposures)
    assert temporal["Images"].shape == (WAVELENGTHS, WIDTH, HEIGHT)
    assert (temporal["Images"] == oracle[:, IDX]).all()

    spectral = create.create_spectralcube(
        IDX, oracle, now, np.cumsum(exposures)[IDX], exposures[IDX], wavelengths
    )
    assert spectral["Images"].shape == (WAVELENGTHS, WIDTH, HEIGHT)
    assert (spectral["Images"] == oracle[IDX]).all()


def test_temporal_to_spectral():
    WIDTH = 10
    HEIGHT = 10
    EXPOSURES = 10
    WAVELENGTHS = 10

    now = dt.datetime.now()  # noqa: DTZ005
    wavelengths = np.linspace(100, 1000, WAVELENGTHS)
    exposures = np.full((EXPOSURES,), 1 / EXPOSURES)
    (ref, temporal, expected) = create.create_all_cubes(
        now, exposures, wavelengths, width=WIDTH, height=HEIGHT
    )
    spectral, _times = transform.temporal_to_spectral(ref, temporal, "", 0.01)

    for exp in expected:
        found = False
        for spec in spectral:
            if (spec["Images"] == exp["Images"]).all():
                found = True
                break
        if not found:
            raise ValueError(
                f"could not find expected spectral cube {exp['Info']['Cube'].attrs['Name']}"
            )
