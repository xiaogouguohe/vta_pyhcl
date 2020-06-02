"""
VTA pyhcl implementation of core/TensorUtil.scala
Author: SunnyChen
Date:   2020-06-02
"""
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


if __name__ == '__main__':
    print(isinstance(TensorClient(tensorType="inp"), Bundle_Helper))
