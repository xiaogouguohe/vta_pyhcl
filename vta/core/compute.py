from pyhcl import *
from vta.core.isa import *
from vta.shell.parameters import *
from vta.util.ext_funcs import *
from vta.shell.vme import *


def compute(debug: bool = False):
    p = ShellKey()
    mp = p.memParams
    cp = CoreKey()

    class Compute_IO(Bundle_Helper):
        def __init__(self):
            self.i_post_0 = Input(Bool)
            self.i_post_1 = Input(Bool)
            self.o_post_0 = Output(Bool)
            self.o_post_1 = Output(Bool)
            self.inst = flipped(decoupled(U.w(INST_BITS)))
            self.uop_baddr = Input(U.w(mp.addrBits))
            self.acc_baddr = Input(U.w(mp.addrBits))
            self.vme_rd_0 = VMEReadMaster()
            self.vme_rd_1 = VMEReadMaster()
            self.inp = TensorClient(tensorType="inp")
            self.wgt = TensorClient(tensorType="wgt")
            self.out = TensorClient(tensorType="out")
            finish = Output(Bool)

    class Compute(Module):
        # Base IO
        io = mapper(Compute_IO())

        sIdle, sSync, sExe = [U(i) for i in range(3)]
        state = RegInit(sIdle)

        s = Seq.tabulate(2)(_=> semaphore(counterBits=8, counterInitValue=0))

        loadUop = LoadUop()
        tensorAcc = TensorLoad(tensorType="acc")
        tensorGemm = TensorGemm()
        tensorAlu = TensorAlu()

        inst_q = queue(gentype=U.w(INST_BITS), entries=cp.instQueueEntries)

        dec = LoadDecode()
        dec.io.inst <<= inst_q.io.deq_bits

        inst_type = Cat(dec.io.isFinish,
                        dec.io.isAlu,
                        dec.io.isGemm,
                        dec.io.isLoadAcc,
                        dec.io.isLoadUop).asUInt

        sprev = inst_q.io.deq.valid & Mux(
            dec.io.pop_prev, s(0).io.sready, Bool(True))
        snext = inst_q.io.deq.valid & Mux(
            dec.io.pop_next, s(1).io.sready, Bool(True))
        start = snext & sprev
        done = LookUpTable(inst_type, {
            U(1): loadUop.io.done,
            U(2): tensorAcc.io.done,
            U(4): tensorGemm.io.done,
            U(8): tensorAlu.io.done,
            U(10): Bool(True)
        })

        # control
        with when(state == sIdle):
            with when(start):
                with when(dec.io.isSync):
                    state <<= sSync
                with elsewehen(inst_type.orR):
                    state <<= sExe
        with elsewhen(state == sSync):
            state <<= sIdle
        with elsewhen(state == sExe):
            with when(done):
                state <<= sIdle

        # instructions
        inst_q.io.enq = io.inst
        inst_q.io.deq.ready <<= (state === sExe & done) | (state == = sSync)

        # uop
        loadUop.io.start <<= state == = sIdle & start & dec.io.isLoadUop
        loadUop.io.inst <<= inst_q.io.deq.bits
        loadUop.io.baddr <<= io.uop_baddr
        io.vme_rd(0) = loadUop.io.vme_rd
        loadUop.io.uop.idx = Mux(dec.io.isGemm,
                            tensorGemm.io.uop.idx,
                            tensorAlu.io.uop.idx)

        # acc
        tensorAcc.io.start <<= state == = sIdle & start & dec.io.isLoadAcc
        tensorAcc.io.inst <<= inst_q.io.deq.bits
        tensorAcc.io.baddr <<= io.acc_baddr
        tensorAcc.io.tensor.rd.idx = Mux(dec.io.isGemm,
                                    tensorGemm.io.acc.rd.idx,
                                    tensorAlu.io.acc.rd.idx)
        tensorAcc.io.tensor.wr = Mux(dec.io.isGemm,
                                tensorGemm.io.acc.wr,
                                tensorAlu.io.acc.wr)
        io.vme_rd(1) = tensorAcc.io.vme_rd

        # gemm
        tensorGemm.io.start <<= state == = sIdle & start & dec.io.isGemm
        tensorGemm.io.inst <<= inst_q.io.deq.bits
        tensorGemm.io.uop.data.valid <<= loadUop.io.uop.data.valid & dec.io.isGemm
        tensorGemm.io.uop.data.bits = loadUop.io.uop.data.bits
        tensorGemm.io.inp = io.inp
        tensorGemm.io.wgt = io.wgt
        tensorGemm.io.acc.rd.data.valid <<= tensorAcc.io.tensor.rd.data.valid & dec.io.isGemm
        tensorGemm.io.acc.rd.data.bits = tensorAcc.io.tensor.rd.data.bits
        tensorGemm.io.out.rd.data.valid <<= io.out.rd.data.valid & dec.io.isGemm
        tensorGemm.io.out.rd.data.bits = io.out.rd.data.bits

        # alu
        tensorAlu.io.start <<= state == = sIdle & start & dec.io.isAlu
        tensorAlu.io.inst <<= inst_q.io.deq.bits
        tensorAlu.io.uop.data.valid <<= loadUop.io.uop.data.valid & dec.io.isAlu
        tensorAlu.io.uop.data.bits = loadUop.io.uop.data.bits
        tensorAlu.io.acc.rd.data.valid <<= tensorAcc.io.tensor.rd.data.valid & dec.io.isAlu
        tensorAlu.io.acc.rd.data.bits = tensorAcc.io.tensor.rd.data.bits
        tensorAlu.io.out.rd.data.valid <<= io.out.rd.data.valid & dec.io.isAlu
        tensorAlu.io.out.rd.data.bits = io.out.rd.data.bits

        # out
        io.out.rd.idx = Mux(dec.io.isGemm,
                            tensorGemm.io.out.rd.idx,
                            tensorAlu.io.out.rd.idx)
        io.out.wr = Mux(dec.io.isGemm, tensorGemm.io.out.wr,
                        tensorAlu.io.out.wr)

        # semaphore
        s(0).io.spost <<= io.i_post(0)
        s(1).io.spost <<= io.i_post(1)
        s(0).io.swait <<= dec.io.pop_prev & (state === sIdle & start)
        s(1).io.swait <<= dec.io.pop_next & (state === sIdle & start)
        io.o_post(0) <<= dec.io.push_prev & ((state === sExe & done) | (state === sSync))
        io.o_post(1) <<= dec.io.push_next & ((state === sExe & done) | (state === sSync))

        # finish
        io.finish <<= state === sExe & done & dec.io.isFinish


        #debug
        with when(debug):
            #start
            with when((state==sIdle) & (start)):
                with when(dec.io.isSync):
                    printf("[Compute] start sync\n")
                with elsewhen(dec.io.isLoadUop):
                    printf("[Compute] start load uop\n")
                with elsewhen(dec.io.isLoadAcc):
                    printf("[Compute] start load acc\n")
                with elsewhen(dec.io.isGemm):
                    printf("[Compute] start gemm\n")
                with elsewhen(dec.io.isAlu):
                    printf("[Compute] start alu\n")
                with elsewhen(dec.io.isFinish):
                    printf("[Compute] start finish\n")
            #done
            with elsewhen(state == sSync):
                printf("[Compute] done sync\n")
            with elsewhen(state == sExe):
                with when(done):
                    with when(dec.io.isLoadUop):
                        printf("[Compute] start load uop\n")
                    with elsewhen(dec.io.isLoadAcc):
                        printf("[Compute] start load acc\n")
                    with elsewhen(dec.io.isGemm):
                        printf("[Compute] start gemm\n")
                    with elsewhen(dec.io.isAlu):
                        printf("[Compute] start alu\n")
                    with elsewhen(dec.io.isFinish):
                        printf("[Compute] start finish\n")

    return Compute()
