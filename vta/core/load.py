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
from vta.core.isa import *
from vta.shell.parameters import *
from vta.util.ext_funcs import *
from vta.shell.vme import *


def load(debug: bool = False):
    p = ShellKey()
    mp = p.memParams

    class Inst(BaseType):
        def __init__(self):
            self.inst = U.w(INST_BITS)


    class Load(Module):
        # Base IO
        io = IO(
            i_post=Input(Bool),
            o_post=Output(Bool),
            inp_baddr=Input(U.w(mp.addrBits)),
            wgt_baddr=Input(U.w(mp.addrBits))
        )
        decoupled(io, Inst(), is_fliped=True)

        # vme_rd = Vec(2, new VMEReadMaster)
        VMEReadMaster_io = VMEReadMaster()
        cat_io(io, VMEReadMaster_io, 'vme_rd_1')
        cat_io(io, VMEReadMaster_io, 'vme_rd_2')

