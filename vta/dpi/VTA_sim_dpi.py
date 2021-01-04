from pyhcl import *

import sys
sys.path.append("..")
from interface_axi.axi import *
from shell.parameters import *

class VTASimDPI(Module): #BlackBox
    io = IO(
        clock = Input(Clock),
        reset = Input(Bool),
        dpi_wait = Output(Bool)
    )
    #setsource

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VTASimDPI()), "VTASimDPI.fir"))