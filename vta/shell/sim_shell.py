from pyhcl import *
#import chisel3.experimental.MultiIOModule
import sys
sys.path.append("..")

from interface_axi.axi import *
from shell import *
from dpi import *
from util.ext_funcs import *

class VTAHost_IO(Bundle_Helper):
    def __init__(self):
        self.axi = XilinxAXILiteClient()

class VTAHost(Module):
    io = mapper(VTAHost_IO())

    #host_dpi = VTAHostDPI()
    #host_axi = VTAHostDPIToAXI()
    """ host_dpi.io.reset := reset
    host_dpi.io.clock := clock
    host_axi.io.dpi <> host_dpi.io.dpi
    io.axi <> host_axi.io.axi """

""" class VTAMem(implicit p: Parameters) extends Module {
  val io = IO(new Bundle {
    val axi = new AXIClient(p(ShellKey).memParams)
  })
  val mem_dpi = Module(new VTAMemDPI)
  val mem_axi = Module(new VTAMemDPIToAXI)
  mem_dpi.io.reset := reset
  mem_dpi.io.clock := clock
  mem_dpi.io.dpi <> mem_axi.io.dpi
  mem_axi.io.axi <> io.axi
}

class VTASim(implicit p: Parameters) extends MultiIOModule {
  val sim_wait = IO(Output(Bool()))
  val sim = Module(new VTASimDPI)
  sim.io.reset := reset
  sim.io.clock := clock
  sim_wait := sim.io.dpi_wait

class SimShell(implicit p: Parameters) extends MultiIOModule {
  val mem = IO(new AXIClient(p(ShellKey).memParams))
  val host = IO(new AXILiteMaster(p(ShellKey).hostParams))
  val sim_clock = IO(Input(Clock()))
  val sim_wait = IO(Output(Bool()))
  val mod_sim = Module(new VTASim)
  val mod_host = Module(new VTAHost)
  val mod_mem = Module(new VTAMem)
  mem <> mod_mem.io.axi
  host <> mod_host.io.axi
  mod_sim.reset := reset
  mod_sim.clock := sim_clock
  sim_wait := mod_sim.sim_wait """

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(SimShell()), "SimShell.fir"))