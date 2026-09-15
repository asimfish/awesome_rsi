"""Assistant-authored reference Triton candidates. FP32 contiguous tensors only."""
import torch
import triton
import triton.language as tl
from triton.language.extra.cuda import libdevice

BLOCK = 1024
SOFTMAX_WARPS = 4

@triton.jit
def pointwise(X, Y, N: tl.constexpr, OP: tl.constexpr, TILE: tl.constexpr):
    offset = tl.program_id(0) * TILE + tl.arange(0, TILE)
    x = tl.load(X + offset, offset < N, other=0)
    if OP == 0:
        value = tl.maximum(x, 0)
    else:
        value = 0.5 * x * (1.0 + libdevice.tanh(0.7978845608028654 * (x + 0.044715 * x * x * x)))
    tl.store(Y + offset, value, offset < N)

@triton.jit
def row_softmax(X, Y, N: tl.constexpr, TILE: tl.constexpr):
    row = tl.program_id(0)
    col = tl.arange(0, TILE)
    x = tl.load(X + row * N + col, col < N, other=-float('inf'))
    exp = tl.exp(x - tl.max(x, axis=0))
    value = exp / tl.sum(exp, axis=0)
    tl.store(Y + row * N + col, value, col < N)

def run(x, op):
    if x.dtype != torch.float32 or not x.is_contiguous() or x.ndim != 2:
        raise ValueError('Supported contract: contiguous 2D FP32')
    y = torch.empty_like(x)
    if x.numel() == 0:
        return y
    if op == 'softmax':
        row_softmax[(x.shape[0],)](x, y, x.shape[1], triton.next_power_of_2(x.shape[1]), num_warps=SOFTMAX_WARPS)
    elif op in ('relu', 'gelu'):
        pointwise[(triton.cdiv(x.numel(), BLOCK),)](x, y, x.numel(), 0 if op == 'relu' else 1, BLOCK, num_warps=4)
    else:
        raise ValueError('Unknown operator')
    return y
