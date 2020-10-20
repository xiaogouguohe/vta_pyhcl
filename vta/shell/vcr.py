# VTA pyhcl implementation of shell/VCR.scala
# Author: SunnyChen
# Date:   2020-05-25

from pyhcl import* 
import sys 
sys.path.append("..") 
from parameters import *
from interface_axi.axi import *
from util.generic_parameterized_bundle import *
from util.ext_funcs import *

""" class VCRParams:
    def __init__(self):
        self.nCtrl = 1
        self.nECnt = 1
        self.nVals = 1
        self.nPtrs = 6
        self.nUCnt = 1
        self.regBits = 32 """

""" class VCRBase(GenericParameterizedBundle):
    def __init__(self, p):
        super().__init__(p) """
        
class VCRBase(GenericParameterizedBundle):
    def __init__(self, p):
        super().__init__(p) 
        

class VCRMaster(VCRBase):
    def __init__(self, p): #p ShellParams or ShellKey
        super().__init__(p)
        vp = p.vcrParams
        mp = p.memParams
        launch = Output(Bool)
        finish = Input(Bool)
        #ecnt = Vec(vp.nECnt, flipped(ValidIO(U.w(vp.regBits)))) 怎么改？
        ecnt = Vec(vp.nECnt, flipped(U.w(vp.regBits)))
        vals = Output(Vec(vp.nVals, U.w(vp.regBits)))
        ptrs = Output(Vec(vp.nPtrs, U.w(mp.addrBits)))
        #ucnt = Vec(vp.nUCnt, flipped(ValidIO(U.w(vp.regBits))))
        ucnt = Vec(vp.nUCnt, flipped(U.w(vp.regBits)))

class VCRClient(VCRBase):
    def __init__(self, p): #p ShellParams or ShellKey
        super().__init__(p)
        vp = p.vcrParams
        mp = p.memParams
        launch = Input(Bool)
        finish = Output(Bool)
        #ecnt = Vec(vp.nECnt, ValidIO(UInt(vp.regBits.W)))
        ecnt = Vec(vp.nECnt, U.w(vp.regBits))
        vals = Input(Vec(vp.nVals, U.w(vp.regBits)))
        ptrs = Input(Vec(vp.nPtrs, U.w(mp.addrBits)))
        #ucnt = Vec(vp.nUCnt, ValidIO(UInt(vp.regBits.W)))
        ucnt = Vec(vp.nUCnt, U.w(vp.regBits))

class VCR_IO(Bundle_Helper):
    def __init__(self):
        self.host = AXILiteClient(p.hostParams),
        self.vcr = VCRMaster(p)

class VCR(Module):
    ''' val io = IO(new Bundle {
        val host = new AXILiteClient(p(ShellKey).hostParams)
        val vcr = new VCRMaster
    }) '''

    p = ShellKey()
    io = IO(
        #tmp = decoupled(AXILiteAddress(p.hostParams)),
        host = AXILiteClient(p.hostParams),
        vcr = VCRMaster(p)
    ) 

    #tmp2 = io.tmp
    #wdata = io.host

    vp = p.vcrParams
    mp = p.memParams
    hp = p.hostParams

    # Write control (AW, W, B)
    #waddr = RegInit(U.w(hp.addrBits)(0xffff)) # init with invalid address
    #a = host3
    #wdata = io.host.w.bits.data
    #sWriteAddress :: sWriteData :: sWriteResponse :: Nil = Enum(3)
    #wstate = RegInit(sWriteAddress)

    # read control (AR, R)
    #val sReadAddress :: sReadData :: Nil = Enum(2)
    #state = RegInit(sReadAddress)
    #val rdata = RegInit(0.U(vp.regBits.W))

    '''// registers
    val nPtrs = if (mp.addrBits == 32) vp.nPtrs else 2 * vp.nPtrs
    val nTotal = vp.nCtrl + vp.nECnt + vp.nVals + nPtrs + vp.nUCnt

    val reg = Seq.fill(nTotal)(RegInit(0.U(vp.regBits.W)))
    val addr = Seq.tabulate(nTotal)(_ * 4)
    val reg_map = (addr zip reg) map { case (a, r) => a.U -> r }
    val eo = vp.nCtrl
    val vo = eo + vp.nECnt
    val po = vo + vp.nVals
    val uo = po + nPtrs

    switch(wstate) {
        is(sWriteAddress) {
        when(io.host.aw.valid) {
            wstate := sWriteData
        }
        }
        is(sWriteData) {
        when(io.host.w.valid) {
            wstate := sWriteResponse
        }
        }
        is(sWriteResponse) {
        when(io.host.b.ready) {
            wstate := sWriteAddress
        }
        }
    }

    when(io.host.aw.fire()) { waddr := io.host.aw.bits.addr }

    io.host.aw.ready := wstate === sWriteAddress
    io.host.w.ready := wstate === sWriteData
    io.host.b.valid := wstate === sWriteResponse
    io.host.b.bits.resp := 0.U

    switch(rstate) {
        is(sReadAddress) {
        when(io.host.ar.valid) {
            rstate := sReadData
        }
        }
        is(sReadData) {
        when(io.host.r.ready) {
            rstate := sReadAddress
        }
        }
    }

    io.host.ar.ready := rstate === sReadAddress
    io.host.r.valid := rstate === sReadData
    io.host.r.bits.data := rdata
    io.host.r.bits.resp := 0.U

    when(io.vcr.finish) {
        reg(0) := "b_10".U
    }.elsewhen(io.host.w.fire() && addr(0).U === waddr) {
        reg(0) := wdata
    }

    for (i <- 0 until vp.nECnt) {
        when(io.vcr.ecnt(i).valid) {
        reg(eo + i) := io.vcr.ecnt(i).bits
        }.elsewhen(io.host.w.fire() && addr(eo + i).U === waddr) {
        reg(eo + i) := wdata
        }
    }

    for (i <- 0 until (vp.nVals + nPtrs)) {
        when(io.host.w.fire() && addr(vo + i).U === waddr) {
        reg(vo + i) := wdata
        }
    }

    when(io.host.ar.fire()) {
        rdata := MuxLookup(io.host.ar.bits.addr, 0.U, reg_map)
    }

    io.vcr.launch := reg(0)(0)

    for (i <- 0 until vp.nVals) {
        io.vcr.vals(i) := reg(vo + i)
    }

    if (mp.addrBits == 32) { // 32-bit pointers
        for (i <- 0 until nPtrs) {
        io.vcr.ptrs(i) := reg(po + i)
        }
    } else { // 64-bits pointers
        for (i <- 0 until (nPtrs / 2)) {
        io.vcr.ptrs(i) := Cat(reg(po + 2 * i + 1), reg(po + 2 * i))
        }
    }

    for (i <- 0 until vp.nUCnt) {
        when(io.vcr.ucnt(i).valid) {
        reg(uo + i) := io.vcr.ucnt(i).bits
        }.elsewhen(io.host.w.fire() && addr(uo + i).U === waddr) {
        reg(uo + i) := wdata
        }
    }
    }
    '''

if __name__ == "__main__":
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VCR()), "VCR.fir"))