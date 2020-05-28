# VTA pyhcl implementation of shell/VME.scala, VTA Memory Engine(VME)
# Author: SunnyChen
# Date:   2020-05-25


from pyhcl import *
from vta.shell.parameters import *
from vta.util.ext_funcs import *


# VMECmd
# This interface is used for creating write and read requests to memory.
class VMECmd(BaseType):
    def __init__(self):
        addrBits = ShellKey().memParams.addrBits
        lenBits = ShellKey().memParams.lenBits
        self.addr = U.w(addrBits)
        self.len = U.w(lenBits)


# VMEReadMaster
# This interface is used by modules inside the core to generate read requests
# and receive responses from VME.
# def VMEReadMaster():
#     p = ShellKey()
#     dataBits = p.memParams.dataBits
#
#     class Cmd(BaseType):
#         def __init__(self):
#             self.cmd = VMECmd()
#
#     class Data(BaseType):
#         def __init__(self):
#             self.data = U.w(dataBits)
#
#     vmreadmaster = IO()
#     decoupled(vmreadmaster, Cmd())
#     decoupled(vmreadmaster, Data(), is_fliped=True)
#     return vmreadmaster
class VMEReadMaster(Bundle):
    def __init__(self):
        p = ShellKey()
        dataBits = p.memParams.dataBits
        self.cmd = decoupled(VMECmd())
        self.data = flipped(decoupled(U.w(dataBits)))


if __name__ == '__main__':
    pass
