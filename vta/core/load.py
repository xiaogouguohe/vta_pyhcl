# VTA pyhcl implementation of core/Load.scala
# Author: SunnyChen
# Date:   2020-05-28

"""
    Load.

    Load inputs and weights from memory (DRAM) into scratchpads (SRAMs).
    This module instantiate the TensorLoad unit which is in charge of
    loading 1D and 2D tensors to scratchpads, so it can be used by
    other modules such as Compute.
"""

import sys
sys.path.append("..")

from core.decode import LoadDecode
from core.isa import *
from core.semaphore import semaphore
from core.tensorutil import TensorClient
from shell.vme import *
from util.selfqueue import queue
from core.tensorload import tensorload


def load(debug: bool = False):
    p = ShellKey()
    mp = p.memParams
    cp = CoreKey()

    class Load_IO(Bundle_Helper):
        def __init__(self):
            self.i_post = Input(Bool)
            self.o_post = Output(Bool)
            self.inst = flipped(decoupled(U.w(INST_BITS)))
            self.inp_baddr = Input(U.w(mp.addrBits))
            self.wgt_baddr = Input(U.w(mp.addrBits))
            self.vme_rd_0 = VMEReadMaster()
            self.vme_rd_1 = VMEReadMaster()
            self.inp = TensorClient(tensorType="inp")
            self.wgt = TensorClient(tensorType="wgt")

    class Load(Module):
        # Base IO
        io = mapper(Load_IO())

        sIdle, sSync, sExe = [U(i) for i in range(3)]
        state = RegInit(sIdle)

        s = semaphore(counterBits=8, counterInitValue=0)
        inst_q = queue(gentype=U.w(INST_BITS), entries=cp.instQueueEntries)

        dec = LoadDecode()
        dec.io.inst <<= inst_q.io.deq_bits

        tensorType = ["inp", "wgt"]
        tensorDec = [dec.io.isInput, dec.io.isWeight]

        tensorLoad = [tensorload(tensorType[i]) for i in range(2)]

        start = inst_q.io.deq_valid & Mux(dec.io.pop_next, s.io.sready, Bool(True))
        done = Mux(dec.io.isInput, tensorLoad[0].io.done, tensorLoad[1].io.done)

        # control
        with when(state == sIdle):
            with when(start):
                with when(dec.io.isSync):
                    state <<= sSync
                with elsewhen(dec.io.isInput | dec.io.isWeight):
                    state <<= sExe
        with elsewhen(state == sSync):
            state <<= sIdle
        with elsewhen(state == sExe):
            with when(done):
                state <<= sIdle

        # instructions
        # inst_q.io.enq <> io.inst
        io.inst_ready <<= inst_q.io.enq_ready
        inst_q.io.enq_valid <<= io.inst_valid
        inst_q.io.enq_bits <<= io.inst_bits
        inst_q.io.deq_ready <<= ((state == sExe) & done) | (state == sSync)

        # load tensor
        # [0] input (inp)
        # [1] weight (wgt)
        ptr = [io.inp_baddr, io.wgt_baddr]
        # val tsor = Seq(io.inp, io.wgt)
        for i in range(2):
            tensorLoad[i].io.start <<= (state == sIdle) & start & tensorDec[i]
            tensorLoad[i].io.inst <<= inst_q.io.deq_bits
            tensorLoad[i].io.baddr <<= ptr[i]

            # tensorLoad(i).io.tensor <> tsor(i)


    return Load()


if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(load()), "Load.fir"))
