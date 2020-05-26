# Hardware queue implementation of Chisel3 library (Decoupled.scala)
# Author: SunnyChen
# Date: 2020-05-26
from math import *
from pyhcl import *
from vta.util.ext_funcs import *


def ispow2(n):
    return (n & (n-1)) == 0


class Counter:
    def __init__(self, n):
        assert n >= 0

        self.n = n
        self.value = RegInit(U.w(ceil(log(n, 2)))(0)) if n > 1 else U(0)

    def inc(self):
        if self.n > 1:
            wrap = self.value == S(self.n - 1)
            self.value <<= self.value + U(1)

            # is n the power of 2?
            if ispow2(self.n) != 0:
                with when(wrap):
                    self.value <<= U(0)

            return wrap
        else:
            return Bool(True)


def queue(gentype, entries):
    class Enq(BaseType):
        def __init__(self):
            self.enq = gentype

    class Deq(BaseType):
        def __init__(self):
            self.deq = gentype

    class Queue(Module):
        # Base IO
        io = IO(
            count=Output(U.w(ceil(log(entries, 2)))),

            # # debug
            # enq_cvalue=Output(U.w(ceil(log(entries, 2)))),
            # deq_cvalud=Output(U.w(ceil(log(entries, 2))))
        )
        decoupled(io, Enq(), is_fliped=True)
        decoupled(io, Deq())

        # Module Logic
        ram = Mem(entries, gentype)
        enq_ptr = Counter(entries)
        deq_ptr = Counter(entries)
        maybe_full = RegInit(Bool(False))

        ptr_match = enq_ptr.value == deq_ptr.value
        empty = ptr_match & (~maybe_full)
        full = ptr_match & maybe_full
        do_enq = io.enq_valid & io.enq_ready
        do_deq = io.deq_valid & io.deq_ready

        with when(do_enq):
            ram[enq_ptr.value] <<= io.enq_bits
            enq_ptr.inc()

        with when(do_deq):
            deq_ptr.inc()

        with when(do_enq != do_deq):
            maybe_full <<= do_enq

        io.deq_valid <<= ~empty
        io.enq_ready <<= ~full
        io.deq_bits <<= ram[deq_ptr.value]

        ptr_diff = enq_ptr.value - deq_ptr.value
        if ispow2(entries):
            io.count <<= Mux(maybe_full & ptr_match, U(entries), U(0)) | ptr_diff
        else:
            io.count <<= Mux(ptr_match,
                             Mux(maybe_full, U(entries), U(0)),
                             Mux(deq_ptr.value > enq_ptr.value,
                                 U(entries) + ptr_diff, ptr_diff))

        # # debug
        # io.enq_cvalue <<= enq_ptr.value
        # io.deq_cvalud <<= deq_ptr.value

    return Queue()


if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(queue(U.w(32), 4)), "Queue.fir"))
