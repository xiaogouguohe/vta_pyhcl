# VTA pyhcl implementation of interface.axi/AXI.scala
# Author: SunnyChen
# Date:   2020-05-25
from math import log


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

        self.strbBits = int(dataBits / 8)
        self.sizeBits = 3
        self.burstBits = 2
        self.lockBits = 2
        self.cacheBits = 4
        self.protBits = 3
        self.qosBits = 4
        self.regionBits = 4
        self.respBits = 2
        self.sizeConst = round(log(int(dataBits / 8), 2))
        self.idConst = 0
        self.userConst = 1 if coherent else 0
        self.burstConst = 1
        self.lockConst = 0
        self.cacheConst = 15 if coherent else 3
        self.protConst = 4 if coherent else 0
        self.qosConst = 0
        self.regionConst = 0


if __name__ == '__main__':
    pass
