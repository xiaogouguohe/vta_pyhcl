from pyhcl import *

import sys
sys.path.append("..")
from interface_axi.axi import *
from shell.parameters import *

class VTASimDPI_IO(Bundle_Helper):
    def __init__(self):
        #self.clock = Input(Clock)
        #self.reset = Input(Bool)
        #self.dpi_wait = Output(Bool)
        pass

class VTASimDPI(Module): #BlackBox
    io = mapper(VTASimDPI_IO())
    #setsource
    #pass

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VTASimDPI()), "VTASimDPI.fir"))