from pyhcl import *

import sys
sys.path.append("..")
from interface_axi.axi import *
from shell.parameters import *


class VTAHostDPIParams:
    dpiAddrBits = 8
    dpiDataBits = 32


class Req(Bundle):
    def __init__(self):
        super().__init__()
        p = VTAHostDPIParams()
        dic = self._kv
        dic["valid"] = Bool
        dic["opcode"] = Bool
        dic["addr"] = U.w(p.dpiAddrBits)
        dic["value"] = U.w(p.dpiDataBits)
        dic["deq"] = Bool.flip()


class VTAHostDPIMaster(Bundle):  # with VTAHostDPIParams
    def __init__(self):
        super().__init__()
        dic = self._kv
        dic["req"] = Req()
        dic["resp"] = Flip(Valid(U.w(32))) #VTAHostDPIParams().dpiDataBits
        #dic["tmp"] = U.w(1)


class VTAHostDPIClient(Bundle):  # with VTAHostDPIParams
    def __init__(self):
        super().__init__()
        dic = self._kv
        dic["req"] = Flip(Req())
        dic["resp"] = Valid(U.w(32)) #VTAHostDPIParams().dpiDataBits
        #dic["tmp"] = U.w(1).flip()



class VTAHostDPI(BlackBox):  # extends BlackBox with HasBlackBoxResource {
    io = IO(
        # clock=Input(Clock),
        # reset=Input(Bool),
        dpi=Output(VTAHostDPIMaster()),
    )
    # setResource("/verilog/VTAHostDPI.v")

def vtaHostDpiToAXI(debug=False):

    class VTAHostDPIToAXI(Module):
        io = IO(
            dpi=Output(VTAHostDPIClient()),
            axi = Output(AXILiteMaster()),
        )

        addr = RegInit(U(0))
        # val addr = RegInit(0.U.asTypeOf(chiselTypeOf(io.dpi.req.addr)))
        data = RegInit(U(0))
        # val data = RegInit(0.U.asTypeOf(chiselTypeOf(io.dpi.req.value)))
        sIdle, sReadAddress, sReadData, sWriteAddress, sWriteData, sWriteResponse = [U(i) for i in range(6)]
        state = RegInit(sIdle)

        with when(state == sIdle):
            with when(io.dpi.req.valid):
                with when(io.dpi.req.opcode):
                    state <<= sWriteAddress
                with otherwise():
                    state <<= sReadAddress
        with when(state == sReadAddress):
            with when(io.axi.ar.ready):
                state <<= sReadData
        with when(state == sReadData):
            with when(io.axi.r.valid):
                state <<= sIdle
        with when(state == sWriteAddress):
            with when(io.axi.aw.ready):
                state <<= sWriteData
        with when(state == sWriteData):
            with when(io.axi.w.ready):
                state <<= sWriteResponse
        with when(state == sWriteResponse):
            with when(io.axi.b.valid):
                state <<= sIdle


        #with when(state == sIdle and io.dpi.req.valid):
        #    addr <<= io.dpi.req.addr
        #    data <<= io.dpi.req.value

        io.axi.aw.valid <<= (state == sWriteAddress)
        io.axi.aw.bits.addr <<= addr
        io.axi.w.valid <<= (state == sWriteData)
        io.axi.w.bits.data <<= data
        io.axi.w.bits.strb <<= U(0)  # should be "h_f"
        io.axi.b.ready <<= (state == sWriteResponse)

        io.axi.ar.valid <<= (state == sReadAddress)
        io.axi.ar.bits.addr <<= addr
        io.axi.r.ready <<= (state == sReadData)

        io.dpi.req.deq <<= ((state == sReadAddress & io.axi.ar.ready) | (state == sWriteAddress & io.axi.aw.ready))
        io.dpi.resp.valid <<= io.axi.r.valid
        io.dpi.resp.bits <<= io.axi.r.bits.data

        ''' if self.debug {
            with when(state == sWriteAddress and io.axi.aw.ready):
                #printf("[VTAHostDPIToAXI] [AW] addr:%x\n", addr)
            with when(state == sReadAddress and io.axi.ar.ready):
                #printf("[VTAHostDPIToAXI] [AR] addr:%x\n", addr)
            with when(io.axi.r.fire()):
                #printf("[VTAHostDPIToAXI] [R] value:%x\n", io.axi.r.bits.data)
            with when(io.axi.w.fire()) 
                #printf("[VTAHostDPIToAXI] [W] value:%x\n", io.axi.w.bits.data) '''
    return VTAHostDPIToAXI()

