// dummy wrapper
module top (
    input wire clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(32):0] s_chan,
    input wire s_last,
    input wire [$clog2(112):0] s_col,
    input wire [$clog2(112):0] s_row,
    input wire [16*32-1:0] s_data,
    output wire m_valid,
    output wire [$clog2(64):0] m_chan,
    output wire m_last,
    output wire [$clog2(1):0] m_col,
    output wire [$clog2(1):0] m_row,
    output wire [4*32-1:0] m_data
);
reset_release u1 (.ninit_done(ninit_done));
wire ninit_done, gated_reset;
assign gated_reset = ninit_done && reset;

dx120p u0 (
    .clk(clk),
    .reset(gated_reset),
    .s_row(s_row),
    .s_col(s_col),
    .s_data(s_data),
    .s_valid(s_valid),
    .s_chan(s_chan),
    .s_last(s_last),
    .m_row(m_row),
    .m_col(m_col),
    .m_data(m_data),
    .m_valid(m_valid),
    .m_chan(m_chan),
    .m_last(m_last)
);
endmodule
