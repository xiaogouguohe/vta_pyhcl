# VTA pyhcl implementation of shell/VCR.scala
# Author: SunnyChen
# Date:   2020-05-25

from pyhcl import*
import sys 
sys.path.append("..") 
from shell.parameters import *
from interface_axi.axi import *
from util.generic_parameterized_bundle import *
from util.ext_funcs import *

class VCRBase(Bundle):
    def __int__(self):
        super().__int__()

class VCRMaster(Bundle):
    def __init__(self): #p ShellParams or ShellKey
        super().__init__()
        p = ShellKey()
        vp = p.vcrParams
        mp = p.memParams
        #self.launch = Output(Bool)
        #self.finish = Input(Bool)
        #self.ecnt = Vec(vp.nECnt, Flip(Valid(U.w(vp.regBits))))
        #self.ecnt = Flip(Valid(U.w(vp.regBits)))
        #self.vals = Output(Vec(vp.nVals, U.w(vp.regBits)))
        #self.ptrs = Output(Vec(vp.nPtrs, U.w(mp.addrBits)))
        #self.ucnt = Vec(vp.nUCnt, Flip(Valid(U.w(vp.regBits))))
        #self.ucnt = Flip(Valid(U.w(vp.regBits)))
        dic = self._kv
        dic["launch"] = Bool
        dic["finish"] = Bool.flip()
        dic["ecnt"] = Flip(Valid(U.w(vp.regBits)))
        #dic["ecnt"] = Vec(vp.nECnt, Flip(Valid(U.w(vp.regBits))))
        dic["vals"] = Vec(vp.nVals, U.w(vp.regBits))
        dic["ptrs"] = Vec(vp.nPtrs, U.w(mp.addrBits))
        dic["ucnt"] = Flip(Valid(U.w(vp.regBits)))

class VCRClient(Bundle):
    def __init__(self): #p ShellParams or ShellKey
        super().__init__()
        p = ShellKey()
        vp = p.vcrParams
        mp = p.memParams
        # self.launch = Input(Bool)
        # self.finish = Output(Bool)
        # #self.ecnt = Vec(vp.nECnt, Valid(U.w(vp.regBits)))
        # self.ecnt = Valid(U.w(vp.regBits))
        # self.vals = Input(Vec(vp.nVals, U.w(vp.regBits)))
        # self.ptrs = Input(Vec(vp.nPtrs, U.w(mp.addrBits)))
        # #self.ucnt = Vec(vp.nUCnt, Valid(U.w(vp.regBits)))
        # self.ucnt = Valid(U.w(vp.regBits))
        dic = self._kv
        dic["launch"] = Input(Bool)
        dic["finish"] = Output(Bool)
        # dic["ecnt"] = Vec(vp.nECnt, Valid(U.w(vp.regBits)))
        dic["ecnt"] = Valid(U.w(vp.regBits))
        dic["vals"] = Input(Vec(vp.nVals, U.w(vp.regBits)))
        dic["ptrs"] = Input(Vec(vp.nPtrs, U.w(mp.addrBits)))
        # dic["ucnt"] = Vec(vp.nUCnt, Valid(U.w(vp.regBits)))
        dic["ucnt"] = Valid(U.w(vp.regBits))

