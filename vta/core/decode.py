# VTA pyhcl implementation of core/Decode.scala
# Author: SunnyChen
# Date:   2020-05-26
from pyhcl import *
from vta.core.isa import *


# FetchDecode
# Partial decoding for dispatching instructions to Load, Compute, and Store.


class FetchDecode(Module):
    io = IO(
        inst=Input(U.w(INST_BITS)),
        isLoad=Output(Bool),
        isCompute=Output(Bool),
        isStore=Output(Bool)
    )

    cs_op_type = LookUpTable(io.inst, {
        LUOP: OP_G,
        LWGT: OP_L,
        LINP: OP_L,
        LACC: OP_G,
        SOUT: OP_S,
        GEMM: OP_G,
        FNSH: OP_G,
        VMIN: OP_G,
        VMAX: OP_G,
        VADD: OP_G,
        VSHX: OP_G,
        ...: OP_X
    })

    cs_val_inst = LookUpTable(io.inst, {
        LUOP: Y,
        LWGT: Y,
        LINP: Y,
        LACC: Y,
        SOUT: Y,
        GEMM: Y,
        FNSH: Y,
        VMIN: Y,
        VMAX: Y,
        VADD: Y,
        VSHX: Y,
        ...: N
    })

    io.isLoad <<= cs_val_inst & (cs_op_type == OP_L)
    io.isCompute <<= cs_val_inst & (cs_op_type == OP_G)
    io.isStore <<= cs_val_inst & (cs_op_type == OP_S)
