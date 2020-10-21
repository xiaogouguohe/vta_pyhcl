# VTA pyhcl implementation of core/Fetch.scala
# Author: SunnyChen
# Date:   2020-05-25

# * Fetch
# *
# * The fetch unit reads instructions (tasks) from memory (i.e. DRAM), using the
# * VTA Memory Engine (VME), and push them into an instruction queue called
# * inst_q. Once the instruction queue is full, instructions are dispatched to
# * the Load, Compute and Store module queues based on the instruction opcode.
# * After draining the queue, the fetch unit checks if there are more instructions
# * via the ins_count register which is written by the host.
# *
# * Additionally, instructions are read into two chunks (see sReadLSB and sReadMSB)
# * because we are using a DRAM payload of 8-bytes or half of a VTA instruction.
# * This should be configurable for larger payloads, i.e. 64-bytes, which can load
# * more than one instruction at the time. Finally, the instruction queue is
# * sized (entries_q), depending on the maximum burst allowed in the memory.

import sys 
sys.path.append("..") 

from pyhcl import *
from core.decode import FetchDecode
from core.isa import *
from shell.vme import *
from util.selfqueue import *


def fetch(debug: bool = False):
    p = ShellKey()
    vp = p.vcrParams
    mp = p.memParams

    class Inst(Bundle_Helper):
        def __init__(self):
            self.ld = decoupled(U.w(INST_BITS))
            self.co = decoupled(U.w(INST_BITS))
            self.st = decoupled(U.w(INST_BITS))

    class Fetch_IO(Bundle_Helper):
        def __init__(self):
            self.launch = Input(Bool)
            self.ins_baddr = Input(U.w(mp.addrBits))
            self.ins_count = Input(U.w(vp.regBits))
            self.vme_rd = VMEReadMaster()
            self.inst = Inst()

    # Fetch module
    class Fetch(Module):
        # Construct IO
        io = mapper(Fetch_IO())

        # Module logic begins
        entries_q = 1 << (mp.lenBits - 1)
        inst_q = queue(U.w(INST_BITS), entries_q)
        dec = FetchDecode()

        s1_launch = Reg(Bool)   # val s1_launch = RegNext(io.launch)
        s1_launch <<= io.launch
        pulse = io.launch & (~s1_launch)

        raddr = Reg(U.w(mp.addrBits))
        rlen = Reg(U.w(mp.lenBits))
        ilen = Reg(U.w(mp.lenBits))

        xrem = Reg(U.w(vp.regBits))
        xsize = (io.ins_count << U(1)) - U(1)
        xmax = U((1 << mp.lenBits))
        xmax_bytes = U(int((1 << mp.lenBits) * mp.dataBits / 8))

        sIdle, sReadCmd, sReadLSB, sReadMSB, sDrain = [U(i) for i in range(5)]
        state = RegInit(sIdle)

        # Control
        # TODO: Using if-elif-else to implement switch-is temporarily
        with when(state == sIdle):
            with when(pulse):
                state <<= sReadCmd
                with when(xsize < xmax):
                    rlen <<= xsize
                    ilen <<= xsize >> U(1)
                    xrem <<= U(0)
                with otherwise():
                    rlen <<= xmax - U(1)
                    ilen <<= (xmax >> U(1)) - U(1)
                    xrem <<= xsize - xmax
        with elsewhen(state == sReadCmd):
            with when(io.vme_rd_cmd_ready):
                state <<= sReadLSB
        with elsewhen(state == sReadLSB):
            with when(io.vme_rd_data_valid):
                state <<= sReadMSB
        with elsewhen(state == sReadMSB):
            with when(io.vme_rd_data_valid):
                with when(inst_q.io.count == ilen):
                    state <<= sDrain
                with otherwise():
                    state <<= sReadLSB
        with otherwise():
            # sDrain
            with when(inst_q.io.count == U(0)):
                with when(xrem == U(0)):
                    state <<= sIdle
                with elsewhen(xrem < xmax):
                    state <<= sReadCmd
                    rlen <<= xrem
                    ilen <<= xrem >> U(1)
                    xrem <<= U(0)
                with otherwise():
                    state <<= sReadCmd
                    rlen <<= xmax - U(1)
                    ilen <<= (xmax >> U(1)) - U(1)
                    xrem <<= xrem - xmax

        # read instructions from DRAM
        with when(state == sIdle):
            raddr <<= io.ins_baddr
        with elsewhen((state == sDrain) & (inst_q.io.count == U(0)) & (xrem != U(0))):
            raddr <<= raddr + xmax_bytes

        io.vme_rd_cmd_valid <<= (state == sReadCmd)
        io.vme_rd_cmd_bits_addr <<= raddr
        io.vme_rd_cmd_bits_len <<= rlen

        io.vme_rd_data_ready <<= inst_q.io.enq_ready

        lsb = Reg(U.w(mp.dataBits))
        msb = io.vme_rd_data_bits
        inst = CatBits(msb, lsb)

        with when(state == sReadLSB):
            lsb <<= io.vme_rd_data_bits

        inst_q.io.enq_valid <<= io.vme_rd_data_valid & (state == sReadMSB)
        inst_q.io.enq_bits <<= inst

        # decode
        dec.io.inst <<= inst_q.io.deq_bits

        # instruction queues
        io.inst_ld_valid <<= dec.io.isLoad & inst_q.io.deq_valid & (state == sDrain)
        io.inst_co_valid <<= dec.io.isCompute & inst_q.io.deq_valid & (state == sDrain)
        io.inst_st_valid <<= dec.io.isStore & inst_q.io.deq_valid & (state == sDrain)

        io.inst_ld_bits <<= inst_q.io.deq_bits
        io.inst_co_bits <<= inst_q.io.deq_bits
        io.inst_st_bits <<= inst_q.io.deq_bits

        # check if selected queue is ready
        deq_sel = CatBits(dec.io.isCompute, dec.io.isStore, dec.io.isLoad).to_uint()
        deq_ready = LookUpTable(deq_sel, {
            U(0x01): io.inst_ld_ready,
            U(0x02): io.inst_st_ready,
            U(0x04): io.inst_co_ready,
            ...: Bool(False)
        })

        inst_q.io.deq_ready <<= deq_ready & inst_q.io.deq_valid & (state == sDrain)

    return Fetch()


if __name__ == '__main__':
    #Emitter.dumpVerilog(Emitter.dump(Emitter.emit(fetch()), "fetch.fir"))
    #Emitter.dumpVerilog(Emitter.dump(Emitter.emit(fetch()), "fetch.fir"))
    fetch()
    