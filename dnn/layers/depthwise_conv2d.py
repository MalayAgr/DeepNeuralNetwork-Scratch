from typing import Any, Optional, Tuple, Union

import numpy as np

from .activations import Activation
from .base_layer import LayerInput
from .conv2d import Conv2D
from .utils import (
    backprop_bias_conv,
    backprop_ip_depthwise_conv2d,
    backprop_kernel_depthwise_conv2d,
    depthwise_convolve2d,
)


class DepthwiseConv2D(Conv2D):
    str_attrs = Conv2D.str_attrs[1:]

    def __init__(
        self,
        ip: LayerInput,
        *args,
        kernel_size: Tuple[int, int],
        stride: Tuple[int, int] = (1, 1),
        activation: Optional[Union[Activation, str]] = None,
        multiplier: int = 1,
        padding: str = "valid",
        initializer: str = "he",
        use_bias: bool = True,
        name: str = None,
        **kwargs
    ) -> None:
        super().__init__(
            ip=ip,
            filters=multiplier,
            kernel_size=kernel_size,
            stride=stride,
            activation=activation,
            padding=padding,
            initializer=initializer,
            use_bias=use_bias,
            name=name,
        )

        self.multiplier = multiplier

    def fans(self) -> Tuple[int, int]:
        fan_in, fan_out = super().fans()

        return fan_in, fan_out * self.ip_C

    def build(self) -> Any:
        super().build()

        if self.use_bias:
            remaining = (self.multiplier * self.ip_C) - self.biases.shape[0]
            extra = self._add_param(shape=(remaining, 1, 1, 1), initializer="zeros")
            self.biases = np.concatenate((self.biases, extra))

    def output_shape(self) -> Tuple:
        shape = super().output_shape()

        if self.activations is not None:
            return shape

        c, h, w, m = shape

        return c * self.ip_C, h, w, m

    def conv_func(
        self,
    ) -> Union[
        Tuple[np.ndarray, np.ndarray, np.ndarray],
        Tuple[np.ndarray, np.ndarray, None],
        Tuple[np.ndarray, None, np.ndarray],
        Tuple[np.ndarray, None, None],
    ]:
        return depthwise_convolve2d(
            X=self.input(),
            kernel=self.kernels,
            stride=self.stride,
            padding=(self.p_H, self.p_W),
            return_vec_ip=True,
            return_vec_kernel=True,
        )

    def _reshape_dZ(self, dZ: np.ndarray) -> np.ndarray:
        shape = (dZ.shape[-1], -1, self.ip_C, self.multiplier)

        dZ = np.swapaxes(dZ, -1, 0).reshape(*shape)

        dZ = np.moveaxis(dZ, 1, 2)

        return dZ

    def _compute_dW(self, dZ: np.ndarray) -> np.ndarray:
        return backprop_kernel_depthwise_conv2d(
            ip=self._vec_ip,
            grad=dZ,
            kernel_size=self.kernel_size,
            multiplier=self.multiplier,
        )

    def _compute_dB(self, dZ: np.ndarray) -> np.ndarray:
        return backprop_bias_conv(grad=dZ, axis=(0,), reshape=self.biases.shape[1:])

    def _compute_dVec_Ip(self, dZ: np.ndarray) -> np.ndarray:
        return backprop_ip_depthwise_conv2d(grad=dZ, kernel=self._vec_kernel)
