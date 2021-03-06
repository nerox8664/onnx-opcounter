import torch
from torch import nn
from thop import profile
import pytest
import tempfile
import os
from onnx_opcounter import calculate_params
import onnx


def check_params(model, input):
    macs, params = profile(model, inputs=(input,))

    with tempfile.TemporaryDirectory() as tmp:
        torch.onnx.export(model, input, os.path.join(tmp, "_model.onnx"),
                          verbose=True, input_names=['input'], output_names=['output'])
        onnx_model = onnx.load_model(os.path.join(tmp, "_model.onnx"))
        onnx_params = calculate_params(onnx_model)

        assert int(params) == int(onnx_params)


@pytest.mark.parametrize('kernel_size', [1, 3, 5, 7])
@pytest.mark.parametrize('padding', [0, 1, 3, 5])
@pytest.mark.parametrize('stride', [1])
@pytest.mark.parametrize('bias', [True, False])
@pytest.mark.parametrize('dilation', [1, 2, 3])
@pytest.mark.parametrize('groups', [1, 2, 3])
def test_conv2d_case1(kernel_size, padding, stride, bias, dilation, groups):
    model = nn.Sequential(nn.Conv2d(
        groups * 3, groups, kernel_size=kernel_size, padding=padding,
        stride=stride, bias=bias, dilation=dilation, groups=groups
    ),)
    model.eval()

    input = torch.randn((1, groups * 3, 224, 224))
    check_params(model, input)


@pytest.mark.parametrize('kernel_size', [1, 3, 5, 7])
@pytest.mark.parametrize('padding', [0, 1, 3, 5])
@pytest.mark.parametrize('stride', [1])
@pytest.mark.parametrize('bias', [True, False])
@pytest.mark.parametrize('dilation', [1, 2, 3])
@pytest.mark.parametrize('groups', [1, 2, 3])
def test_convtranspose2d_case1(kernel_size, padding, stride, bias, dilation, groups):
    model = nn.Sequential(nn.ConvTranspose2d(
        groups * 3, groups, kernel_size=kernel_size, padding=padding,
        stride=stride, bias=bias, dilation=dilation, groups=groups
    ),)
    model.eval()

    input = torch.randn((1, groups * 3, 224, 224))
    check_params(model, input)


@pytest.mark.parametrize('inputs', [1, 32, 64, 128, 256])
@pytest.mark.parametrize('outputs', [1, 32, 64, 128])
@pytest.mark.parametrize('bias', [True, False])
def test_linear_case1(inputs, outputs, bias):
    model = nn.Sequential(nn.Linear(
        inputs, outputs, bias=bias
    ),)
    model.eval()

    input = torch.randn((1, inputs))
    check_params(model, input)


@pytest.mark.parametrize('planes', [1, 32, 64, 128, 256])
@pytest.mark.parametrize('size', [1, 32, 64, 128, 256])
@pytest.mark.parametrize('affine', [True, False])
def test_bn_case1(planes, size, affine):
    pytest.skip('PyTorch OpCounter produces wrong results')
    model = nn.Sequential(nn.BatchNorm1d(
        planes, affine=affine
    ),)
    model.eval()

    input = torch.randn((1, planes, size))
    check_params(model, input)
