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
from pyhcl import *
from vta.core.decode import LoadDecode
from vta.core.isa import *
from vta.core.semaphore import semaphore
from vta.core.tensorutil import TensorClient
from vta.shell.parameters import *
from vta.util.ext_funcs import *
from vta.shell.vme import *
from vta.util.selfqueue import queue


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
        

    return Load()


if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(load()), "Load.fir"))
