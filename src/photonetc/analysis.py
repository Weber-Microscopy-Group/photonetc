# # Data analysis

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Callable
import numpy as np
from scipy.optimize import curve_fit

if TYPE_CHECKING:
    from .datacube import Datacube


def fit_frames(
    data: np.ndarray,
    fn: Callable,
    p0: Callable[[np.ndarray], tuple] | tuple | None = None,
    bounds: (
        Callable[[np.ndarray], tuple[tuple, tuple]] | tuple[tuple, tuple] | tuple
    ) = (-np.inf, np.inf),
    **kwargs,
) -> list[None | tuple[np.ndarray, np.ndarray]]:
    """Fits each frame of a datacube indexed as `(frame, x, y)`.
    Fit function is applied to each frame, fitting the XY plane.

    Args:
        data (np.ndarray): Datacube indexed as `(frame, x, y)`.
        fn (Callable): Fit function. Sent to `scipy.optimize.curve_fit`.
        p0 Callable[[np.ndarray], tuple] | tuple | None, optional): Initial parameters. Defaults to None.
        bounds (Callable[[np.ndarray], tuple[tuple, tuple]] | tuple[tuple, tuple] | tuple, optional): Parameter bounds. Defaults to None.
        **kwargs: Arguments sent to `scipy.optimize.curve_fit`.

    Returns:
        list[None | tuple[np.ndarray, np.ndarray]]: Fit parameters for each frame.
        If a frame fit fails, then `None`.
    """
    frame_cnt, i_cnt, j_cnt = data.shape
    xy = np.meshgrid(np.arange(i_cnt), np.arange(j_cnt), indexing="ij")
    xy = (
        xy[0].ravel(),
        xy[1].ravel(),
    )
    fits: list[None | tuple[np.ndarray, np.ndarray]] = [None for _ in range(frame_cnt)]
    for idx in range(frame_cnt):
        frame = data[idx]
        p0_frame = None
        if isinstance(p0, tuple):
            p0_frame = p0
        elif isinstance(p0, Callable):
            p0_frame = p0(frame)

        if isinstance(bounds, Callable):
            bounds_frame = bounds(frame)
        else:
            bounds_frame = bounds

        try:
            fit = curve_fit(
                fn,
                xy,
                frame.ravel(),
                p0=p0_frame,
                bounds=bounds_frame,
                **kwargs,
            )

            fits[idx] = fit
        except Exception:
            continue

    return fits


def fit_pixels(
    data: np.ndarray,
    fn: Callable,
    p0: Callable[[np.ndarray], tuple] | tuple | None = None,
    bounds: (
        Callable[[np.ndarray], tuple[tuple, tuple]] | tuple[tuple, tuple] | tuple
    ) = (-np.inf, np.inf),
    **kwargs,
) -> list[list[None | tuple[np.ndarray, np.ndarray]]]:
    """Fits each pixel of a datacube indexed as `(frame, x, y)`.
    Fit function is applied to each pixel, fitting through the frames.

    Args:
        data (np.ndarray): Datacube indexed as `(frame, x, y)`.
        fn (Callable): Fit function. Sent to `scipy.optimize.curve_fit`.
        p0 (Callable[[np.ndarray], tuple] | tuple | None, optional): Initial parameters. Defaults to None.
        bounds (Callable[[np.ndarray], tuple[tuple, tuple]] | tuple[tuple, tuple] | tuple, optional): Parameter bounds. Defaults to None.
        **kwargs: Arguments sent to `scipy.optimize.curve_fit`.

    Returns:
        list[list[None | tuple[np.ndarray, np.ndarray]]]: Fit parameters for each pixel.
        If a frame fit fails, then `None`.
    """
    frame_cnt, i_cnt, j_cnt = data.shape
    x = np.arange(frame_cnt)
    fits: list[list[None | tuple[np.ndarray, np.ndarray]]] = [
        [None for _ in range(j_cnt)] for _ in range(i_cnt)
    ]
    for idx in range(i_cnt):
        for jdx in range(j_cnt):
            pixel = data[:, idx, jdx]
            p0_pixel = None
            if isinstance(p0, tuple):
                p0_pixel = p0
            elif isinstance(p0, Callable):
                p0_pixel = p0(pixel)

            if isinstance(bounds, Callable):
                bounds_pixel = bounds(pixel)
            else:
                bounds_pixel = bounds

            try:
                fit = curve_fit(
                    fn,
                    x,
                    pixel,
                    p0=p0_pixel,
                    bounds=bounds_pixel,
                    **kwargs,
                )

                fits[idx][jdx] = fit
            except Exception:
                continue

    return fits
