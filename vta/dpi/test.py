from pyhcl import *

import sys
sys.path.append("..")
from interface_axi.axi import *
from shell.parameters import *
from pyhcl.ir.utils import *

class TestBun(Bundle):
    def __init__(self):
        super(TestBun, self).__init__()
        dic = self._kv
        dic["a"] = Decoupled(U.w(1))

class TestBlackBox(BlackBox):
    io = IO(
        x=Output(TestBun()),
    )

class TestInnerMod(Module):
    io = IO(
        x=Input(TestBun()),
        y=Output(TestBun()),
        z=Input(TestBun()),
    )

    io.y.a.valid <<= io.z.a.valid

# class VTAMem(Module):
#     io = IO(
#         axi=Output(AXIClient()),
#     )
#     mem_dpi = VTAMemDPI()
#     mem_axi = vtaMemDPIToAXI()
#
#     #ir.utils.connect_all(mem_dpi.io.dpi, mem_axi.io.dpi)
#     ir.utils.connect_all(mem_axi.io.axi, io.axi)

class TestMod(Module):
    io1 = IO(
        x=Output(AXIClient()),
    )

    io2 = IO(
        a=Input(AXIClient()),
    )

    #print(type(io1.x))
    connect_all(io1.x, io2.a)

    # io = IO(
    #     x=Input(TestBun()),
    # )
    #
    # blackBox = TestBlackBox()
    # innerMod = TestInnerMod()
    # blackBox.io.x.a.valid <<= innerMod.io.x.a.valid

    # io = IO(
    #     x=Output(TestBun()),
    #     y=Output(Flip(TestBun())),
    #     #y=Input(TestBun()),
    # )
    #
    # io.x.a.bits <<= io.y.a.bits
    # io.x.a.valid <<= io.y.a.valid

    # tmp = U.w(1).flip()
    #
    # io = IO(
    #     x=Output(U.w(1)),
    #     y=Output(tmp),
    #     #y=Input(U.w(1)),
    # )
    #
    # io.x <<= io.y

    # io = IO(
    #     x=Output(Bundle(
    #         a=U.w(1),
    #         b=U.w(1).flip()
    #     ))
    # )
    #
    # io.x.a <<= io.x.b

    # io = IO(
    #     x=Output(Decoupled(U.w(1))),
    # )
    #
    # io.x.valid <<= Input(U.w(1))
    # io.x.bits <<= Input(U.w(1))

    # io = IO(
    #     x=Output(Bundle(
    #         a=U.w(1),
    #         b=U.w(1).flip(),
    #         c=(U.w(1).flip()).flip()
    #     ))
    # )
    #
    # io.x.a <<= Input(U.w(1))

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(TestMod()), "TestMod.fir"))

