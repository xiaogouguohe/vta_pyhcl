# VTA pyhcl implementation of interface.axi/AXI.scala
# Author: SunnyChen
# Date:   2020-05-25
from math import *


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
        self.lenBits = lenBits
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


if __name__ == '__main__':
    pass
