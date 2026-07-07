# # Plotting utilities

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Literal
import os
import tempfile
import numpy as np
import plotly.graph_objects as go
import imageio.v3 as imageio
from . import Hypercube, Video

if TYPE_CHECKING:
    from .datacube import Datacube


def animate_frames(
    frames: list[go.Frame],
    duration: float = 100,
    **kwargs,
) -> go.Figure:
    """Animate frames.

    Args:
        frames (list[go.Frame]): Frames to animate.
        duration (float, optional): Duration of each frame in ms. Defaults to 100.
        **kwargs: Passed to `go.Figure.update_layout`.

    Returns:
        go.Figure: Animation.
    """
    for idx, frame in enumerate(frames):
        frame.name = str(idx)

    fig = go.Figure(
        data=frames[0].data,
        frames=frames,
        layout=frames[0].layout,
    )

    fig.update_layout(
        margin=dict(l=50, r=0, t=0, b=150),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        updatemenus=[
            dict(
                type="buttons",
                buttons=[
                    dict(
                        label="Play",
                        method="animate",
                        args=[
                            None,
                            {
                                "frame": {
                                    "duration": duration,
                                    "redraw": True,
                                },
                                "fromcurrent": True,
                            },
                        ],
                    ),
                    dict(
                        label="Pause",
                        method="animate",
                        args=[
                            [None],
                            {
                                "frame": {"duration": 0},
                                "mode": "immediate",
                            },
                        ],
                    ),
                ],
            )
        ],
        sliders=[
            dict(
                steps=[
                    dict(
                        method="animate",
                        args=[
                            [str(idx)],
                            {
                                "frame": {
                                    "duration": 0,
                                    "redraw": True,
                                },
                                "mode": "immediate",
                            },
                        ],
                        label=str(idx),
                    )
                    for idx in range(len(frames))
                ],
                currentvalue=dict(prefix="Frame "),
            )
        ],
        **kwargs,
    )

    return fig


def plot_data_frames(
    cube: Datacube,
    colorscale: str = "Viridis",
    constant_cbar: bool | tuple[float, float] = True,
) -> list[go.Heatmap]:
    """Create plots for each frame of a `Hypercube`.

    Args:
        cube (Hypercube): Data to plot.
        colorscale (str, optional): Color scale. Defaults to "Viridis".
        constant_cbar (bool | tuple[float, float], optional): Set colorbar scaling across all frames.
            If `True`, the color bar is held contstant across all frames using `p05` an `p95`.
            If `False`, the color bar rescales each frame.
            If a tuple of `(min, max)` manually sets the colorbar scale to the given values.
            Defaults to True.

    Returns:
        list[go.Heatmap]: Heatmap of each frame.
    """
    data = cube.data
    zmin = None
    zmax = None
    if constant_cbar is True:
        zmin = np.quantile(data, 0.05)
        zmax = np.quantile(data, 0.95)
    elif isinstance(constant_cbar, tuple):
        zmin, zmax = constant_cbar

    frames = [
        go.Heatmap(
            z=data[frame, :, :],
            colorscale=colorscale,
            zmin=zmin,
            zmax=zmax,
            zauto=False,
        )
        for frame in range(data.shape[0])
    ]

    return frames


FRAME_ANNOTATION = Literal["wavelength", "timestamp"]


def animate(
    cube: Datacube,
    speed: float = 1,
    scale: float = 1,
    colorscale: str = "Viridis",
    constant_cbar: bool | tuple[float, float] = True,
    annotations: Optional[FRAME_ANNOTATION] = None,
) -> go.Figure:
    """Animate a Hypercube.

    Args:
        cube (Hypercube): Data to visualize.
        speed (float, optional): Playback speed. Defaults to 1.
        scale (float, optional): Plot scale. Defaults to 1.
        colorscale (str, optional): Color scale. Defaults to "Viridis".
        constant_cbar (bool | tuple[float, float], optional): Set colorbar scaling across all frames.
            If `True`, the color bar is held contstant across all frames using `p05` an `p95`.
            If `False`, the color bar rescales each frame.
            If a tuple of `(min, max)` manually sets the colorbar scale to the given values.
            Defaults to True.
        annotations (Optional[FRAME_ANNOTATIONS], optional): Annotations to include.

    Returns:
        go.Figure: Animation.
    """
    plots = plot_data_frames(
        cube,
        colorscale=colorscale,
        constant_cbar=constant_cbar,
    )

    data = cube.data
    frame_cnt = data.shape[0]
    annotations_text = None
    if annotations == "wavelength":
        if not isinstance(cube, Hypercube):
            raise TypeError("Datacube does not have wavelength")

        annotations_text = ["{:.0f} nm".format(l) for l in cube.wavelengths]
    elif annotations == "timestamp":
        annotations_text = ["{:.2f} nm".format(l) for l in cube.elapsed]

    annotations_frame = [None for _ in range(frame_cnt)]
    if annotations_text is not None:
        annotations_frame = [
            [
                dict(
                    text=text,
                    xref="paper",
                    yref="paper",
                    x=0.02,
                    y=0.05,
                    showarrow=False,
                    font=dict(size=16, color="white"),
                )
            ]
            for text in annotations_text
        ]

    rows, cols = data.shape[1:]
    width = rows * scale
    height = cols * scale
    scene = dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Intensity",
    )

    frames = [
        go.Frame(
            data=[plot],
            layout=go.Layout(annotations=annotations_frame[idx]),
        )
        for idx, plot in enumerate(plots)
    ]

    duration = float(np.mean(cube.exposure_times) * speed)
    return animate_frames(
        frames,
        duration=duration,
        width=width,
        height=height,
        scene=scene,
    )


