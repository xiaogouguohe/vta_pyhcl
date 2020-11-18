# VTA pyhcl implementation of shell/VTAShell.scala
# Author: SunnyChen
# Date:   2020-05-25

import sys
sys.path.append("..") 

from interface_axi.axi import *
from shell.vcr import *
from shell.vme import *
#from core

class VTAShell_IO:
    def __init__(self):
        self.host = AXILiteClient()
        self.mem = AXIMaster()

class VTAShell(Module):
  io = mapper(VTAShell_IO)

  vcr = VCR()
  vme = VME()
  #core = Core()

  """core.io.vcr <> vcr.io.vcr
  vme.io.vme <> core.io.vme

  vcr.io.host <> io.host
  io.mem <> vme.io.mem """
    #core.io_vcr <<= vcr.io_vcr
    

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VTAShell()), "VTAShell.fir"))





if __name__ == '__main__':
    pass
