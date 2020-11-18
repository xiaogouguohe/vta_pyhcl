# VTA pyhcl implementation of core/Decode.scala
# Author: SunnyChen
# Date:   2020-05-26
from pyhcl import *
import sys 
sys.path.append("..") 

from core.isa import *
from util.ext_funcs import Bundle_Helper

class MemDecode(Bundle_Helper):
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
        self.xpad_1 = inst[hxpad_1[1]:hxpad_1[0]]
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

class GemmDecode(Bundle_Helper):
    def __init__(self):
        self.wgt_1 = U.w(C_WIDX_BITS)
        self.wgt_0 = U.w(C_WIDX_BITS)
        self.inp_1 = U.w(C_IIDX_BITS)
        self.inp_0 = U.w(C_IIDX_BITS)
        self.acc_1 = U.w(C_AIDX_BITS)
        self.acc_0 = U.w(C_AIDX_BITS)
        self.empty_0 = Bool
        self.lp_1 = U.w(C_ITER_BITS)
        self.lp_0 = U.w(C_ITER_BITS)
        self.uop_end = U.w(C_UOP_END_BITS)
        self.uop_begin = U.w(C_UOP_BGN_BITS)
        self.reset = Bool
        self.push_next = Bool
        self.push_prev = Bool
        self.pop_next = Bool
        self.pop_prev = Bool
        self.op = U.w(OP_BITS)

class AluDecode(Bundle_Helper):
    def __init__(self):
        self.empty_1 = Bool
        self.alu_imm = U.w(C_ALU_IMM_BITS)
        self.alu_use_imm = Bool
        self.alu_op = U.w(C_ALU_DEC_BITS)
        self.src_1 = U.w(C_IIDX_BITS)
        self.src_0 = U.w(C_IIDX_BITS)
        self.dst_1 = U.w(C_AIDX_BITS)
        self.dst_0 = U.w(C_AIDX_BITS)
        self.empty_0 = Bool
        self.lp_1 = U.w(C_ITER_BITS)
        self.lp_0 = U.w(C_ITER_BITS)
        self.uop_end = U.w(C_UOP_END_BITS)
        self.uop_begin = U.w(C_UOP_BGN_BITS)
        self.reset = Bool
        self.push_next = Bool
        self.push_prev = Bool
        self.pop_next = Bool
        self.pop_prev = Bool
        self.op = U.w(OP_BITS)

class UopDecode(Bundle_Helper):
    def __init__(self):
        self.u2 = U.w(10)
        self.u1 = U.w(11)
        self.u0 = U.w(11)

class FetchDecode(Module):
    io = IO(
        inst = Input(U.w(INST_BITS)),
        isLoad = Output(Bool),
        isCompute = Output(Bool),
        isStore = Output(Bool)
    )

    if io.inst == LUOP:
        csignals = [Y, OP_G]
    elif io.host == LWGT:
        csignals = [Y, OP_L]
    elif io.host == LINP:
        csignals = [Y, OP_L]
    elif io.host == LACC:
        csignals = [Y, OP_G]
    elif io.host == SOUT:
        csignals = [Y, OP_S]
    elif io.host == GEMM:
        csignals = [Y, OP_G]
    elif io.host == FNSH:
        csignals = [Y, OP_G]
    elif io.host == VMIN:
        csignals = [Y, OP_G]
    elif io.host == VMAX:
        csignals = [Y, OP_G]
    elif io.host == VADD:
        csignals = [Y, OP_G]
    elif io.host == VSHX:
        csignals = [Y, OP_G]
    
    cs_val_inst, cs_op_type = csignals

    ''' cs_op_type = LookUpTable(io.inst, {
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
    }) '''

    io.isLoad <<= (cs_val_inst & cs_op_type == OP_L)
    io.isCompute <<= (cs_val_inst & cs_op_type == OP_G)
    io.isStore <<= (cs_val_inst & cs_op_type == OP_S)

class LoadDecode(Module):
    io = IO(
        inst = Input(U.w(INST_BITS)),
        push_next = Output(Bool),
        pop_next = Output(Bool),
        isInput = Output(Bool),
        isWeight = Output(Bool),
        isSync = Output(Bool),
    )
    ''' dec = io.inst.asTypeOf(MemDecode())
    io.push_next <<= dec.push_next
    io.pop_next <<= dec.pop_next
    io.isInput <<= (io.inst == LINP & dec.xsize != U(0))
    io.isWeight <<= (io.inst == LWGT & dec.xsize != U(0))
    io.isSync <<= (io.inst == LINP | io.inst == LWGT) & dec.xsize == U(0) '''

    io.push_next <<= io.inst[hpush_next[1]:hpush_next[0]]
    io.pop_next <<= io.inst[hpop_next[1]:hpop_next[0]]
    io.isInput <<= (io.inst == LINP) & (io.inst[hxsize[1]:hxsize[0]] != U(0))
    io.isWeight <<= (io.inst == LWGT) & (io.inst[hxsize[1]:hxsize[0]] != U(0))
    io.isSync <<= ((io.inst == LINP) | (io.inst == LWGT)) & (io.inst[hxsize[1]:hxsize[0]] == U(0))

class ComputeDecode(Module):
    io = IO(
        inst = Input(U.w(INST_BITS)),
        push_next = Output(Bool),
        push_prev = Output(Bool),
        pop_next = Output(Bool),
        pop_prev = Output(Bool),
        isLoadAcc = Output(Bool),
        isLoadUop = Output(Bool),
        isSync = Output(Bool),
        isAlu = Output(Bool),
        isGemm = Output(Bool),
        isFinish = Output(Bool)
    )
    ''' dec = io.inst.asTypeOf(new MemDecode)
    io.push_next <<= dec.push_next
    io.push_prev <<= dec.push_prev
    io.pop_next <<= dec.pop_next
    io.pop_prev <<= dec.pop_prev
    io.isLoadAcc <<= io.inst == LACC & dec.xsize != U(0)
    io.isLoadUop <<= io.inst == LUOP & dec.xsize != U(0)
    io.isSync <<= (io.inst == LACC | io.inst == LUOP) & dec.xsize == U(0)
    io.isAlu <<= io.inst == VMIN | io.inst == VMAX | io.inst == VADD | io.inst == VSHX
    io.isGemm <<= io.inst == GEMM
    io.isFinish <<= io.inst == FNSH '''

class StoreDecode(Module):
    io = IO(
        inst = Input(U.w(INST_BITS)),
        push_prev = Output(Bool),
        pop_prev = Output(Bool),
        isStore = Output(Bool),
        isSync = Output(Bool)
    )
    ''' dec = io.inst.asTypeOf(new MemDecode)
    io.push_prev <<= dec.push_prev
    io.pop_prev <<= dec.pop_prev
    io.isStore <<= io.inst == SOUT & dec.xsize != U(0)
    io.isSync <<= io.inst == SOUT & dec.xsize == U(0)'''

if __name__ == '__main__':
    """ memDecode = MemDecode()
    gemmDecode =GemmDecode()
    aluDecode = AluDecode()
    uopDecode = UopDecode()
    fetchDecode = FetchDecode()
    loadDecode = LoadDecode()
    storeDecode = StoreDecode() """
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(FetchDecode()), "FetchDecode.fir"))
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(LoadDecode()), "LoadDecode.fir"))
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(ComputeDecode()), "ComputeDecode.fir"))
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(StoreDecode()), "StoreDecode.fir"))