class VCR(Module):

    io = IO(
        host=Output(AXILiteClient()),
        vcr=Output(VCRMaster())
        #host = AXILiteClient(),
        #vcr = VCRMaster()
    )


    p = ShellKey()

    vp = p.vcrParams
    mp = p.memParams
    hp = p.hostParams

    # Write control (AW, W, B)
    waddr = RegInit(U.w(hp.addrBits)(0xffff))  # init with invalid address
    wdata = io.host.w.bits.data
    sWriteAddress, sWriteData, sWriteResponse = [U(i) for i in range(3)]
    wstate = RegInit(sWriteAddress)

    # read control (AR, R)
    sReadAddress, sReadData = [U(i) for i in range(2)]
    rstate = RegInit(sReadAddress)
    rdata = RegInit(U.w(vp.regBits)(0))

    # egisters
    nPtrs = 0
    if mp.addrBits == 32:
        nPtrs = vp.nPtrs
    else:
        nPtrs = 2 * vp.nPtrs
    nTotal = vp.nCtrl + vp.nECnt + vp.nVals + nPtrs + vp.nUCnt  # 1 + 1 + 1 + 6 + 1

    # reg = Seq.fill(nTotal)(RegInit(U.w(vp.regBits)(0)))s
    tmp = U(1)
    # print(type(tmp))
    reg = [RegInit(U.w(32)(0)) for i in range(nTotal)]  # should be RegInit(U.w(vp.regBits)(0))
    # val addr = Seq.tabulate(nTotal)(_ * 4)
    addr = [4 * i for i in range(nTotal)]
    # reg_map = zip(addr, reg) #map { case (a, r) => a.U -> r }
    eo = vp.nCtrl
    vo = eo + vp.nECnt
    po = vo + vp.nVals
    uo = po + nPtrs

    with when(wstate == sWriteAddress):
        with when(io.host.aw.valid):  # valid是Output(Bool)类型，应该怎么判断？
            wstate <<= sWriteData  # fetch.py用的是<<= ， =报错 ？
    with elsewhen(wstate == sWriteData):
        with when(io.host.w.valid):
            wstate <<= sWriteResponse
    with elsewhen(wstate == sWriteResponse):
        with when(io.host.b.ready):
            wstate <<= sWriteAddress



    # when(io.host.aw.fire()) { waddr := io.host.aw.bits.addr } #怎么写
    #with when(io.host.aw.valid):
    #    waddr <<= io.host.aw.bits.addr



    io.host.aw.ready <<= (wstate == sWriteAddress)
    io.host.w.ready <<= (wstate == sWriteData)
    io.host.b.valid <<= (wstate == sWriteResponse)
    io.host.b.bits.resp <<= U(0)

    with when(rstate == sReadAddress):
        with when(io.host.ar.valid):
            rstate <<= sReadData
    with when(rstate == sReadData):
        with when(io.host.r.ready):
            rstate <<= sReadAddress

    io.host.ar.ready <<= (rstate == sReadAddress)
    io.host.r.valid <<= (rstate == sReadData)
    io.host.r.bits.data <<= rdata
    io.host.r.bits.resp <<= U(0)

    with when(io.vcr.finish):
        reg[0] <<= U(1)  # U("b_10")
    with elsewhen(io.host.w.valid & U(addr[0]) == waddr):  # w.fire()
        reg[0] <<= wdata

    for i in range(vp.nECnt):
        #print("in func vcr, io.vcr.ecnt[i]:", io.vcr.ecnt[i])
        #print("in func vcr, type of io.vcr.ecnt[i]", type(io.vcr.ecnt[i]))
        #with when(io.vcr.ecnt[i].valid):
        with when(io.vcr.ecnt.valid):
            reg[eo + i] <<= io.vcr.ecnt.bits
        with elsewhen(io.host.w.valid & U(addr[eo + i]) == waddr):  # w.fire()
            reg[eo + i] <<= wdata

    for i in range(vp.nVals + nPtrs):
        with when(io.host.w.valid & U(addr[vo + i]) == waddr):  # w.fire()
            reg[vo + i] <<= wdata

    # with when(io.host_ar.valid):
    #    rdata <<= MuxLookup(io.host_ar_bits_addr, U(0), reg_map)

    io.vcr.launch <<= reg[0][0]

    for i in range(vp.nVals):
        io.vcr.vals[i] <<= reg[vo + i]

    if mp.addrBits == 32:
        for i in range(nPtrs):
            io.vcr.ptrs[i] <<= reg[po + i]
    else:
        for i in range(nPtrs / 2):
            # io_vcr.ptrs[i] <<= Cat(reg[po + 2 * i + 1], reg[po + 2 * i])
            pass

    with when(io.vcr.ucnt.valid):
        reg[uo] <<= io.vcr.ucnt.bits
    with elsewhen(io.host.w.valid & U(addr[uo]) == waddr):
        reg[uo] <<= wdata



if __name__ == "__main__":
    vcrMaster = VCRMaster()
    dic = vcrMaster._kv
    for key in dic:
        print(key, dic[key], type(dic[key]))

    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(VCR()), "VCR.fir"))
    #vcrMaster = VCRMaster()
    #vcrClient = VCRClient()
    #vcr = VCR()