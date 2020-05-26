circuit Queue :
  module Queue :
    input clock : Clock
    input reset : UInt<1>
    output io : {count : UInt<3>, enq_cvalue : UInt<3>, deq_cvalud : UInt<3>, flip enq_bits : UInt<32>, flip enq_valid : UInt<1>, enq_ready : UInt<1>, deq_bits : UInt<32>, deq_valid : UInt<1>, flip deq_ready : UInt<1>}
  
    node do_enq = and(io.enq_valid, io.enq_ready)
    cmem ram : UInt<32>[5]
    reg _T : UInt<3>, clock with : 
      reset => (reset, UInt<3>("h0"))
    when do_enq :
      write mport _T_1 = ram[_T], clock
      _T_1 <= io.enq_bits
      node _T_2 = add(_T, UInt<1>("h1"))
      _T <= _T_2
    node do_deq = and(io.deq_valid, io.deq_ready)
    reg _T_3 : UInt<3>, clock with : 
      reset => (reset, UInt<3>("h0"))
    when do_deq :
      node _T_4 = add(_T_3, UInt<1>("h1"))
      _T_3 <= _T_4
    node _T_5 = neq(do_enq, do_deq)
    reg maybe_full : UInt<1>, clock with : 
      reset => (reset, UInt<1>("h0"))
    when _T_5 :
      maybe_full <= do_enq
    node ptr_match = eq(_T, _T_3)
    node _T_6 = not(maybe_full)
    node empty = and(ptr_match, _T_6)
    node _T_7 = not(empty)
    io.deq_valid <= _T_7
    node full = and(ptr_match, maybe_full)
    node _T_8 = not(full)
    io.enq_ready <= _T_8
    read mport _T_9 = ram[_T_3], clock
    io.deq_bits <= _T_9
    node _T_11 = mux(maybe_full, UInt<3>("h5"), UInt<1>("h0"))
    node _T_13 = gt(_T_3, _T)
    node ptr_diff = sub(_T, _T_3)
    node _T_14 = add(UInt<3>("h5"), ptr_diff)
    node _T_12 = mux(_T_13, _T_14, ptr_diff)
    node _T_10 = mux(ptr_match, _T_11, _T_12)
    io.count <= _T_10
    io.enq_cvalue <= _T
    io.deq_cvalud <= _T_3
