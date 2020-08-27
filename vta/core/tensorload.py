# VTA pyhcl implementation of core/TensorLoad.scala
# Author: SunnyChen
# Date:   2020-06-08


from pyhcl import *
from vta.core.decode import MemDecode_Div
from vta.core.isa import *
from vta.core.tensorutil import *
from vta.shell.vme import VMEReadMaster

"""
    TensorLoad.
    
    Load 1D and 2D tensors from main memory (DRAM) to input/weight
    scratchpads (SRAM). Also, there is support for zero padding, while
    doing the load. Zero-padding works on the y and x axis, and it is
    managed by TensorPadCtrl. The TensorDataCtrl is in charge of
    handling the way tensors are stored on the scratchpads.
"""


def tensorload(tensorType: str = "none", debug: bool = False):
    tp = TensorParams(tensorType)
    mp = ShellKey().memParams

    class TensorLoad_IO(Bundle_Helper):
        def __init__(self):
            self.start = Input(Bool)
            self.done = Input(Bool)
            self.inst = Input(U.w(INST_BITS))
            self.baddr = Input(U.w(mp.addrBits))
            self.vme_rd = VMEReadMaster()
            self.tensor = TensorClient(tensorType)

    class TensorLoad(Module):
        io = mapper(TensorLoad_IO())

        sizeFactor = tp.tensorLength * tp.numMemBlock
        strideFactor = tp.tensorLength * tp.tensorWidth

        dec = MemDecode_Div(io.inst)
        dataCtrl = tensordatactrl(tensorType, sizeFactor, strideFactor)
        dataCtrlDone = RegInit(Bool(False))
        yPadCtrl0 = tensorpadctrl("YPad0", sizeFactor)
        yPadCtrl1 = tensorpadctrl("YPad1", sizeFactor)
        xPadCtrl0 = tensorpadctrl("XPad0", sizeFactor)
        xPadCtrl1 = tensorpadctrl("XPad1", sizeFactor)

        tag = Reg(U.w(log2ceil(tp.numMemBlock)))
        set = Reg(U.w(log2ceil(tp.tensorLength)))

        sIdle, sYPad0, sXPad0, sReadCmd, sReadData, sXPad1, sYPad1 = [U(i) for i in range(7)]
        state = RegInit(U.w(3)(0))      # val state = RegInit(sIdle)

        # control
        with when(state == sIdle):
            with when(io.start):
                with when(dec.ypad_0 != U(0)):
                    state <<= sYPad0
                with elsewhen(dec.xpad_0 != U(0)):
                    state <<= sXPad0
                with otherwise():
                    state <<= sReadCmd
        with elsewhen(state == sYPad0):
            with when(yPadCtrl0.io.done):
                with when(dec.xpad_0 != U(0)):
                    state <<= sXPad0
                with otherwise():
                    state <<= sReadCmd
        with elsewhen(state == sXPad0):
            with when(xPadCtrl0.io.done):
                state <<= sReadCmd
        with elsewhen(state == sReadCmd):
            with when(io.vme_rd_data_valid):
                with when(dataCtrl.io.done):
                    with when(dec.xpad_1 != U(0)):
                        state <<= sXPad1
                    with elsewhen(dec.ypad_1 != U(0)):
                        state <<= sYPad1
                    with otherwise():
                        state <<= sIdle
                with elsewhen(dataCtrl.io.stride):
                    with when(dec.xpad_1 != U(0)):
                        state <<= sXPad1
                    with elsewhen(dec.xpad_0 != U(0)):
                        state <<= sXPad0
                    with otherwise():
                        state <<= sReadCmd
                with elsewhen(dataCtrl.io.split):
                    state <<= sReadCmd
        with elsewhen(state == sXPad1):
            with when(xPadCtrl1.io.done):
                with when(dataCtrlDone):
                    with when(dec.ypad_1 != U(0)):
                        state <<= sYPad1
                    with otherwise():
                        state <<= sIdle
                with otherwise():
                    with when(dec.xpad_0 != U(0)):
                        state <<= sXPad0
                    with otherwise():
                        state <<= sReadCmd
        with elsewhen(state == sYPad1):
            with when(yPadCtrl1.io.done & dataCtrlDone):
                state <<= sIdle

        # Apply to data controller
        dataCtrl.io.start <<= (state == sIdle) & io.start
        dataCtrl.io.inst <<= io.inst
        dataCtrl.io.baddr <<= io.baddr

        vme_cmd_fire = io.vme_rd_cmd_ready & io.vme_rd_cmd_valid
        vme_data_fire = io.vme_rd_data_ready & io.vme_rd_data_valid

        dataCtrl.io.xinit <<= vme_cmd_fire
        dataCtrl.io.xupdate <<= vme_data_fire
        dataCtrl.io.yupdate <<= vme_data_fire

        with when(state == sIdle):
            dataCtrlDone <<= Bool(False)
        with elsewhen(vme_data_fire & dataCtrl.io.done):
            dataCtrlDone <<= Bool(True)

        # Pad
        yPadCtrl0.io.start <<= (dec.ypad_0 != U(0)) & (state == sIdle) & io.start

        yPadCtrl1.io.start <<= (dec.ypad_1 != U(0)) & \
                               (vme_data_fire & dataCtrl.io.done & (dec.xpad_1 == U(0)) |
                                ((state == sXPad1) & xPadCtrl1.io.done & dataCtrlDone))

    return TensorLoad()
