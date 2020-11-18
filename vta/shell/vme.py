# VTA pyhcl implementation of shell/VME.scala, VTA Memory Engine(VME)
# Author: SunnyChen
# Date:   2020-05-25

import sys 
sys.path.append("..") 

from pyhcl import *
from shell.parameters import *
from util.ext_funcs import *
from interface_axi.axi import *


# VMECmd
# This interface is used for creating write and read requests to memory.
class VMECmd(Bundle_Helper):
    def __init__(self):
        addrBits = ShellKey().memParams.addrBits
        lenBits = ShellKey().memParams.lenBits
        self.addr = U.w(addrBits)
        self.len = U.w(lenBits)

class VMEReadMaster(Bundle_Helper):
    def __init__(self):
        super().__init__()
        dataBits = ShellKey().memParams.dataBits
        self.cmd = decoupled(VMECmd())
        self.data = flipped(decoupled(U.w(dataBits)))

class VMEReadClient(Bundle_Helper):
    def __init__(self):
        dataBits = ShellKey().memParams.dataBits
        self.cmd = flipped(decoupled(VMECmd()))
        self.data = decoupled(U.w(dataBits))

class VMEWriteMaster(Bundle_Helper):
    def __init__(self):
        dataBits = ShellKey().memParams.dataBits
        self.cmd = decoupled(VMECmd())
        self.data = decoupled(U.w(dataBits))
        self.ack = Input(Bool)

class VMEWriteClient(Bundle_Helper):
    def __init__(self):
        dataBits = ShellKey().memParams.dataBits
        self.cmd = flipped(decoupled(VMECmd()))
        self.data = flipped(decoupled(U.w(dataBits)))
        self.ack = Output(Bool)

class VMEMaster(Bundle_Helper):
    def __init__(self):
        nRd = ShellKey().vmeParams.nReadClients
        nWr = ShellKey.vmeParams.nWriteClients
        self.rd = Vec(nRd, VMEReadMaster())
        self.wr = Vec(nWr, VMEWriteMaster())

class VMEClient(Bundle_Helper):
    def __init__(self):
        nRd = ShellKey().vmeParams.nReadClients
        nWr = ShellKey().vmeParams.nWriteClients
        self.rd = Vec(nRd, VMEReadClient())
        self.wr = Vec(nWr, VMEWriteClient())

class VME_IO(Bundle_Helper):
    def __init__(self):
        self.mem = AXIMaster()
        self.vme = VMEReadClient()

class VME(Module):
    io = mapper(VME_IO())

    nReadClients = ShellKey().vmeParams.nReadClients
    #rd_arb = Module(Arbiter(VMECmd(), nReadClients))
    #rd_arb_chosen = RegEnable(rd_arb.io.chosen, rd_arb.io.out.fire())

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VME()), "VME.fir"))
