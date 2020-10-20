from pyhcl import *
from axi import *

def test_AXIParams_init():
    axiParams = AXIParams()
    print("in func test_AXIParams_init, axiParams," + \
        "\ncoherent:", axiParams.coherent,\
        "\nidBits:", axiParams.idBits, \
        "\naddrBits:", axiParams.addrBits, \
        "\ndataBits:", axiParams.dataBits, \
        "\nlenBits:", axiParams.lenBits, \
        "\nuserBits:", axiParams.userBits, \
        )

def test_AXIBase_init():
    axiParams = AXIParams() 
    axiBase = AXIBase(axiParams)
    print("in func test_AXIBase_init, axiBase.params," + \
        "\ncoherent:", axiBase.params.coherent,\
        "\nidBits:", axiBase.params.idBits, \
        "\naddrBits:", axiBase.params.addrBits, \
        "\ndataBits:", axiBase.params.dataBits, \
        "\nlenBits:", axiBase.params.lenBits, \
        "\nuserBits:", axiBase.params.userBits, \
        )

def test_AXILiteAddress_init():
    axiParams = AXIParams()
    axiLiteAddress = AXILiteAddress(axiParams)
    print("in func test_AXILiteAddress_init, axiLiteAddress," + \
        "\naddr:", axiLiteAddress.addr)

def test_AXILiteWriteData_init():
    axiParams = AXIParams()
    axiLiteWriteData = AXILiteWriteData(axiParams)
    print("in func test_AXILiteAddress_init, AXILiteWriteData," + \
        "\ndata:", axiLiteWriteData.data, \
        "\nstrb:", axiLiteWriteData.strb)

#AXILiteWriteResponse
#AXILiteReadData

def test_AXILiteMaster_init():
    axiParams = AXIParams()
    axiLiteMaster = AXILiteMaster(axiParams)

def test_AXILiteClient_init():
    axiParams = AXIParams()
    axiLiteClient = AXILiteClient(axiParams)
    print("type of axiLiteClient:", type(axiLiteClient))
    print("type of w:", type(axiLiteClient.w))

if __name__ == "__main__":
    #test_AXIParams_init()
    #test_AXIBase_init()
    #test_AXILiteAddress_init()
    #test_AXILiteWriteData_init()
    #test_AXILiteMaster_init()
    test_AXILiteClient_init()