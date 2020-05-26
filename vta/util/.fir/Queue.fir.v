module Queue(
  input         clock,
  input         reset,
  output [2:0]  io_count,
  output [2:0]  io_enq_cvalue,
  output [2:0]  io_deq_cvalud,
  input  [31:0] io_enq_bits,
  input         io_enq_valid,
  output        io_enq_ready,
  output [31:0] io_deq_bits,
  output        io_deq_valid,
  input         io_deq_ready
);
  reg [31:0] ram [0:4];
  reg [31:0] _RAND_0;
  wire [31:0] ram__T_9_data;
  wire [2:0] ram__T_9_addr;
  reg [31:0] _RAND_1;
  wire [31:0] ram__T_1_data;
  wire [2:0] ram__T_1_addr;
  wire  ram__T_1_mask;
  wire  ram__T_1_en;
  wire  do_enq;
  reg [2:0] _T;
  reg [31:0] _RAND_2;
  wire [3:0] _T_2;
  wire [3:0] _GEN_5;
  wire  do_deq;
  reg [2:0] _T_3;
  reg [31:0] _RAND_3;
  wire [3:0] _T_4;
  wire [3:0] _GEN_6;
  wire  _T_5;
  reg  maybe_full;
  reg [31:0] _RAND_4;
  wire  ptr_match;
  wire  _T_6;
  wire  empty;
  wire  full;
  wire [2:0] _T_11;
  wire  _T_13;
  wire [3:0] ptr_diff;
  wire [4:0] _T_14;
  wire [4:0] _T_12;
  wire [4:0] _T_10;
  assign ram__T_9_addr = _T_3;
  `ifndef RANDOMIZE_GARBAGE_ASSIGN
  assign ram__T_9_data = ram[ram__T_9_addr];
  `else
  assign ram__T_9_data = ram__T_9_addr >= 3'h5 ? _RAND_1[31:0] : ram[ram__T_9_addr];
  `endif // RANDOMIZE_GARBAGE_ASSIGN
  assign ram__T_1_data = io_enq_bits;
  assign ram__T_1_addr = _T;
  assign ram__T_1_mask = 1'h1;
  assign ram__T_1_en = io_enq_valid & io_enq_ready;
  assign do_enq = io_enq_valid & io_enq_ready;
  assign _T_2 = _T + 3'h1;
  assign _GEN_5 = do_enq ? _T_2 : {{1'd0}, _T};
  assign do_deq = io_deq_valid & io_deq_ready;
  assign _T_4 = _T_3 + 3'h1;
  assign _GEN_6 = do_deq ? _T_4 : {{1'd0}, _T_3};
  assign _T_5 = do_enq != do_deq;
  assign ptr_match = _T == _T_3;
  assign _T_6 = ~ maybe_full;
  assign empty = ptr_match & _T_6;
  assign full = ptr_match & maybe_full;
  assign _T_11 = maybe_full ? 3'h5 : 3'h0;
  assign _T_13 = _T_3 > _T;
  assign ptr_diff = _T - _T_3;
  assign _T_14 = 4'h5 + ptr_diff;
  assign _T_12 = _T_13 ? _T_14 : {{1'd0}, ptr_diff};
  assign _T_10 = ptr_match ? {{2'd0}, _T_11} : _T_12;
  assign io_count = _T_10[2:0];
  assign io_enq_cvalue = _T;
  assign io_deq_cvalud = _T_3;
  assign io_enq_ready = ~ full;
  assign io_deq_bits = ram__T_9_data;
  assign io_deq_valid = ~ empty;
`ifdef RANDOMIZE_GARBAGE_ASSIGN
`define RANDOMIZE
`endif
`ifdef RANDOMIZE_INVALID_ASSIGN
`define RANDOMIZE
`endif
`ifdef RANDOMIZE_REG_INIT
`define RANDOMIZE
`endif
`ifdef RANDOMIZE_MEM_INIT
`define RANDOMIZE
`endif
`ifndef RANDOM
`define RANDOM $random
`endif
`ifdef RANDOMIZE_MEM_INIT
  integer initvar;
`endif
`ifndef SYNTHESIS
initial begin
  `ifdef RANDOMIZE
    `ifdef INIT_RANDOM
      `INIT_RANDOM
    `endif
    `ifndef VERILATOR
      `ifdef RANDOMIZE_DELAY
        #`RANDOMIZE_DELAY begin end
      `else
        #0.002 begin end
      `endif
    `endif
  _RAND_0 = {1{`RANDOM}};
  `ifdef RANDOMIZE_MEM_INIT
  for (initvar = 0; initvar < 5; initvar = initvar+1)
    ram[initvar] = _RAND_0[31:0];
  `endif // RANDOMIZE_MEM_INIT
  _RAND_1 = {1{`RANDOM}};
  `ifdef RANDOMIZE_REG_INIT
  _RAND_2 = {1{`RANDOM}};
  _T = _RAND_2[2:0];
  `endif // RANDOMIZE_REG_INIT
  `ifdef RANDOMIZE_REG_INIT
  _RAND_3 = {1{`RANDOM}};
  _T_3 = _RAND_3[2:0];
  `endif // RANDOMIZE_REG_INIT
  `ifdef RANDOMIZE_REG_INIT
  _RAND_4 = {1{`RANDOM}};
  maybe_full = _RAND_4[0:0];
  `endif // RANDOMIZE_REG_INIT
  `endif // RANDOMIZE
end // initial
`endif // SYNTHESIS
  always @(posedge clock) begin
    if(ram__T_1_en & ram__T_1_mask) begin
      ram[ram__T_1_addr] <= ram__T_1_data;
    end
    if (reset) begin
      _T <= 3'h0;
    end else begin
      _T <= _GEN_5[2:0];
    end
    if (reset) begin
      _T_3 <= 3'h0;
    end else begin
      _T_3 <= _GEN_6[2:0];
    end
    if (reset) begin
      maybe_full <= 1'h0;
    end else if (_T_5) begin
      maybe_full <= do_enq;
    end
  end
endmodule