def figs_to_gif(
    out: os.PathLike,
    frames: list[go.Figure],
    duration: float = 100,
    progress: bool = False,
):
    """Create a gif.

    Args:
        out (os.PathLike): Output path.
        frames (list[go.Figure]): Frames.
        duration (float, optional): Frame duration in ms. Defaults to 100.
        progress (bool, optional): Print progress. Defaults to False.
    """
    if progress:
        print(f"exporting {len(frames)} frames as a gif")

    imgs = []
    for idx, fig in enumerate(frames):

        with tempfile.NamedTemporaryFile(delete_on_close=False) as tmp:
            fig.write_image(tmp.name, format="png")
            tmp.close()
            img = imageio.imread(tmp.name)
            imgs.append(img)

        if progress:
            complete = int(100 * (idx + 1) / len(frames))
            print(f"{complete}% complete")

    out_str = str(out)
    _, ext = os.path.splitext(out)
    if ext != ".gif":
        out_str = out_str + ".gif"

    fps = 1 / duration
    imageio.imwrite(out_str, imgs, extension=".gif", duration=duration)


def to_gif(
    cube: Datacube,
    out: os.PathLike,
    speed: float = 1,
    scale: float = 1,
    colorscale: str = "Viridis",
    constant_cbar: bool | tuple[float, float] = True,
    annotations: Optional[FRAME_ANNOTATION] = None,
    progress: bool = False,
):
    """Save a cube as a gif.

    Args:
        cube (Hypercube): Data to visualize.
        out (os.PathLike): Output path.
        speed (float, optional): Playback speed. Defaults to 1.
        scale (float, optional): Plot scale. Defaults to 1.
        colorscale (str, optional): Color scale. Defaults to "Viridis".
        constant_cbar (bool | tuple[float, float], optional): Set colorbar scaling across all frames.
            If `True`, the color bar is held contstant across all frames using `p05` an `p95`.
            If `False`, the color bar rescales each frame.
            If a tuple of `(min, max)` manually sets the colorbar scale to the given values.
            Defaults to True.
        annotations (Optional[FRAME_ANNOTATIONS], optional): Annotations to include.
        progress (bool, optional): Print progress. Defaults to False.
    """
    plots = plot_data_frames(cube, colorscale=colorscale, constant_cbar=constant_cbar)

    data = cube.data
    frame_cnt = data.shape[0]
    annotations_text = None
    if annotations == "wavelength":
        if not isinstance(cube, Hypercube):
            raise TypeError("Datacube does not have wavelength")

        annotations_text = ["{:.0f} nm".format(l) for l in cube.wavelengths]
    elif annotations == "timestamp":
        annotations_text = ["{:.2f} nm".format(l) for l in cube.elapsed]

    annotations_frame = [None for _ in range(frame_cnt)]
    if annotations_text is not None:
        annotations_frame = [
            [
                dict(
                    text=text,
                    xref="paper",
                    yref="paper",
                    x=0.02,
                    y=0.05,
                    showarrow=False,
                    font=dict(size=16, color="white"),
                )
            ]
            for text in annotations_text
        ]

    rows, cols = data.shape[1:]
    width = rows * scale
    height = cols * scale
    scene = dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Intensity",
    )

    frames = [
        go.Figure(
            data=[plot],
            layout=go.Layout(
                annotations=annotations_frame[idx],
                width=width,
                height=height,
                yaxis=dict(scaleanchor="x", scaleratio=1),
                scene=scene,
            ),
        )
        for idx, plot in enumerate(plots)
    ]

    duration = float(np.mean(cube.exposure_times) * speed)
    figs_to_gif(
        out,
        frames,
        duration=duration,
        progress=progress,
    )
