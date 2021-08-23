from __future__ import annotations
from typing import Optional, Tuple

import numpy as np


class Input:
    """
    Class to represent the input layer of a neural network.

    In a neural network, the input cannot be determined until previous
    layers have done their operation. It also doesn't make sense to lock
    a neural network with particular architecture with a single input.
    This class allows the same architecture to be used with different
    inputs and allows the model to conveniently handle the inherently
    lazy nature of neural networks.

    Attributes
    ----------
    ip: Numpy array or None
        Input that will be provided to other layers.

    shape: tuple
        Expected shape of the input.
    """

    def __init__(self, shape: Tuple, *args, **kwargs) -> None:
        """
        Initializes an Input instance with the given input shape.

        Arguments:
        ----------
        shape: Expected shape of the input.

        Raises
        ----------
        ValueError: When the last dimension of shape is not None.
        """
        if shape[-1] is not None:
            raise ValueError("The last dimension should be set to None.")
        self._shape = shape
        self._ip = None

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(shape={self._shape})"

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def shape(self) -> Tuple:
        """
        The shape of the input of the layer.
        """
        if self.ip is not None:
            return self.ip.shape
        return self._shape

    @property
    def ip(self) -> Optional[np.ndarray]:
        """
        The actual Numpy array that the layer will provide to other layers.
        """
        return self._ip

    @ip.setter
    def ip(self, X: np.ndarray) -> None:
        """
        Setter for the ip property.

        Arguments
        ----------
        X: Numpy array which should be provided to other layers.

        Raises
        ----------
        AttributeError: When the expected shape and shape of X do not match.
        """
        # Make sure the supplied input matches the expected shape
        if X.shape[:-1] != self._shape[:-1]:
            raise AttributeError("The input does not have the expected shape")
        self._ip = X
