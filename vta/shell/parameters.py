# File to contains paramters
# Author: SunnyChen
# Date:   2020-05-25
from vta.interface_axi.axi import AXIParams


class VMEParams:
    '''
        VME parameters.
        These parameters are used on VME interfaces and modules.
    '''
    nReadClients: int = 5
    nWriteClients: int = 1


class VCRParams:
    nCtrl = 1
    nECnt = 1
    nVals = 1
    nPtrs = 6
    regBits = 32


# Shell parameters
class ShellParams:
    hostParams = AXIParams()
    memParams = AXIParams()
    vcrParams = VCRParams()
    vmeParams = VMEParams()


class ShellKey(ShellParams):
    pass
