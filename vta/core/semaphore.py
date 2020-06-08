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


def semaphore(counterBits: int = 1, counterInitValue: int = 1):
    class Semaphore(Module):
        io = IO(
            spost=Input(Bool),
            swait=Input(Bool),
            sready=Output(Bool)
        )
        cnt = RegInit(U.w(counterBits)(counterInitValue))

        with when(io.spost & (~io.swait) & (cnt != S((1 << counterBits) - 1))):
            cnt <<= cnt + U(1)
        with when((~io.spost) & io.swait & (cnt != U(0))):
            cnt <<= cnt - U(1)

    return Semaphore()
