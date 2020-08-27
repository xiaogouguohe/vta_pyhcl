"""
VTA pyhcl implementation of core/TensorUtil.scala
Author: SunnyChen
Date:   2020-06-02
"""
from vta.core.decode import MemDecode_Div
from vta.core.isa import *
from vta.shell.parameters import *
from vta.util.ext_funcs import *
from math import *
from pyhcl import *


"""
TensorParams.

This Bundle derives parameters for each tensorType, including inputs (inp),
weights (wgt), biases (acc), and outputs (out). This is used to avoid
doing the same boring calculations over and over again.
"""


class TensorParams(Bundle_Helper):
    def __init__(self, tensorType: str):
        super().__init__()
        assert tensorType == "inp" or tensorType == "wgt" or \
               tensorType == "acc" or tensorType == "out"
        self.p = CoreKey()
        self.sp = ShellKey()

        if tensorType == "inp":
            self.tensorLength, self.tensorWidth, self.tensorElemBits = self.p.batch, self.p.blockIn, self.p.inpBits
            self.memDepth = self.p.inpMemDepth
        elif tensorType == "wgt":
            self.tensorLength, self.tensorWidth, self.tensorElemBits = self.p.blockOut, self.p.blockIn, self.p.wgtBits
            self.memDepth = self.p.wgtMemDepth
        elif tensorType == "acc":
            self.tensorLength, self.tensorWidth, self.tensorElemBits = self.p.batch, self.p.blockOut, self.p.accBits
            self.memDepth = self.p.accMemDepth
        else:
            self.tensorLength, self.tensorWidth, self.tensorElemBits = self.p.batch, self.p.blockOut, self.p.outBits
            self.memDepth = self.p.outMemDepth

        self.memBlockBits = self.sp.memParams.dataBits
        self.numMemBlock = (self.tensorWidth * self.tensorElemBits) / self.memBlockBits

        self.memAddrBits = int(ceil(log(self.memDepth, 2)))

"""
TensorClient.

This interface receives read and write tensor-requests to scratchpads. For example,
The TensorLoad unit uses this interface for receiving read and write requests from
the TensorGemm unit.
"""


class TensorClient(TensorParams):
    def __init__(self, tensorType: str):
        super().__init__(tensorType)
        inner_memAddrBits = self.memAddrBits
        inner_tensorLength, inner_tensorWidth, inner_tensorElemBits = self.tensorLength, self.tensorWidth, self.tensorElemBits

        class RD(Bundle_Helper):
            def __init__(self):
                self.idx = flipped(valid(U.w(inner_memAddrBits)))
                self.data = valid(Vec(inner_tensorLength, Vec(inner_tensorWidth, U.w(inner_tensorElemBits))))

        class WR(Bundle_Helper):
            def __init__(self):
                self.idx = flipped(valid(U.w(inner_memAddrBits)))
                self.data = flipped(valid(Vec(inner_tensorLength, Vec(inner_tensorWidth, U.w(inner_tensorElemBits)))))

        self.rd = RD()
        self.wr = WR()


