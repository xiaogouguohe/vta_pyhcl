# VTA pyhcl implementation of core/Fetch.scala
# Author: SunnyChen
# Date:   2020-05-25


from pyhcl import *
from vta.core.isa import *
from vta.shell.parameters import *
from vta.shell.vme import VMReadMaster
from vta.util.ext_funcs import *


def fetch(debug: bool = False):
    p = ShellKey()
    vp = p.vcrParams
    mp = p.memParams

    # inst Bundle
    inst = IO()

    class Inst(BaseType):
        def __init__(self):
            self.ld = U.w(INST_BITS)
            self.co = U.w(INST_BITS)
            self.st = U.w(INST_BITS)

    decoupled(inst, Inst())

    # Fetch module
    class Fetch(Module):
        # Construct IO
        # Based IO
        io = IO(
            launch=Input(Bool),
            ins_baddr=Input(U.w(mp.addrBits)),
            ins_count=Input(U.w(vp.regBits)),
        )
        VMReadMaster_io = VMReadMaster()
        cat_io(io, VMReadMaster_io, 'vme_rd')
        cat_io(io, inst, 'inst')

        io.vme_rd_cmd_bits_addr <<= U(1)

    return Fetch()


if __name__ == '__main__':
    Emitter.dump(Emitter.emit(fetch()), "fetch.fir")
