from math import ceil
from typing import Generator, Optional, Union
from dnn.layers.activations import Activation
from dnn.utils import activation_factory

import numpy as np


def add_activation(activation: Union[Activation, str, None]) -> Activation:
    if activation is None:
        return

    if isinstance(activation, Activation):
        return activation

    return activation_factory(activation)


def compute_conv_padding(
    kernel_size: tuple[int, int], mode: str = "valid"
) -> tuple[int, int]:
    if mode == "same":
        kH, kW = kernel_size
        return ceil((kH - 1) / 2), ceil((kW - 1) / 2)
    return 0, 0


def compute_conv_output_dim(n: int, f: int, p: int, s: int) -> int:
    return int((n - f + 2 * p) / s + 1)


def pad(X: np.ndarray, pad_H: int, pad_W: int) -> tuple[np.ndarray, tuple[int, int]]:
    padded = np.pad(X, ((0, 0), (pad_H, pad_H), (pad_W, pad_W), (0, 0)))

    new_size = padded.shape[1], padded.shape[2]

    return padded, new_size


def slice_idx_generator(
    oH: int, oW: int, sH: int, sW: int
) -> Generator[tuple[int, int], None, None]:
    return ((i * sH, j * sW) for i in range(oH) for j in range(oW))


def vectorize_for_conv(
    X: np.ndarray,
    kernel_size: tuple[int, int],
    stride: tuple[int, int],
    output_size: tuple[int, int],
    reshape: Optional[tuple] = None,
) -> np.ndarray:
    sH, sW = stride
    kH, kW = kernel_size
    oH, oW = output_size

    indices = slice_idx_generator(oH, oW, sH, sW)

    if reshape is None:
        reshape = (-1, X.shape[-1])

    vectorized_ip = np.array(
        [X[:, i : i + kH, j : j + kW].reshape(*reshape) for i, j in indices]
    )

    return vectorized_ip


def accumulate_dX_conv(
    dX_shape: tuple,
    output_size: tuple[int, int],
    dIp: np.ndarray,
    stride: tuple[int, int],
    kernel_size: tuple[int, int],
    reshape: tuple,
    padding: tuple[int, int] = (0, 0),
    moveaxis: bool = True,
) -> np.ndarray:
    kH, kW = kernel_size
    sH, sW = stride

    dX = np.zeros(shape=dX_shape, dtype=np.float32)

    slice_idx = slice_idx_generator(output_size[0], output_size[1], sH, sW)

    for idx, (start_r, start_c) in enumerate(slice_idx):
        end_r, end_c = start_r + kH, start_c + kW
        dX[..., start_r:end_r, start_c:end_c] += dIp[:, idx, ...].reshape(*reshape)

    if padding != (0, 0):
        pH, pW = padding
        dX = dX[..., pH:-pH, pW:-pW]

    if moveaxis is False:
        return dX

    return np.moveaxis(dX, 0, -1)
