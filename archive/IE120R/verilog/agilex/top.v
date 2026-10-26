// dummy wrapper
module top (
    input wire clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(896):0] s_col,
    input wire [$clog2(896):0] s_row,
    input wire [3*32-1:0] s_data,
    output wire m_valid,
    output wire [$clog2(64):0] m_chan,
    output wire m_last,
    output wire [$clog2(7):0] m_col,
    output wire [$clog2(7):0] m_row,
    output wire [8*32-1:0] m_data
);
reset_release u1 (.ninit_done(ninit_done));
wire ninit_done, gated_reset;
assign gated_reset = ninit_done && reset;

ie120r u0 (
    .clk(clk),
    .reset(gated_reset),
    .s_row(s_row),
    .s_col(s_col),
    .s_data(s_data),
    .s_valid(s_valid),
    .m_row(m_row),
    .m_col(m_col),
    .m_data(m_data),
    .m_valid(m_valid),
    .m_chan(m_chan),
    .m_last(m_last)
);
endmodule
