import pytest
import photonetc as pe
import pathlib

DATA_PATH = pathlib.Path(__file__).parent.parent / "data/hypercube.h5"


def test_load_file():
    data = pe.Hypercube(DATA_PATH)


def test_properties():
    data = pe.Hypercube(DATA_PATH)

    binning = data.binning
    assert binning[0] == 4
    assert binning[1] == 4

    roi_size = data.camera.roi_size
    assert roi_size.shape == (2,)
    assert roi_size[0] == 1024
    assert roi_size[1] == 1024

    roi_start = data.camera.roi_start
    assert roi_start.shape == (2,)
    assert roi_start[0] == 512
    assert roi_start[1] == 512

    roi = data.camera.roi
    assert roi.shape == (4,)
    assert roi[0] == 512
    assert roi[1] == 512
    assert roi[2] == 1024
    assert roi[3] == 1024

    assert data.camera.pixel_size == 6500.0
    assert data.optics.objective == "20x"
    assert data.optics.magnification == 20.0

    assert data.data.shape == (88, 256, 256)
    assert data.wavelengths.shape == (88,)
    assert data.exposure_times.shape == (88,)

    px_size = data.pixel_size
    assert px_size.shape == (2,)
    assert px_size[0] == 1300.0
    assert px_size[1] == 1300.0
