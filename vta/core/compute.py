from pyhcl import *

import sys
sys.path.append("..")

from shell.parameters import *
from util.ext_funcs import *
from shell.vme import *
from tensorutil import *
from semaphore import *
from loaduop import *
from tensorload import *

class Compute_IO(Bundle_Helper):
    def __init__(self):
        super().__init__()
        p = ShellKey()
        mp = p.memParams
        self.i_post = [Input(Bool), Input(Bool)]
        self.o_post = [Output(Bool), Output(Bool)]
        self.inst = flipped(decoupled(U.w(128))) #INST_BITS = 128
        self.uop_baddr = Input(U.w(mp.addrBits))
        self.acc_baddr = Input(U.w(mp.addrBits))
        self.vme_rd = [VMEReadMaster(), VMEReadMaster()]
        self.inp = TensorMaster(tensorType = "inp")
        self.wgt = TensorMaster(tensorType = "wgt")
        self.out = TensorMaster(tensorType = "out")
        self.finish = Output(Bool)
        self.acc_wr_event = Output(Bool)

class Compute(Module):
    io = mapper(Compute_IO())

    sIdle, sSync, sExe = [U(i) for i in range(3)]
    state = RegInit(sIdle)

    #val s = Seq.tabulate(2)(_ =>
    #    Module(new Semaphore(counterBits = 8, counterInitValue = 0)))
    s = [semaphore(counterBits = 8, counterInitValue = 0), semaphore(counterBits = 8, counterInitValue = 0)]
    
    loadUop = loadUop()
    tensorAcc = tensorload(tensorType = "acc")
    """ val tensorGemm = Module(new TensorGemm)
    val tensorAlu = Module(new TensorAlu) """

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(Compute()), "Computer.fir"))
