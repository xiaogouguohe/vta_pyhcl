circuit Fetch :
  module Fetch :
    input clock : Clock
    input reset : UInt<1>
    output io : {flip launch : UInt<1>, flip ins_baddr : UInt<32>, flip ins_count : UInt<32>, vme_rd_cmd_valid : UInt<1>, flip vme_rd_cmd_ready : UInt<1>, vme_rd_cmd_bits_addr : UInt<32>, vme_rd_cmd_bits_len : UInt<8>, flip vme_rd_data_bits : UInt<64>, flip vme_rd_data_valid : UInt<1>, vme_rd_data_ready : UInt<1>, inst_ld_bits : UInt<128>, inst_ld_valid : UInt<1>, flip inst_ld_ready : UInt<1>, inst_co_bits : UInt<128>, inst_co_valid : UInt<1>, flip inst_co_ready : UInt<1>, inst_st_bits : UInt<128>, inst_st_valid : UInt<1>, flip inst_st_ready : UInt<1>}
  
    io.vme_rd_cmd_bits_addr <= UInt<1>("h1")
