circuit Demo :
  module Demo :
    input clock : Clock
    input reset : UInt<1>
    output io : {cmd_valid : UInt<1>, flip cmd_ready : UInt<1>, cmd_bits_addr : UInt<32>, cmd_bits_len : UInt<8>, flip data_bits : UInt<64>, flip data_valid : UInt<1>, data_ready : UInt<1>}
  
    io.cmd_valid <= UInt<1>("h1")
    io.cmd_bits_addr <= UInt<2>("h2")
    io.cmd_bits_len <= UInt<2>("h3")
    io.data_ready <= UInt<1>("h1")
