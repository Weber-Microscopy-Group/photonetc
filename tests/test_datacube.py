import pytest
import photonetc as pe
import pathlib

DATA_PATH_HYPERCUBE = pathlib.Path(__file__).parent.parent / "data/hypercube.h5"
DATA_PATH_VIDEO = pathlib.Path(__file__).parent.parent / "data/video.h5"


def test_hypercube_properties():
    PX_SIZE_NM = 6500
    MAGNIFICATION = 20
    BINS = 4
    FRAME_COUNT = 88
    X_COUNT = 1024
    Y_COUNT = 1024
    X_START = 512
    Y_START = 512

    cube = pe.Hypercube(DATA_PATH_HYPERCUBE)

    binning = cube.binning
    assert binning[0] == BINS
    assert binning[1] == BINS

    roi_size = cube.camera.roi_size
    assert roi_size.shape == (2,)
    assert roi_size[0] == X_COUNT
    assert roi_size[1] == Y_COUNT

    roi_start = cube.camera.roi_start
    assert roi_start.shape == (2,)
    assert roi_start[0] == X_START
    assert roi_start[1] == Y_START

    roi = cube.camera.roi
    assert roi.shape == (4,)
    assert roi[0] == X_START
    assert roi[1] == Y_START
    assert roi[2] == X_COUNT
    assert roi[3] == Y_COUNT

    assert cube.camera.pixel_size == PX_SIZE_NM
    assert cube.optics.objective == "20x"
    assert cube.optics.magnification == MAGNIFICATION

    assert cube.data.shape == (FRAME_COUNT, X_COUNT / BINS, Y_COUNT / BINS)
    assert cube.wavelengths.shape == (FRAME_COUNT,)
    assert cube.exposure_times.shape == (FRAME_COUNT,)

    px_size = cube.pixel_size
    assert px_size.shape == (2,)
    assert px_size[0] == PX_SIZE_NM * BINS / MAGNIFICATION
    assert px_size[1] == PX_SIZE_NM * BINS / MAGNIFICATION


def test_video_properties():
    PX_SIZE_NM = 6500
    MAGNIFICATION = 20
    BINS = 4
    FRAME_COUNT = 18
    X_COUNT = 1024
    Y_COUNT = 1024
    X_START = 512
    Y_START = 512

    cube = pe.Video(DATA_PATH_VIDEO)

    binning = cube.binning
    assert binning[0] == BINS
    assert binning[1] == BINS

    roi_size = cube.camera.roi_size
    assert roi_size.shape == (2,)
    assert roi_size[0] == X_COUNT
    assert roi_size[1] == Y_COUNT

    roi_start = cube.camera.roi_start
    assert roi_start.shape == (2,)
    assert roi_start[0] == X_START
    assert roi_start[1] == Y_START

    roi = cube.camera.roi
    assert roi.shape == (4,)
    assert roi[0] == X_START
    assert roi[1] == Y_START
    assert roi[2] == X_COUNT
    assert roi[3] == Y_COUNT

    assert cube.camera.pixel_size == PX_SIZE_NM
    assert cube.optics.objective == "20x"
    assert cube.optics.magnification == MAGNIFICATION

    assert cube.data.shape == (FRAME_COUNT, X_COUNT / BINS, Y_COUNT / BINS)
    assert len(cube.timestamps) == FRAME_COUNT
    assert cube.exposure_times.shape == (FRAME_COUNT,)

    px_size = cube.pixel_size
    assert px_size.shape == (2,)
    assert px_size[0] == PX_SIZE_NM * BINS / MAGNIFICATION
    assert px_size[1] == PX_SIZE_NM * BINS / MAGNIFICATION
