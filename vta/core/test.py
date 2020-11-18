import sys
sys.path.append("..")

from pyhcl import *
from shell.vcr import *
from shell.vme import *

vcrMaster = VCRMaster()
print("type of vcrMaster:", type(vcrMaster))
vcr = VCR()

