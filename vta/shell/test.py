from pyhcl import *
from pyhcl import ir
from pyhcl.core._repr import *

# a = U.w(1)
# b = Decoupled(a)
# dic = b._kv
# for key in dic:
#     print(key, dic[key], type(dic[key]))
#
# c = Flip(b)
# dic = b._kv
# for key in dic:
#     print(key, dic[key], type(dic[key]))

class Inner(Bundle):
    def __init__(self):
        super(Inner, self).__init__()
        dic = self._kv
        dic["m"] = U.w(1)
        dic["n"] = U.w(1)


class TestBun(Bundle):
    def __init__(self):
        super(TestBun, self).__init__()
        dic = self._kv
        dic["inner"] = Inner()
        dic["a"] = U.w(1)
        dic["b"] = U.w(1)

class VTAHostDPIMaster(Bundle):  # with VTAHostDPIParams
    def __init__(self):
        super().__init__()
        dic = self._kv
        dic["resp"] = Flip(Valid(U.w(32)))  # VTAHostDPIParams().dpiDataBits

class VTAHostDPIClient(Bundle):  # with VTAHostDPIParams
    def __init__(self):
        super().__init__()
        dic = self._kv
        dic["resp"] = Valid(U.w(32))  # VTAHostDPIParams().dpiDataBits

class VTAHostDPI(Module):  # extends BlackBox with HasBlackBoxResource {
    io = IO(
        #dpi=Output(VTAHostDPIMaster()),
        dpi = Output(Valid(U.w(1))),
    )

class VTAHostDPIToAXI(Module):
    io = IO(
        #dpi = Output(VTAHostDPIClient()),
        dpi = Output(Flip(Valid(U.w(1)))),
    )

class DPI(BlackBox):
    io = IO(
        dpi1 = Output(Valid(U.w(1))),
        dpi2 = Output(Flip(Valid(U.w(1)))),
    )

class TestMod(Module):
    host_dpi = VTAHostDPI()
    host_axi = VTAHostDPIToAXI()
    host_axi.io.dpi.bits <<= host_dpi.io.dpi.bits

    # dpi = DPI()
    # dpi.io.dpi1.bits <<= dpi.io.dpi2.bits

    # io = IO(
    #     dpi1=Output(Valid(U.w(1))),
    #     dpi2=Output(Flip(Valid(U.w(1)))),
    # )
    # io.dpi1.valid <<= io.dpi2.valid
    # io.dpi1.bits <<= io.dpi2.bits



    # testBun = TestBun()
    # print("testBun:", testBun)
    # io1 = IO(
    #     x = Output(Valid(U.w(1))),
    #     #y = Input(TestBun())
    # )
    # io2 = IO(
    #     x = Output(Flip(Valid(U.w(1)))),
    # )
    #
    # #ir.utils.auto_connect2(io1.x, io2.x)
    # io1.x.valid <<= io2.x.valid
    # io1.x.bits <<= io2.x.bits

    # print("io:", io)
    # print("type of io:", io)
    # print("io.value:", io.value)
    # print("type of io.value:", type(io.value))
    # print("io.x:", io.x)
    # print("type of io.x:", type(io.x))
    # print("io.x.value:", io.x.value)
    # print("type of io.x.value:", type(io.x.value))
    # print("io.x.a:", io.x.a)
    # print("type of io.x.a:", type(io.x.a))
    # print("io.x.a.value:", io.x.a.value)
    # print("type of io.x.a.value:", type(io.x.a.value))
    # print("io.x.inner:", io.x.inner)
    # print("type of io.x.inner:", type(io.x.inner))
    # print("io.x.inner.value:", io.x.inner.value)
    # print("type of io.x.inner.value:", type(io.x.inner.value))
    # print()
    # #dic = io.x.value.typ._kv
    # dic = io.x.__dict__
    # for key in dic:
    #     print("key:", key)
    #     print("dic[key]:", dic[key])
    #     print()
    # print("io.x.a:", io.x.a)
    # print("io.x.a.value:", io.x.a.value)
    # print("io.x.value.typ._kv['a']:", io.x.value.typ._kv["a"])
    # print()
    # print(io.x)
    # print(io.value.x)
    #io.x.a <<= io.y.a
    #io.x.b <<= io.y.b
    #io.x.inner <<= io.y.inner

if __name__ == '__main__':
    Emitter.dumpVerilog(Emitter.dump(Emitter.emit(TestMod()), "TestMod.fir"))

