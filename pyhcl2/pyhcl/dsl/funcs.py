from functools import reduce


def CatBits(*args):
    if len(args) == 1:
        return args[0]
    else:
        from pyhcl.core._repr import Cat
        half = len(args) >> 1
        lf = CatBits(*args[:half])
        rt = CatBits(*args[half:])
        return Cat(lf, rt)


def CatVecL2H(vec):
    return CatBits(*[i for i in OneDimensionalization(vec)])


def CatVecH2L(vec):
    return CatBits(*[i for i in OneDimensionalization(vec).reverse()])


def Sum(vec):
    return reduce(lambda x, y: x + y, vec)


def OneDimensionalization(vec):
    a = vec
    lvl = a.lvl
    for _ in range(lvl - 1):
        a = a.flatten()
    return a


def Decoupled(typ):
    from .bundle import Bundle
    from .cdatatype import U
    return Bundle(
        valid = U.w(1), #Output
        ready = U.w(1).flip(), #Input
        bits = typ
    )


def Valid(typ):
    from .bundle import Bundle
    from .cdatatype import U
    from .cio import Output
    from ..core._repr import CType
    from .vector import Vec

    coupled = Bundle(
        valid=U.w(1),
        bits=Output(typ)
    )

    if isinstance(typ, CType) or isinstance(typ, type):
        coupled.bits = Output(typ)
    elif isinstance(typ, Vec):
        coupled.bits = Output(typ)
    #elif isinstance(typ, List):
        #print("basetype:", basetype)
        #print("type(basetype)", type(basetype))
        #print("len(basetype):", len(basetype))
        #coupled.bits = [Output(basetype[i]) for i in range(len(basetype))]
        coupled.bits = Output(typ)
    elif isinstance(typ, Bundle):
        coupled.bits = Bundle()
        dic = typ.__dict__
        for keys in dic:
            #coupled.bits.__dict__[keys] = valid(keys)
            if isinstance(dic[keys], CType) or isinstance(dic[keys], type):
                coupled.bits.__dict__[keys] = Output(dic[keys])
    return coupled
