# Implements functions which not implement in current PyHCL
# Author: SunnyChen
# Date:   2020-05-25


from pyhcl import *


# class Demo:
#     dataBits = ShellKey().memParams.dataBits
#     data = U.w(dataBits)


class BaseType:
    pass


def decoupled(io, obj, is_fliped=False):
    '''
        Usage of decoupled:
        io: io ports wants to decoupled with
        obj: objects contain type information
    '''
    assert isinstance(obj, BaseType)

    obj_vars = vars(obj)
    for keys in obj_vars:
        if isinstance(obj_vars[keys], type):
            if not is_fliped:
                io._ios[keys+'_bits'] = Output(obj_vars[keys])
                io._ios[keys+'_valid'] = Output(Bool)
                io._ios[keys+'_ready'] = Input(Bool)
            else:
                io._ios[keys + '_bits'] = Input(obj_vars[keys])
                io._ios[keys + '_valid'] = Input(Bool)
                io._ios[keys + '_ready'] = Output(Bool)
        elif isinstance(obj_vars[keys], BaseType):
            inner = obj_vars[keys]
            inner_vars = vars(inner)
            if not is_fliped:
                io._ios[keys + '_valid'] = Output(Bool)
                io._ios[keys + '_ready'] = Input(Bool)
                for innkeys in inner_vars:
                    if isinstance(inner_vars[innkeys], type):
                        io._ios[keys+'_bits_'+innkeys] = Output(inner_vars[innkeys])
            else:
                io._ios[keys + '_valid'] = Input(Bool)
                io._ios[keys + '_ready'] = Output(Bool)
                for innkeys in inner.__dict__:
                    if isinstance(inner.__dict__[innkeys], type):
                        io._ios[keys + '_bits_' + innkeys] = Input(inner.__dict__[innkeys])


def cat_io(base_io, ext_io, sub_name):
    '''
        Cat two io definitions
    '''
    for keys in ext_io._ios:
        base_io._ios[sub_name+'_'+keys] = ext_io._ios[keys]
