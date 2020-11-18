# VTA pyhcl implementation of interface.axi/AXI.scala
# Author: xiaogouguohe
# Date:   2020-10-17
from pyhcl import *
from math import *
import sys 
sys.path.append("..") 
from util.generic_parameterized_bundle import *
from util.ext_funcs import *

class AXIParams:
    def __init__(self,
        coherent: bool = False,
        idBits: int = 1,
        addrBits: int = 32,
        dataBits: int = 64,
        lenBits: int = 8,
        userBits: int = 1
    ):
        assert addrBits > 0
        assert dataBits >= 8 and dataBits % 2 == 0

        self.coherent = coherent
        self.idBits = idBits
        self.addrBits = addrBits
        self.dataBits = dataBits
        self.lenBits = lenBits          # Max burst length = 256, lenBits = 8
        self.userBits = userBits

        self.strbBits: int = int(dataBits / 8)
        self.sizeBits: int = 3
        self.burstBits: int = 2
        self.lockBits: int = 2
        self.cacheBits: int = 4
        self.protBits: int = 3
        self.qosBits: int = 4
        self.regionBits: int = 4
        self.respBits: int = 2
        self.sizeConst: int = int(ceil(log(int(dataBits / 8), 2)))
        self.idConst: int = 0
        self.userConst: int = 1 if coherent else 0
        self.burstConst: int = 1
        self.lockConst: int = 0
        self.cacheConst: int = 15 if coherent else 3
        self.protConst: int = 4 if coherent else 0
        self.qosConst: int = 0
        self.regionConst: int = 0

#class AXIBase(Bundle_Helper):
class AXIBase(Bundle):
    def __int__(self):
        super().__init__()
        pass

class AXILiteAddress(AXIBase):
    def __init__(self):
        super().__init__()
        params = AXIParams()
        self.addr = U.w(params.addrBits)

class AXILiteWriteData(AXIBase):
    def __init__(self):
        super().__init__()
        params = AXIParams()
        self.data = U.w(params.dataBits)
        self.strb = U.w(params.strbBits)

class AXILiteWriteResponse(AXIBase):
    def __init__(self):
        super().__init__()
        params = AXIParams()
        self.resp = U.w(params.respBits)

class AXILiteReadData(AXIBase):
    def __init__(self):
        super().__init__()
        params = AXIParams()
        self.data = U.w(params.dataBits)
        self.resp = U.w(params.respBits)

class AXILiteMaster(AXIBase):
    def __init__(self):
        super.__init__()
        params = AXIParams()
        #self.aw = Decoupled(AXILiteAddress())
        #self.w = Decoupled(AXILiteWriteData())
        self.b = Flip(Decoupled(AXILiteWriteResponse()))
        #self.ar = Decoupled(AXILiteAddress())
        #self.r = Flip(Decoupled(AXILiteReadData()))

    def tieoff(self):
        self.aw.valid = Bool(False)
        self.aw.bits.addr = U(0)
        self.w.valid = Bool(False)
        self.w.bits.data = U(0)
        self.w.bits.strb = U(0)
        self.b.ready = Bool(False)
        self.ar.valid = Bool(False)
        self.ar.bits.addr = U(0)
        self.r.ready = Bool(False)

class AXILiteClient(AXIBase):
    def __init__(self):
        super().__init__()
        self.aw = Flip(Decoupled(AXILiteAddress()))
        self.w = Flip(Decoupled(AXILiteWriteData()))
        self.b = Decoupled(AXILiteWriteResponse())
        self.ar = Flip(Decoupled(AXILiteAddress()))
        self.r = Decoupled(AXILiteReadData())

    def tieoff(self):
        self.aw.ready = Bool(False)
        self.w.ready = Bool(False)
        self.b.valid = Bool(False)
        self.b.bits.resp = U(0)
        self.ar.ready = Bool(False)
        self.r.valid = Bool(False)
        self.r.bits.resp = U(0)
        self.r.bits.data = U(0)

class AXIAddress(AXILiteAddress):
    def __init__(self):
        super().__init__()
        params = AXIParams()
        self.params = params
        self.id = U.w(params.idBits)
        self.user = U.w(params.userBits)
        self.len = U.w(params.lenBits)
        self.size = U.w(params.sizeBits)
        self.burst = U.w(params.burstBits)
        self.lock = U.w(params.lockBits)
        self.cache = U.w(params.cacheBits)
        self.prot = U.w(params.protBits)
        self.qos = U.w(params.qosBits)
        self.region = U.w(params.regionBits)

