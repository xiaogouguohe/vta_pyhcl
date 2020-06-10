#VTA pyhcl implementation of core/Store.scala
#Aothor:Lois799
#created on 2020/06/10
#Store.scala 与 Load.scala 较相似，我重构Store.scala是参考了原有的Load.scala和Sunny Chen重构得到的load.py
#通过对比Load.scala和load.py，及学习了部分python与部分scala语法，所得该store.py;
#可能有些遗漏，迷惑，已标注
/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

from pyhcl import *
from vta.core.isa import *
from vta.shell.parameters import *
from vta.util.ext_funcs import *
from vta.shell.vme import *

/** Store.
  *
  * Store results back to memory (DRAM) from scratchpads (SRAMs).
  * This module instantiate the TensorStore unit which is in charge
  * of storing 1D and 2D tensors to main memory.
  */
  
  #参考load.py对Load 的重构
  def store(debug:bool = False):
    p = ShellKey()
    mp= p.memParams
    
    class Inst(baseType):
      def __init__(self):
        self.inst = U.w(INST_BITS)
        
    class Store(Module):
      #Base IO
      io=IO(
        i_post=Input(Bool),
        o_post=Output(Bool),
        out_baddr=Input(U.w(mp.addrBits)),
        out = new TensorClient(tensorType = "out")
        
        /*val inst = Flipped(Decoupled(UInt(INST_BITS.W)))/*可能是不用重构的，也可能是在后面*/      
       ）
      decoupled(io, Inst(), is_fliped=True)
      
      #val vme_wr = new VMEWriteMaster //参考load.py对vme_rd = Vec(2, new VMEReadMaster)的重构方法
      VMEReadMaster_io = VMEReadMaster()
      cat_io(io, VMEReadMaster_io, 'vme_wr')
      
      #val sIdle :: sSync :: sExe :: Nil = Enum(3)
      #val state = RegInit(sIdle)
      sIdle, sSync, sExe = [U(i) for i in range(3)]
      state = RegInit(sIdle)
      
      
