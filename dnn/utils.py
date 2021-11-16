from __future__ import annotations

import math
from collections.abc import Iterator
from typing import Tuple

import numpy as np
from numba import njit

from dnn.loss import Loss


def loss_factory(loss: str) -> Loss:
    registry = Loss.get_loss_classes()
    cls = registry.get(loss)
    if cls is None:
        raise ValueError("Loss with this name does not exist")
    return cls()


@njit
def generate_batches(
    X: np.ndarray, Y: np.ndarray, batch_size: int, shuffle: bool = True
) -> Iterator[Tuple[np.ndarray, np.ndarray, int]]:
    num_samples = X.shape[-1]

    if batch_size > num_samples:
        msg = "The batch size is greater than the number of samples in the dataset."
        raise ValueError(msg)

    num_full_batches = math.floor(num_samples / batch_size)

    if shuffle is True:
        perm = np.random.permutation(num_samples)
        X, Y = X[..., perm], Y[..., perm]

    if num_full_batches == 1:
        yield X, Y, num_samples
        return

    for idx in range(num_full_batches):
        start = idx * batch_size
        end = (idx + 1) * batch_size
        yield X[..., start:end], Y[..., start:end], batch_size

    if num_samples % batch_size != 0:
        start = batch_size * num_full_batches
        yield X[..., start:], Y[..., start:], num_samples - start