class AXIWriteData(AXILiteWriteData):
    def __init__(self):
        super().__init__()
        params = AXIParams()
        self.last = Bool
        self.id = U.w(params.idBits)
        self.user = U.w(params.userBits)

class AXIWriteResponse(AXILiteWriteResponse):
    def __init__(self):
        super().__init__()
        params = AXIParams()
        self.id = U.w(params.idBits)
        self.user = U.w(params.userBits)

class AXIReadData(AXILiteReadData):
    def __init__(self):
        super().__init__()
        params = AXIParams()
        self.last = Bool
        self.id = U.w(params.idBits)
        self.user = U.w(params.userBits)

class AXIMaster(AXIBase):
    def __init__(self):
        super.__init__()
        params = AXIParams()
        self.aw = Decoupled(AXIAddress())
        self.w = Decoupled(AXIWriteData())
        self.b = Flip(Decoupled(AXIWriteResponse()))
        self.ar = Decoupled(AXIAddress())
        self.r = Flip(Decoupled(AXIReadData()))

    def tieoff(self):
        self.aw.valid = Bool(False)
        self.aw.bits.addr = U(0)
        self.aw.bits.id = U(0)
        self.aw.bits.user = U(0)
        self.aw.bits.len = U(0)
        self.aw.bits.size = U(0)
        self.aw.bits.burst = U(0)
        self.aw.bits.lock = U(0)
        self.aw.bits.cache = U(0)
        self.aw.bits.prot = U(0)
        self.aw.bits.qos = U(0)
        self.aw.bits.region = U(0)
        self.w.valid = Bool(False)
        self.w.bits.data = U(0)
        self.w.bits.strb = U(0)
        self.w.bits.last = Bool(False)
        self.w.bits.id = U(0)
        self.w.bits.user = U(0)
        self.b.ready = Bool(False)
        self.ar.valid = Bool(False)
        self.ar.bits.addr = U(0)
        self.ar.bits.id = U(0)
        self.ar.bits.user = U(0)
        self.ar.bits.len = U(0)
        self.ar.bits.size = U(0)
        self.ar.bits.burst = U(0)
        self.ar.bits.lock = U(0)
        self.ar.bits.cache = U(0)
        self.ar.bits.prot = U(0)
        self.ar.bits.qos = U(0)
        self.ar.bits.region = U(0)
        self.r.ready = Bool(False)

    def setConst(self):
        self.aw.bits.user = U(params.userConst)
        self.aw.bits.burst = U(params.burstConst)
        self.aw.bits.lock = U(params.lockConst)
        self.aw.bits.cache = U(params.cacheConst)
        self.aw.bits.prot = U(params.protConst)
        self.aw.bits.qos = U(params.qosConst)
        self.aw.bits.region = U(params.regionConst)
        self.aw.bits.size = U(params.sizeConst)
        self.aw.bits.id = U(params.idConst)
        self.w.bits.id = U(params.idConst)
        self.w.bits.user = U(params.userConst)
        self.w.bits.strb = Fill(params.strbBits, Bool(True)) #?
        self.ar.bits.user = U(params.userConst)
        self.ar.bits.burst = U(params.burstConst)
        self.ar.bits.lock = U(params.lockConst)
        self.ar.bits.cache = U(params.cacheCons)
        self.ar.bits.prot = U(params.protConst)
        self.ar.bits.qos = U(params.qosConst)
        self.ar.bits.region = U(params.regionConst)
        self.ar.bits.size = U(params.sizeConst)
        self.ar.bits.id = U(params.idConst)

class AXIClient(AXIBase):
    def __init__(self):
        super.__init__()
        params = AXIParams()
        self.aw = Flip(Decoupled(AXIAddress()))
        self.w = Flip(Decoupled(AXIWriteData()))
        self.b = Decoupled(AXIWriteResponse())
        self.ar = Flip(Decoupled(AXIAddress()))
        self.r = Decoupled(AXIReadData())
        #self.tieoff()

    def tieoff(self):
        self.aw.ready = Bool(False)
        self.w.ready = Bool(False)
        self.b.valid = Bool(False)
        self.b.bits.resp = U(0)
        self.b.bits.user = U(0)
        self.b.bits.id = U(0)
        self.ar.ready = Bool(False)
        self.r.valid = Bool(False)
        self.r.bits.resp = U(0)
        self.r.bits.data = U(0)
        self.r.bits.user = U(0)
        self.r.bits.last = Bool(False)
        self.r.bits.id = U(0)

