from pyhcl import *
import sys
sys.path.append("..")

from interface_axi.axi import *
from shell import *
from dpi.VTA_host_dpi import *
from dpi.VTA_mem_dpi import *
from dpi.VTA_sim_dpi import *
from util.ext_funcs import *
from pyhcl import ir

class VTAHost(Module):
    io = IO(
        axi = Output(XilinxAXILiteClient()),
    )
    host_dpi = VTAHostDPI()
    host_axi = vtaHostDpiToAXI()

    ir.utils.auto_connect2(host_axi.io.dpi, host_dpi.io.dpi)
    ir.utils.auto_connect2(io.axi, host_axi.io.axi)
    #ost_axi.io.dpi <> host_dpi.io.dpi
    #io.axi <> host_axi.io.axi


class VTAMem(Module):
    io = IO(
        axi=Output(AXIClient()),
    )
    mem_dpi = VTAMemDPI()
    mem_axi = vtaMemDPIToAXI()

    #mem_dpi.io.reset := reset
    #mem_dpi.io.clock := clock
    ir.utils.auto_connect2(mem_dpi.io.dpi, mem_axi.io.dpi)
    ir.utils.auto_connect2(mem_axi.io.axi, io.axi)

# class VTASim(Module):
#     sim_wait = IO(
#       Output(Bool)
#     )
#     sim = VTASimDPI()
#   #sim.io.reset := reset
#   #sim.io.clock := clock
#   #sim_wait <<= sim.io.dpi_wait
#
# class SimShell(Module):
#     # mem = IO(new AXIClient(p(ShellKey).memParams))
#     # host = IO(new AXILiteMaster(p(ShellKey).hostParams))
#     # sim_clock = IO(Input(Clock()))
#     # sim_wait = IO(Output(Bool()))
#     mod_sim = VTASim()
#     mod_host = VTAHost()
#     mod_mem = VTAMem()
#     #mem <> mod_mem.io.axi
#     #host <> mod_host.io.axi
#     ##mod_sim.reset := reset
#     #mod_sim.clock := sim_clock
#     #sim_wait := mod_sim.sim_wait

if __name__ == '__main__':
    #Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VTAHost()), "VTAHost.fir"))
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VTAMem()), "VTAMem.fir"))
    #Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VTASim()), "VTASim.fir"))
