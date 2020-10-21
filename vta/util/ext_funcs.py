# Implements functions which not implement in current PyHCL
# Author: SunnyChen
# Date:   2020-05-25
from typing import List
from pyhcl import *
from math import *


# class Demo:
#     dataBits = ShellKey().memParams.dataBits
#     data = U.w(dataBits)
from pyhcl.core._meta_pub import Pub
from pyhcl.core._repr import CType


class BaseType:
    pass


# Enhance current io functions
class Bundle_Helper:
    pass


def mapper_helper(bundle, dic=None, prefix=""):
    tdic = {} if dic is None else dic

    for k in bundle.__dict__:
        print("k:", k)
        v = bundle.__dict__[k]
        print(type(v))
        if isinstance(v, Pub):
            print("v is Pub")
            if prefix == "":
                tdic[k] = v
            else:
                tdic[prefix+"_"+k] = v
        elif isinstance(v, Bundle_Helper):
            print("v is Bundle_Helper")
            if prefix == "":
                mapper_helper(v, tdic, k)
            else:
                mapper_helper(v, tdic, prefix+"_"+k)
        elif isinstance(v, List):
            print("v is List")
            for i in range(len(v)):
                if isinstance(v[i], Pub):
                    if prefix == "":
                        tdic[k+"_"+str(i)] = v[i]
                    else:
                        tdic[prefix+"_"+k+"_"+str(i)] = v[i]
                elif isinstance(v[i], Bundle_Helper):
                    if prefix == "":
                        mapper_helper(v[i], tdic, k+"_"+str(i))
                    else:
                        mapper_helper(v[i], tdic, prefix+"_"+k+"_"+str(i))
        else:
            print("v is else")
            pass

    print("=====>")
    for k in tdic:
        print(k, tdic[k])
    print("<=====") 
    return tdic

def mapper(bundle):
    dct = mapper_helper(bundle)
    io = IO(**dct)

    return io


def decoupled(basetype):
    coupled = Bundle_Helper()
    coupled.valid = Output(Bool)
    coupled.ready = Input(Bool)

    if isinstance(basetype, CType) or isinstance(basetype, type):
        coupled.bits = Output(basetype)
    elif isinstance(basetype, BaseType):
        coupled.bits = Bundle_Helper()
        dic = basetype.__dict__
        for keys in dic:
            if isinstance(dic[keys], CType) or isinstance(dic[keys], type):
                coupled.bits.__dict__[keys] = Output(dic[keys])

    return coupled


def valid(basetype):
    coupled = Bundle_Helper()
    coupled.valid = Output(Bool)

    if isinstance(basetype, CType) or isinstance(basetype, type):
        coupled.bits = Output(basetype)
    elif isinstance(basetype, Vec):
        coupled.bits = Output(basetype)
    elif isinstance(basetype, BaseType):
        coupled.bits = Bundle_Helper()
        dic = basetype.__dict__
        for keys in dic:
            if isinstance(dic[keys], CType) or isinstance(dic[keys], type):
                coupled.bits.__dict__[keys] = Output(dic[keys])

    return coupled


def base_flipped(obj):
    return Output(obj.typ) if isinstance(obj.value, Input) else Input(obj.typ)


def flipped(bundle):
    dic = bundle.__dict__
    for keys in dic:
        if isinstance(dic[keys], Pub):
            dic[keys] = base_flipped(dic[keys])
        elif isinstance(dic[keys], Bundle_Helper):
            flipped(dic[keys])

    return bundle


def log2ceil(v):
    return ceil(log(v, 2))


def Mem_maskwrite(m, data, mask, length):
    for i in range(length):
        with when(~(mask[i])):
            data[i] <<= U(0)
    m <<= data