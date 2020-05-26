# VTA pyhcl implementation of core/ISA.scala
# Author: SunnyChen
# Date:   2020-05-25
from pyhcl import *

# ISA constants
INST_BITS = 128

OP_BITS = 3

M_DEP_BITS = 4
M_ID_BITS = 2
M_SRAM_OFFSET_BITS = 16
M_DRAM_OFFSET_BITS = 32
M_SIZE_BITS = 16
M_STRIDE_BITS = 16
M_PAD_BITS = 4

C_UOP_BGN_BITS = 13
C_UOP_END_BITS = 14
C_ITER_BITS = 14
C_AIDX_BITS = 11
C_IIDX_BITS = 11
C_WIDX_BITS = 10
C_ALU_DEC_BITS = 2
C_ALU_OP_BITS = 3
C_ALU_IMM_BITS = 16

Y = Bool(True)
N = Bool(False)

U.w(OP_BITS)(0)
OP_L = U.w(OP_BITS)(0)
OP_S = U.w(OP_BITS)(1)
OP_G = U.w(OP_BITS)(2)
OP_F = U.w(OP_BITS)(3)
OP_A = U.w(OP_BITS)(4)
OP_X = U.w(OP_BITS)(5)

ALU_OP_NUM = 5
ALU_OP = [U(i) for i in range(5)]

M_ID_U = U.w(M_ID_BITS)(0)
M_ID_W = U.w(M_ID_BITS)(1)
M_ID_I = U.w(M_ID_BITS)(2)
M_ID_A = U.w(M_ID_BITS)(3)


if __name__ == '__main__':
    print(ALU_OP[3])
