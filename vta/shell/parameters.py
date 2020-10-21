# File to contains paramters
# Author: SunnyChen
# Date:   2020-05-25
import sys 
sys.path.append("..") 
from interface_axi.axi import AXIParams


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
    nUCnt = 1
    regBits = 32


# Shell parameters
class ShellParams:
    hostParams = AXIParams()
    memParams = AXIParams()
    vcrParams = VCRParams()
    vmeParams = VMEParams()


class ShellKey(ShellParams):
    pass


class CoreParams:
    batch: int = 1
    blockOut: int = 16
    blockIn: int = 16
    inpBits: int = 8
    wgtBits: int = 8
    uopBits: int = 32
    accBits: int = 32
    outBits: int = 8
    uopMemDepth: int = 512
    inpMemDepth: int = 512
    wgtMemDepth: int = 512
    accMemDepth: int = 512
    outMemDepth: int = 512
    instQueueEntries: int = 32


class CoreKey(CoreParams):
    pass
