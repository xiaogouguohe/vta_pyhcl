from pyhcl import *
from pyhcl.core._repr import *

tmp = Vec(3, U.w(1))
print(tmp[0])
print(type(tmp[0]))
print(isinstance(tmp[0], Index))

