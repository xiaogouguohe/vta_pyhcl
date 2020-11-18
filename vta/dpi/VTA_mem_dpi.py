from pyhcl import *

import sys
sys.path.append("..")
from interface_axi.axi import *
from shell.parameters import *

class VTAMemDPIParams:
    dpiLenBits = 8
    dpiAddrBits = 64
    dpiDataBits = 64

class Req(Bundle_Helper):
    def __init__(self):
        self.valid = Output(Bool)
        self.opcode = Output(Bool)
        self.len = Output(U.w(VTAMemDPIParams().dpiLenBits))
        self.addr = Output(U.w(VTAMemDPIParams().dpiAddrBits))

class VTAMemDPIMaster(Bundle_Helper):
    def __init__(self):
        self.req = Req()
        self.wr = valid(U.w(VTAMemDPIParams().dpiDataBits))
        self.rd = flipped(decoupled(U.w(VTAMemDPIParams().dpiDataBits)))

class VTAMemDPIClient(Bundle_Helper):
    def __init__(self):
        self.req = Req()
        self.wr = flipped(valid(U.w(VTAMemDPIParams().dpiDataBits)))
        self.rd = decoupled(U.w(VTAMemDPIParams().dpiDataBits))

class VTAMemDPI_IO(Bundle_Helper):
    def __init__(self):
        self.clock = Input(Clock)
        self.reset = Input(Bool)
        self.dpi = VTAMemDPIClient()

class VTAMemDPI(Module):
    io = mapper(VTAMemDPI_IO())

class VTAMemDPIToAXI_IO(Bundle_Helper):
    def __init__(self):
        self.dpi = VTAMemDPIMaster()
        self.axi = AXIClient()

class VTAMemDPIToAXI(Module):
    io = mapper(VTAMemDPIToAXI_IO())
    opcode = RegInit(Bool(False))
    len = RegInit(U(0))
    addr = RegInit(U(0))
    sIdle, sReadAddress, sReadData, sWriteAddress, sWriteData, sWriteResponse = [U(i) for i in range(6)]
    state = RegInit(sIdle)

    with when(state == sIdle):
        with when(io.axi_ar_valid):
            state <<= sReadAddress
        with elsewhen(io.axi_aw_valid):
            state <<= sWriteAddress
    with when(state == sReadAddress):
        with when(io.axi_ar_valid):
            state <<= sReadData
    with when(state == sReadData):
        with when(io.axi_r_ready & io.dpi_rd_valid & len == U(0)): #should be and
            state <<= sIdle
    with when(state == sWriteAddress):
        with when(io.axi_aw_valid):
            state <<= sWriteData
    with when(state == sWriteData):
        with when(io.axi_w_valid & io.axi_w_bits_last):  #should be and
            state <<= sWriteResponse
    with when(state == sWriteResponse):
        with when(io.axi_b_ready):
            state <<= sIdle

    with when(state == sIdle):
        with when(io.axi_ar_valid):
            opcode <<= Bool(False)
            len <<= io.axi_ar_bits_len
            addr <<= io.axi_ar_bits_addr 
        with elsewhen(io.axi_aw_valid):
            opcode <<= Bool(True)
            len <<= io.axi_aw_bits_len
            addr <<= io.axi_aw_bits_addr
    with elsewhen(state == sReadData):
        with when(io.axi_r_ready & io.dpi_rd_valid & len != U(0)): #should be and
            len <<= len - U(1)

    io.dpi_req_valid <<= (state == sReadAddress & io.axi_ar_valid) | (state == sWriteAddress & io.axi_aw_valid)
    io.dpi_req_opcode <<= opcode
    io.dpi_req_len <<= len
    io.dpi_req_addr <<= addr

    io.axi_ar_ready <<= (state == sReadAddress)
    io.axi_aw_ready <<= (state == sWriteAddress)

    io.axi_r_valid <<= (state == sReadData & io.dpi_rd_valid)
    io.axi_r_bits_data <<= io.dpi_rd_bits
    io.axi_r_bits_last <<= (len == U(0))
    io.axi_r_bits_resp <<= U(0)
    io.axi_r_bits_user <<= U(0)
    io.axi_r_bits_id <<= U(0)
    io.dpi_rd_ready <<= (state == sReadData & io.axi_r_ready)

    io.dpi_wr_valid <<= (state == sWriteData & io.axi_w_valid)
    io.dpi_wr_bits <<= io.axi_w_bits_data
    io.axi_w_ready <<= (state == sWriteData)

    io.axi_b_valid <<= (state == sWriteResponse)
    io.axi_b_bits_resp <<= U(0)
    io.axi_b_bits_user <<= U(0)
    io.axi_b_bits_id <<= U(0)

    """ if (debug) {
        when(state === sReadAddress && io.axi.ar.valid) {
        printf("[VTAMemDPIToAXI] [AR] addr:%x len:%x\n", addr, len)
        }
        when(state === sWriteAddress && io.axi.aw.valid) {
        printf("[VTAMemDPIToAXI] [AW] addr:%x len:%x\n", addr, len)
        }
        when(io.axi.r.fire()) {
        printf("[VTAMemDPIToAXI] [R] last:%x data:%x\n",
            io.axi.r.bits.last,
            io.axi.r.bits.data)
        }
        when(io.axi.w.fire()) {
        printf("[VTAMemDPIToAXI] [W] last:%x data:%x\n",
            io.axi.w.bits.last,
            io.axi.w.bits.data)
        }
    }
    } """

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VTAMemDPIToAXI()), "VTAMemDPIToAXI.fir"))