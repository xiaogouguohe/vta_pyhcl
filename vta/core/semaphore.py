# VTA pyhcl implementation of core/Load.scala
# Author: SunnyChen
# Date:   2020-06-08
from pyhcl import *


"""
    Semaphore.
    
    This semaphore is used instead of push/pop fifo, used in the initial
    version of VTA. This semaphore is incremented (spost) or decremented (swait)
    depending on the push and pop fields on instructions to prevent RAW and WAR
    hazards.
"""

''' class Semaphore(Module):
    io = IO(
        spost=Input(Bool),
        swait=Input(Bool),
        sready=Output(Bool)
    )
    cnt = RegInit(U.w(1)(1))

    with when(io.spost & (~io.swait) & (cnt != U((1 << 1) - 1))): # U should be S
        cnt <<= cnt + U(1)
    with when((~io.spost) & io.swait & (cnt != U(0))):
        cnt <<= cnt - U(1)
    io.sready <<= (cnt != U(0)) '''

def semaphore(counterBits: int = 1, counterInitValue: int = 1):
    class Semaphore(Module):
        io = IO(
            spost=Input(Bool),
            swait=Input(Bool),
            sready=Output(Bool)
        )
        cnt = RegInit(U.w(counterBits)(counterInitValue))

        with when(io.spost & (~io.swait) & (cnt != U((1 << counterBits) - 1))): # U should be S
            cnt <<= cnt + U(1)
        with when((~io.spost) & io.swait & (cnt != U(0))):
            cnt <<= cnt - U(1)
        io.sready <<= (cnt != U(0))

    return Semaphore()

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(semaphore()), "Semaphore.fir"))

