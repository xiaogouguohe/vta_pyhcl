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

        xmax_bytes = U((1 << mp.lenBits) * mp.dataBits / 8)
        xcnt = Reg(U.w(mp.lenBits))
        xrem = Reg(U.w(M_SIZE_BITS))
        xsize = (dec.xsize << U(int(ceil(log(sizeFactor, 2))))) - U(1)
        xmax = U(1 << mp.lenBits)
        ycnt = Reg(U.w(M_SIZE_BITS))

        stride = (xcnt == len) & (xrem == U(0)) & (ycnt != (dec.ysize - U(1)))
        split = (xcnt == len) & (xrem != U(0))

    return TensorDataCtrl()


if __name__ == '__main__':
    print(isinstance(TensorClient(tensorType="inp"), Bundle_Helper))