class XilinxAXILiteClient(AXIBase):
    def __init__(self):
        super.__init__()
        params = AXIParams()
        self.AWVALID = Input(Bool)
        self.AWREADY = Output(Bool)
        self.AWADDR = Input(U.w(params.addrBits))
        self.WVALID = Input(Bool)
        self.WREADY = Output(Bool)
        self.WDATA = Input(U.w(params.dataBits))
        self.WSTRB = Input(U.w(params.strbBits))
        self.BVALID = Output(Bool)
        self.BREADY = Input(Bool)
        self.BRESP = Output(U.w(params.respBits))
        self.ARVALID = Input(Bool)
        self.ARREADY = Output(Bool)
        self.ARADDR = Input(U.w(params.addrBits))
        self.RVALID = Output(Bool)
        self.RREADY = Input(Bool)
        self.RDATA = Output(U.w(params.dataBits))
        self.RRESP = Output(U.w(params.respBits))

class XilinxAXIMaster(AXIBase):
    def __init__(self):
        super.__init__()
        params = AXIParams()
        self.AWVALID = Output(Bool)
        self.AWREADY = Input(Bool)
        self.AWADDR = Output(U.w(params.addrBits))
        self.AWID = Output(U.w(params.idBits))
        self.AWUSER = Output(U.w(params.userBits))
        self.AWLEN = Output(U.w(params.lenBits))
        self.AWSIZE = Output(U.w(params.sizeBits))
        self.AWBURST = Output(U.w(params.burstBits))
        self.AWLOCK = Output(U.w(params.lockBits))
        self.AWCACHE = Output(U.w(params.cacheBits))
        self.AWPROT = Output(U.w(params.protBits))
        self.AWQOS = Output(U.w(params.qosBits))
        self.AWREGION = Output(U.w(params.regionBits))
        self.WVALID = Output(Bool)
        self.WREADY = Input(Bool)
        self.WDATA = Output(U.w(params.dataBits))
        self.WSTRB = Output(U.w(params.strbBits))
        self.WLAST = Output(Bool)
        self.WID = Output(U.w(params.idBits))
        self.WUSER = Output(U.w(params.userBits))
        self.BVALID = Input(Bool)
        self.BREADY = Output(Bool)
        self.BRESP = Input(U.w(params.respBits))
        self.BID = Input(U.w(params.idBits))
        self.BUSER = Input(U.w(params.userBits))
        self.ARVALID = Output(Bool)
        self.ARREADY = Input(Bool)
        self.ARADDR = Output(U.w(params.addrBits))
        self.ARID = Output(U.w(params.idBits))
        self.ARUSER = Output(U.w(params.userBits))
        self.ARLEN = Output(U.w(params.lenBits))
        self.ARSIZE = Output(U.w(params.sizeBits))
        self.ARBURST = Output(U.w(params.burstBits))
        self.ARLOCK = Output(U.w(params.lockBits))
        self.ARCACHE = Output(U.w(params.cacheBits))
        self.ARPROT = Output(U.w(params.protBits))
        self.ARQOS = Output(U.w(params.qosBits))
        self.ARREGION = Output(U.w(params.regionBits))
        self.RVALID = Input(Bool)
        self.RREADY = Output(Bool)
        self.RDATA = Input(U.w(params.dataBits))
        self.RRESP = Input(U.w(params.respBits))
        self.RLAST = Input(Bool)
        self.RID = Input(U.w(params.idBits))
        self.RUSER = Input(U.w(params.userBits))

if __name__ == '__main__':
    #axiBase = AXIBase()
    #axiBase._kv
    #axiLiteAddress = AXILiteAddress()
    #axiLiteAddress._kv
    #axiParams = AXIParams()
    #axiLiteAddress = AXILiteAddress()
    #axiLiteWriteResponse = AXILiteWriteResponse()
    #print(type(axiLiteWriteResponse))
    #print(isinstance(axiLiteWriteResponse, Bundle))
    #axiLiteWriteResponse._kv
    #Flip(axiLiteWriteResponse)
    #axiLiteMaster = AXILiteMaster()
    pass
