# VTA pyhcl implementation of core/Decode.scala
# Author: SunnyChen
# Date:   2020-05-26
from pyhcl import *
from vta.core.isa import *
from vta.util.ext_funcs import BaseType

"""
    MemDecode
    
    Decode memory instructions with a Bundle. This is similar to an union,
    therefore order matters when declaring fields. These are the instructions
    decoded with this bundle:
       - LUOP
       - LWGT
       - LINP
       - LACC
       - SOUT
"""


class MemDecode(BaseType):
    def __init__(self):
        self.xpad_1 = U.w(M_PAD_BITS)
        self.xpad_0 = U.w(M_PAD_BITS)
        self.ypad_1 = U.w(M_PAD_BITS)
        self.ypad_0 = U.w(M_PAD_BITS)
        self.xstride = U.w(M_STRIDE_BITS)
        self.xsize = U.w(M_SIZE_BITS)
        self.ysize = U.w(M_SIZE_BITS)
        self.empty_0 = U.w(7)
        self.dram_offset = U.w(M_DRAM_OFFSET_BITS)
        self.sram_offset = U.w(M_SRAM_OFFSET_BITS)
        self.id = U.w(M_ID_BITS)
        self.push_next = Bool
        self.push_prev = Bool
        self.pop_next = Bool
        self.pop_prev = Bool
        self.op = U.w(OP_BITS)


class MemDecode_Div:
    def __init__(self, inst):
        self.xpad_1 = inst[hxpad_1[1]:hxpad_0[0]]
        self.xpad_0 = inst[hxpad_0[1]:hxpad_0[0]]
        self.ypad_1 = inst[hypad_1[1]:hypad_1[0]]
        self.ypad_0 = inst[hypad_0[1]:hypad_0[0]]
        self.xstride = inst[hxstride[1]:hxstride[0]]
        self.xsize = inst[hxsize[1]:hxsize[0]]
        self.ysize = inst[hysize[1]:hysize[0]]
        self.empty_0 = inst[hempty_0[1]:hempty_0[0]]
        self.dram_offset = inst[hdram_offset[1]:hdram_offset[0]]
        self.sram_offset = inst[hsram_offset[1]:hsram_offset[0]]
        self.id = inst[hid[1]:hid[0]]
        self.push_next = inst[hpush_next[1]]
        self.push_prev = inst[hpush_prev[1]]
        self.pop_next = inst[hpop_next[1]]
        self.pop_prev = inst[hpop_prev[1]]
        self.op = inst[hop[1]:hop[0]]


"""
    FetchDecode
    Partial decoding for dispatching instructions to Load, Compute, and Store.
"""


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


"""
    LoadDecode
    
    Decode dependencies, type and sync for Load module
"""


class LoadDecode(Module):
    io = IO(
        inst=Input(U.w(INST_BITS)),
        push_next=Output(Bool),
        pop_next=Output(Bool),
        isInput=Output(Bool),
        isWeight=Output(Bool),
        isSync=Output(Bool)
    )
    io.push_next <<= io.inst[hpush_next[1]:hpush_next[0]]
    io.pop_next <<= io.inst[hpop_next[1]:hpop_next[0]]
    io.isInput <<= (io.inst == LINP) & (io.inst[hxsize[1]:hxsize[0]] != U(0))
    io.isWeight <<= (io.inst == LWGT) & (io.inst[hxsize[1]:hxsize[0]] != U(0))
    io.isSync <<= ((io.inst == LINP) | (io.inst == LWGT)) & (io.inst[hxsize[1]:hxsize[0]] == U(0))


