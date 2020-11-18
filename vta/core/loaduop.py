import sys
sys.path.append("..")

from pyhcl import *
from shell.parameters import *
from util.ext_funcs import *
from decode import *
from shell.vme import *
from shell.vcr import *
from interface_axi.axi import *

class UopMaster(Bundle_Helper):
    def __init__(self):
        p = CoreKey()
        self.addrBits = log2ceil(p.uopMemDepth)
        self.idx = valid(U.w(self.addrBits))
        self.data = flipped(valid(UopDecode()))

class UopClient(Bundle_Helper):
    def __init__(self):
        p = CoreKey()
        self.addrBits = log2ceil(p.uopMemDepth)
        self.idx = flipped(valid(U.w(self.addrBits)))
        self.data = valid(UopDecode())

def loadUop(debug: Bool = False):

    class LoadUop_IO(Bundle_Helper):
        def __init__(self):
            super().__init__()
            p = ShellKey()
            mp = p.memParams
            self.start = Input(Bool)
            self.done = Output(Bool)
            self.inst = Input(U.w(INST_BITS))
            self.baddr = Input(U.w(mp.addrBits))
            self.vme_rd = VMEReadMaster()
            self.uop = UopClient()
            print("type of vme_rd:", type(self.vme_rd))
    
    class LoadUop(Module):
        io = mapper(LoadUop_IO())
        numUop = 2
        uopBits = CoreKey().uopBits
        uopBytes = uopBits / 8
        uopDepth = CoreKey().uopMemDepth / numUop

        #dec = io.inst.asTypeOf(new MemDecode)
        dec = MemDecode()
        raddr = Reg(io.vme_rd_cmd_bits_addr)
        xcnt = Reg(io.vme_rd_cmd_bits_len)
        xlen = Reg(io.vme_rd_cmd_bits_len)
        xrem = Reg(dec.xsize)

        ''' xsize = (dec.xsize >> log2ceil(numUop)) + dec.xsize(0) + (dec.sram_offset % U(2)) - U(1)
        xmax = (1 << mp.lenBits).U
        xmax_bytes = ((1 << mp.lenBits) * mp.dataBits / 8).U

        dram_even = (dec.dram_offset % 2.U) == 0.U
        sram_even = (dec.sram_offset % 2.U) == 0.U
        sizeIsEven = (dec.xsize % 2.U) == 0.U '''
        xsize = U(0)
        xmax = U(0)
        xmax_bytes = U(0)
        dram_even = U(0)
        sram_even = U(0)
        sizeIsEven = U(0)

        sIdle, sReadCmd, sReadData = [U(i) for i in range(3)]
        state = RegInit(sIdle)

        with when(state == sIdle):
            with when(io.start):
                state <<= sReadCmd
                with when(xsize < xmax):
                    xlen <<= xsize
                    xrem <<= U(0)
                with elsewhen(1):
                    xlen <<= xmax - U(1)
                    xrem <<= xsize - xmax
        with when(state == sReadCmd):
            with when(io.vme_rd_cmd_ready):
                state <<= sReadData
        with when(state == sReadData):
            with when(io.vme_rd_data_valid):
                with when(xcnt == xlen):
                    with when(xrem == U(0)):
                        state <<= sIdle
                with elsewhen(1):
                    raddr <<= raddr + xmax_bytes
                    with when(xrem < xmax):
                        state <<= sReadCmd
                        xlen <<= xrem
                        xrem <<= U(0)       
                    with elsewhen(1):
                        state <<= sReadCmd
                        xlen <<= xmax - U(1)
                        xrem <<= xrem - xmax

        #val maskOffset = VecInit(Seq.fill(M_DRAM_OFFSET_BITS)(true.B)).asUInt
        maskOffset = [Bool(True) for _ in range(M_DRAM_OFFSET_BITS)] # asUint
        with when(state == sIdle):
            with when(dram_even):
                #raddr <<= io.baddr | (maskOffset & (dec.dram_offset << log2ceil(uopBytes)))
                raddr <<= U(0)
            with elsewhen(1):
                raddr <<= U(0)
                #raddr <<= (io.baddr | (maskOffset & (dec.dram_offset << log2ceil(uopBytes)))) - U(uopBytes)

        io.vme_rd_cmd_valid <<= state == sReadCmd
        io.vme_rd_cmd_bits_addr <<= raddr
        io.vme_rd_cmd_bits_len <<= xlen

        io.vme_rd_data_ready <<= state == sReadData

        with when(state != sReadData):
            xcnt <<= U(0)
        with elsewhen(io.vme_rd_data_valid): #should be fire()
            xcnt <<= xcnt + U(1)

        waddr = Reg(U.w(log2ceil(uopDepth)))
        with when(state == sIdle):
            waddr <<= U(0)
            # waddr <<= dec.sram_offset >> log2ceil(numUop)
        with elsewhen(io.vme_rd_data_valid): # should be fire()
            waddr <<= waddr + U(1)

        wdata = Wire(Vec(numUop, U.w(uopBits)))
        tmp = waddr.v
        print(type(waddr))
        print(tmp)
        ''' mem = SyncReadMem(uopDepth, chiselTypeOf(wdata))
        wmask = Reg(Vec(numUop, Bool()))

        when(sram_even) {
            when(sizeIsEven) {
            wmask <<= "b_11".U.asTypeOf(wmask)
            }.elsewhen(io.vme_rd.cmd.fire()) {
            when(dec.xsize == 1.U) {
                wmask <<= "b_01".U.asTypeOf(wmask)
            }.otherwise {
                wmask <<= "b_11".U.asTypeOf(wmask)
            }
            }.elsewhen(io.vme_rd.data.fire()) {
            when((xcnt == xlen - 1.U) && (xrem == 0.U)) {
                wmask <<= "b_01".U.asTypeOf(wmask)
            }.otherwise {
                wmask <<= "b_11".U.asTypeOf(wmask)
            }
            }
        }.otherwise {
            when(io.vme_rd.cmd.fire()) {
            wmask <<= "b_10".U.asTypeOf(wmask)
            }.elsewhen(io.vme_rd.data.fire()) {
            when(sizeIsEven && (xcnt == xlen - 1.U) && (xrem == 0.U)) {
                wmask <<= "b_01".U.asTypeOf(wmask)
            }.otherwise {
                wmask <<= "b_11".U.asTypeOf(wmask)
            }
            }
        }

        wdata <<= io.vme_rd.data.bits.asTypeOf(wdata)
        when(dram_even == false.B && sram_even) {
            wdata(0) <<= io.vme_rd.data.bits.asTypeOf(wdata)(1)
        }.elsewhen(sram_even == false.B && dram_even) {
            wdata(1) <<= io.vme_rd.data.bits.asTypeOf(wdata)(0)
        }

        when(io.vme_rd.data.fire()) {
            mem.write(waddr, wdata, wmask)
        }

        // read-from-sram
        io.uop.data.valid <<= RegNext(io.uop.idx.valid)

        sIdx = io.uop.idx.bits % numUop.U
        rIdx = io.uop.idx.bits >> log2Ceil(numUop)
        memRead = mem.read(rIdx, io.uop.idx.valid)
        sWord = memRead.asUInt.asTypeOf(wdata)
        sUop = sWord(sIdx).asTypeOf(io.uop.data.bits)

        io.uop.data.bits <> sUop

        // done
        io.done <<= state == sReadData & io.vme_rd.data.valid & xcnt == xlen & xrem == 0.U

        // debug
        if (debug) {
            when(io.vme_rd.cmd.fire()) {
            printf("[LoadUop] cmd addr:%x len:%x rem:%x\n", raddr, xlen, xrem)
            }
        }
        } '''

    #return LoadUop()

if __name__ == '__main__':
    print("type of VMEReadMaster", type(VMEReadMaster()))
    print("type of UopClient", type(UopClient()))
    uopMaster = UopMaster()
    uopClient = UopClient()
    loadUop = loadUop()