# TensorDataCtrl. Data controller for TensorLoad
def tensordatactrl(tensorType: str = "none", sizeFactor: int = 1, strideFactor: int = 1):
    mp = ShellKey().memParams
    p = CoreKey()

    class TensorDataCtrl(Module):
        io = IO(
            start=Input(Bool),
            done=Output(Bool),
            inst=Input(U.w(INST_BITS)),
            baddr=Input(U.w(mp.addrBits)),
            xinit=Input(Bool),
            xupdate=Input(Bool),
            yupdate=Input(Bool),
            stride=Output(Bool),
            split=Output(Bool),
            commit=Output(Bool),
            addr=Output(U.w(mp.addrBits)),
            len=Output(U.w(mp.lenBits))
        )

        dec = MemDecode_Div(io.inst)

        caddr = Reg(U.w(mp.addrBits))
        baddr = Reg(U.w(mp.addrBits))
        len = Reg(U.w(mp.lenBits))
        maskOffset = U.w(M_DRAM_OFFSET_BITS)(2 ** M_DRAM_OFFSET_BITS - 1)   # All 1
        if tensorType == "inp":
            elemBytes = p.batch * p.blockIn * p.inpBits / 8
        elif tensorType == "wgt":
            elemBytes = p.blockOut * p.blockIn * p.wgtBits / 8
        else:
            elemBytes = p.batch * p.blockOut * p.accBits / 8

        xmax_bytes = U((1 << mp.lenBits) * mp.dataBits / 8)
        xcnt = Reg(U.w(mp.lenBits))
        xrem = Reg(U.w(M_SIZE_BITS))
        xsize = (dec.xsize << U(log2ceil(sizeFactor)) - U(1))
        xmax = U(1 << mp.lenBits)
        ycnt = Reg(U.w(M_SIZE_BITS))

        xfer_bytes = Reg(U.w(mp.addrBits))
        pulse_bytes_bits = log2ceil(mp.dataBits >> 3)
        xstride_bytes = dec.xstride << log2ceil(elemBytes)

        xfer_init_addr = io.baddr | (maskOffset & (dec.dram_offset << log2ceil(elemBytes)))
        xfer_split_addr = caddr + xfer_bytes
        xfer_stride_addr = baddr + xstride_bytes

        xfer_init_bytes = xmax_bytes - xfer_init_addr % xmax_bytes
        xfer_init_pulses = xfer_init_bytes >> pulse_bytes_bits
        xfer_split_bytes = xmax_bytes - xfer_split_addr % xmax_bytes
        xfer_split_pulses = xfer_split_bytes >> pulse_bytes_bits
        xfer_stride_bytes = xmax_bytes - xfer_stride_addr % xmax_bytes
        xfer_stride_pulses = xfer_stride_bytes >> pulse_bytes_bits

        stride = (xcnt == len) & (xrem == U(0)) & (ycnt != (dec.ysize - U(1)))
        split = (xcnt == len) & (xrem != U(0))

        with when(io.start):
            xfer_bytes <<= xfer_init_bytes
            with when(xsize < xfer_init_pulses):
                len <<= xsize
                xrem <<= U(0)
            with otherwise():
                len <<= xfer_init_pulses - U(1)
                xrem <<= xsize - xfer_init_pulses
        with elsewhen(io.xupdate & stride):
            xfer_bytes <<= xfer_stride_bytes
            with when(xsize < xfer_stride_bytes):
                len <<= xsize
                xrem <<= U(0)
            with otherwise():
                len <<= xfer_stride_pulses - U(1)
                xrem <<= xsize - xfer_stride_pulses
        with elsewhen(io.xupdate & split):
            xfer_bytes <<= xfer_split_bytes
            with when(xrem < xfer_split_pulses):
                len <<= xrem
                xrem <<= U(0)
            with otherwise():
                len <<= xfer_split_pulses - U(1)
                xrem <<= xrem - xfer_split_pulses

        with when(io.xinit):
            xcnt <<= U(0)
        with elsewhen(io.xupdate):
            xcnt <<= xcnt + U(1)

        with when(io.start):
            ycnt <<= U(0)
        with elsewhen(io.yupdate & stride):
            ycnt <<= ycnt + U(1)

        with when(io.start):
            caddr <<= xfer_init_addr
            baddr <<= xfer_init_addr
        with elsewhen(io.yupdate):
            with when(split):
                caddr <<= xfer_split_addr
            with elsewhen(stride):
                caddr <<= xfer_stride_addr
                baddr <<= xfer_stride_addr

        io.stride <<= stride
        io.split <<= split
        io.commit <<= xcnt == len
        io.addr <<= caddr
        io.len <<= len
        io.done <<= (xcnt == len) & (xrem == U(0)) & (ycnt == dec.ysize - U(1))

    return TensorDataCtrl()


# TensorPadCtrl. Zero-padding controller for TensorLoad.
def tensorpadctrl(padType: str = "None", sizeFactor: int = 1):
    assert padType == "YPad0" or padType == "YPad1" or \
           padType == "XPad0" or padType == "XPad1"

    class TensorPadCtrl(Module):
        io = IO(
            start=Input(Bool),
            done=Output(Bool),
            inst=Input(U.w(INST_BITS))
        )

        dec = MemDecode_Div(io.inst)

        xmax = Reg(U.w(M_SIZE_BITS))
        ymax = Reg(U.w(M_PAD_BITS))
        xcnt = Reg(U.w(M_SIZE_BITS))
        ycnt = Reg(U.w(M_PAD_BITS))

        if padType == "YPad0" or padType == "YPad1":
            xval = ((dec.xpad_0 + dec.xsize + dec.xpad_1) << log2ceil(sizeFactor)) - U(1)
        elif padType == "XPad0":
            xval = (dec.xpad_0 << log2ceil(sizeFactor)) - U(1)
        else:
            xval = (dec.xpad_1 << log2ceil(sizeFactor)) - U(1)

        if padType == "YPad0":
            yval = Mux(dec.ypad_0 != U(0), dec.ypad_0 - U(1), U(0))
        elif padType == "YPad1":
            yval = Mux(dec.ypad_1 != U(0), dec.ypad_1 - U(1), U(0))
        else:
            yval = U(0)

        sIdle, sActive = [U(i) for i in range(2)]
        state = RegInit(U.w(1)(0))  # val state = RegInit(sIdle)

        with when(state == sIdle):
            with when(io.start):
                state <<= sActive
        with elsewhen(state == sActive):
            with when((ycnt == ymax) & (xcnt == xmax)):
                state <<= sIdle

        with when(state == sIdle):
            xmax <<= xval
            ymax <<= yval

        with when((state == sIdle) | (xcnt == xmax)):
            xcnt <<= U(0)
        with elsewhen(state == sActive):
            xcnt <<= xcnt + U(1)

        with when((state == sIdle) | (ymax == U(0))):
            ycnt <<= U(0)
        with elsewhen((state == sActive) & (xcnt == xmax)):
            ycnt <<= ycnt + U(1)

        io.done <<= (state == sActive) & (ycnt == ymax) & (xcnt == xmax)

    return TensorPadCtrl()


if __name__ == '__main__':
    print(isinstance(TensorClient(tensorType="inp"), Bundle_Helper))