# class VTAHostDPIParams:
#     dpiAddrBits = 8
#     dpiDataBits = 32
#
# class Req(Bundle_Helper):
#     def __init__(self):
#         p = VTAHostDPIParams()
#         self.valid = Output(Bool)
#         self.opcode = Output(Bool)
#         self.addr = Output(U.w(p.dpiAddrBits))
#         self.value = Output(U.w(p.dpiDataBits))
#         self.deq = Input(Bool)
#
# class VTAHostDPIMaster(Bundle_Helper):# with VTAHostDPIParams
#     def __init__(self):
#
#         self.req = Req()
#         self.resp = flipped(valid(U.w(VTAHostDPIParams().dpiDataBits)))
#
# class VTAHostDPIClient(Bundle_Helper):# with VTAHostDPIParams
#     def __init__(self):
#
#         self.req = Req()
#         self.resp = valid(U.w(VTAHostDPIParams().dpiDataBits))
#
# class VTAHostDPI_IO(Bundle_Helper):
#     def __init__(self):
#         self.clock = Input(Clock)
#         self.reset = Input(Bool)
#         self.dpi = VTAHostDPIMaster()
#
# class VTAHostDPI(Module):# extends BlackBox with HasBlackBoxResource {
#     io = mapper(VTAHostDPI_IO())
#     #setResource("/verilog/VTAHostDPI.v")
#
# class VTAHostDPIToAXI_IO(Bundle_Helper):
#     def __init__(self):
#         self.dpi = VTAHostDPIClient()
#         self.axi = AXILiteMaster()
#
# class VTAHostDPIToAXI(Module):
#     def __init__(self, debug = False):
#         self.debug = debug
#
#     io = mapper(VTAHostDPIToAXI_IO())
#     addr = RegInit(U(0))
#     #val addr = RegInit(0.U.asTypeOf(chiselTypeOf(io.dpi.req.addr)))
#     data = RegInit(U(0))
#     #val data = RegInit(0.U.asTypeOf(chiselTypeOf(io.dpi.req.value)))
#     sIdle, sReadAddress, sReadData, sWriteAddress, sWriteData, sWriteResponse = [U(i) for i in range(6)]
#     state = RegInit(sIdle)
#
#     with when(state == sIdle):
#         with when (io.dpi_req_valid):
#             with when (io.dpi_req_opcode):
#                 state <<= sWriteAddress
#             with otherwise():
#                 state <<= sReadAddress
#     with when(state == sReadAddress):
#         with when(io.axi_ar_ready):
#             state <<= sReadData
#     with when(state == sReadData):
#         with when(io.axi_r_valid):
#             state <<= sIdle
#     with when(state == sWriteAddress):
#         with when(io.axi_aw_ready):
#             state <<= sWriteData
#     with when(state == sWriteData):
#         with when(io.axi_w_ready):
#             state <<= sWriteResponse
#     with when(state == sWriteResponse):
#         with when(io.axi_b_valid):
#             state <<= sIdle
#
#     with when (state == sIdle and io.dpi_req_valid):
#         addr <<= io.dpi_req_addr
#         data <<= io.dpi_req_value
#
#     io.axi_aw_valid <<= (state == sWriteAddress)
#     io.axi_aw_bits_addr <<= addr
#     io.axi_w_valid <<= (state == sWriteData)
#     io.axi_w_bits_data <<= data
#     io.axi_w_bits_strb <<= U(0) #should be "h_f"
#     io.axi_b_ready <<= (state == sWriteResponse)
#
#     io.axi_ar_valid <<= (state == sReadAddress)
#     io.axi_ar_bits_addr <<= addr
#     io.axi_r_ready <<= (state == sReadData)
#
#     io.dpi_req_deq <<= ((state == sReadAddress & io.axi_ar_ready) | (state == sWriteAddress & io.axi_aw_ready))
#     io.dpi_resp_valid <<= io.axi_r_valid
#     io.dpi_resp_bits <<= io.axi_r_bits_data
#
#     ''' if self.debug {
#         with when(state == sWriteAddress and io.axi.aw.ready):
#             #printf("[VTAHostDPIToAXI] [AW] addr:%x\n", addr)
#         with when(state == sReadAddress and io.axi.ar.ready):
#             #printf("[VTAHostDPIToAXI] [AR] addr:%x\n", addr)
#         with when(io.axi.r.fire()):
#             #printf("[VTAHostDPIToAXI] [R] value:%x\n", io.axi.r.bits.data)
#         with when(io.axi.w.fire())
#             #printf("[VTAHostDPIToAXI] [W] value:%x\n", io.axi.w.bits.data) '''

if __name__ == '__main__':
    #Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VTAHostDPI()), "VTAHostDPI.fir"))
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(vtaHostDpiToAXI()), "VTAHostDPIToAXI.fir"))
