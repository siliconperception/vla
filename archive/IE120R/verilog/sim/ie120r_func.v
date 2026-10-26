// Copyright (c) 2024 Silicon Perception Inc (www.siliconperception.com)
// 
// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:
// 
// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.
// 
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.


// layer    1 nstrip    4 ocmux    1 m_clk  250000000 req     4592 avail     5000 util   0.9184 nalu     64 wmem     13824 smem    604800 oshape [448, 448, 16]
// layer    2 nstrip   16 ocmux    1 m_clk  250000000 req     4760 avail     5000 util   0.9520 nalu    256 wmem     73728 smem   1720320 oshape [448, 448, 16]
// layer    3 nstrip   16 ocmux    1 m_clk  250000000 req     4760 avail     5000 util   0.9520 nalu    256 wmem     73728 smem   1720320 oshape [448, 448, 16]
// layer    4 nstrip   16 ocmux    4 m_clk  250000000 req     9520 avail    10000 util   0.9520 nalu    128 wmem    147456 smem   1662976 oshape [224, 224, 32]
// layer    5 nstrip   14 ocmux    2 m_clk  250000000 req     9984 avail    10000 util   0.9984 nalu    224 wmem    294912 smem   1806336 oshape [224, 224, 32]
// layer    6 nstrip   14 ocmux    2 m_clk  250000000 req     9984 avail    10000 util   0.9984 nalu    224 wmem    294912 smem   1806336 oshape [224, 224, 32]
// layer    7 nstrip   14 ocmux    8 m_clk  250000000 req    19968 avail    20000 util   0.9984 nalu    168 wmem    884736 smem   1705984 oshape [112, 112, 96]
// layer    8 nstrip    6 ocmux    1 m_clk  250000000 req    16720 avail    20000 util   0.8360 nalu    576 wmem   2654208 smem   2709504 oshape [112, 112, 96]
// layer    9 nstrip    6 ocmux    1 m_clk  250000000 req    16720 avail    20000 util   0.8360 nalu    576 wmem   2654208 smem   2709504 oshape [112, 112, 96]
// layer   10 nstrip    6 ocmux    4 m_clk  250000000 req    35200 avail    40000 util   0.8800 nalu    144 wmem   2654208 smem   2709504 oshape [56, 56, 96]
// layer   11 nstrip    3 ocmux    2 m_clk  250000000 req    33326 avail    40000 util   0.8331 nalu    144 wmem   2654208 smem   1354752 oshape [56, 56, 96]
// layer   12 nstrip    3 ocmux    2 m_clk  250000000 req    33326 avail    40000 util   0.8331 nalu    144 wmem   2654208 smem   1354752 oshape [56, 56, 96]
// layer   13 nstrip    3 ocmux    8 m_clk  250000000 req    70160 avail    80000 util   0.8770 nalu     72 wmem   5308416 smem   1354752 oshape [28, 28, 192]
// layer   14 nstrip    2 ocmux    2 m_clk  250000000 req    48720 avail    80000 util   0.6090 nalu    192 wmem  10616832 smem   1376256 oshape [28, 28, 192]
// layer   15 nstrip    2 ocmux    2 m_clk  250000000 req    48720 avail    80000 util   0.6090 nalu    192 wmem  10616832 smem   1376256 oshape [28, 28, 192]
// layer   16 nstrip    2 ocmux    8 m_clk  250000000 req    97440 avail   160000 util   0.6090 nalu     80 wmem  17694720 smem   1290240 oshape [14, 14, 320]
// layer   17 nstrip    1 ocmux    2 m_clk  250000000 req    80948 avail   160000 util   0.5059 nalu    160 wmem  29491200 smem   1146880 oshape [14, 14, 320]
// layer   18 nstrip    1 ocmux    2 m_clk  250000000 req    80948 avail   160000 util   0.5059 nalu    160 wmem  29491200 smem   1146880 oshape [14, 14, 320]
// layer   19 nstrip    1 ocmux    8 m_clk  250000000 req   161896 avail   320000 util   0.5059 nalu     64 wmem  47185920 smem   1075200 oshape [7, 7, 512]
// layer   20 nstrip    1 ocmux    8 m_clk  250000000 req   258664 avail   320000 util   0.8083 nalu     64 wmem  75497472 smem   1032192 oshape [7, 7, 512]
// layer   21 nstrip    1 ocmux    8 m_clk  250000000 req   258664 avail   320000 util   0.8083 nalu     64 wmem  75497472 smem   1032192 oshape [7, 7, 512]
// layer   22 nstrip    1 ocmux   64 m_clk  250000000 req   234304 avail   320000 util   0.7322 nalu      8 wmem   8388608 smem    737280 oshape [7, 7, 512]

// nalu   3960
// wmem 324843008
// smem 33433216

// op    0 nstrip    4 sdepth   1575 swidth     96 wdepth     27 wwidth    512 bwidth    512
// op    1 nstrip   16 sdepth    210 swidth    512 wdepth    144 wwidth    512 bwidth    512
// op    2 nstrip   16 sdepth    210 swidth    512 wdepth    144 wwidth    512 bwidth    512
// op    3 nstrip   16 sdepth    203 swidth    512 wdepth    144 wwidth   1024 bwidth   1024
// op    4 nstrip   14 sdepth    504 swidth    256 wdepth    288 wwidth   1024 bwidth   1024
// op    5 nstrip   14 sdepth    252 swidth    512 wdepth    288 wwidth   1024 bwidth   1024
// op    6 nstrip   14 sdepth    238 swidth    512 wdepth    288 wwidth   3072 bwidth   3072
// op    7 nstrip    6 sdepth   1176 swidth    384 wdepth    864 wwidth   3072 bwidth   3072
// op    8 nstrip    6 sdepth    147 swidth   3072 wdepth    864 wwidth   3072 bwidth   3072
// op    9 nstrip    6 sdepth    147 swidth   3072 wdepth    864 wwidth   3072 bwidth   3072
// op   10 nstrip    3 sdepth    588 swidth    768 wdepth    864 wwidth   3072 bwidth   3072
// op   11 nstrip    3 sdepth    294 swidth   1536 wdepth    864 wwidth   3072 bwidth   3072
// op   12 nstrip    3 sdepth    294 swidth   1536 wdepth    864 wwidth   6144 bwidth   6144
// op   13 nstrip    2 sdepth    896 swidth    768 wdepth   1728 wwidth   6144 bwidth   6144
// op   14 nstrip    2 sdepth    224 swidth   3072 wdepth   1728 wwidth   6144 bwidth   6144
// op   15 nstrip    2 sdepth    210 swidth   3072 wdepth   1728 wwidth  10240 bwidth  10240
// op   16 nstrip    1 sdepth    896 swidth   1280 wdepth   2880 wwidth  10240 bwidth  10240
// op   17 nstrip    1 sdepth    224 swidth   5120 wdepth   2880 wwidth  10240 bwidth  10240
// op   18 nstrip    1 sdepth    210 swidth   5120 wdepth   2880 wwidth  16384 bwidth  16384
// op   19 nstrip    1 sdepth    504 swidth   2048 wdepth   4608 wwidth  16384 bwidth  16384
// op   20 nstrip    1 sdepth    504 swidth   2048 wdepth   4608 wwidth  16384 bwidth  16384
// op   21 nstrip    1 sdepth    360 swidth   2048 wdepth    512 wwidth  16384 bwidth  16384

// ninst     16 sdepth    203 swidth    512
// ninst     32 sdepth    210 swidth    512
// ninst     14 sdepth    238 swidth    512
// ninst     14 sdepth    504 swidth    256
// ninst     14 sdepth    252 swidth    512
// ninst      4 sdepth   1575 swidth     96
// ninst      6 sdepth   1176 swidth    384
// ninst     12 sdepth    147 swidth   3072
// ninst      3 sdepth    588 swidth    768
// ninst      6 sdepth    294 swidth   1536
// ninst      2 sdepth    210 swidth   3072
// ninst      2 sdepth    896 swidth    768
// ninst      2 sdepth    224 swidth   3072
// ninst      1 sdepth    360 swidth   2048
// ninst      2 sdepth    504 swidth   2048
// ninst      1 sdepth    210 swidth   5120
// ninst      1 sdepth    896 swidth   1280
// ninst      1 sdepth    224 swidth   5120

// ninst      1 wdepth     27 wwidth    512
// ninst      2 wdepth    144 wwidth    512
// ninst      1 wdepth    144 wwidth   1024
// ninst      2 wdepth    288 wwidth   1024
// ninst      1 wdepth    288 wwidth   3072
// ninst      5 wdepth    864 wwidth   3072
// ninst      1 wdepth    864 wwidth   6144
// ninst      1 wdepth    512 wwidth  16384
// ninst      2 wdepth   1728 wwidth   6144
// ninst      1 wdepth   1728 wwidth  10240
// ninst      2 wdepth   2880 wwidth  10240
// ninst      1 wdepth   2880 wwidth  16384
// ninst      2 wdepth   4608 wwidth  16384

module ie120r (
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

wire [$clog2(1):0] s_chan;
wire s_last;
assign s_chan='b0;
assign s_last=s_valid;


wire op0_valid;
wire [$clog2(1):0] op0_chan;
wire op0_last;
wire [$clog2(448):0] op0_col;
wire [$clog2(448):0] op0_row;
wire [16*32-1:0] op0_data;
LAYER1 layer1 (
.reset(reset),
.s_clk(clk),
.s_valid(s_valid),
.s_chan(s_chan),
.s_last(s_last),
.s_col(s_col),
.s_row(s_row),
.s_data(s_data),
.m_clk(clk),
.m_valid(op0_valid),
.m_chan(op0_chan),
.m_last(op0_last),
.m_col(op0_col),
.m_row(op0_row),
.m_data(op0_data)
);

wire op1_valid;
wire [$clog2(1):0] op1_chan;
wire op1_last;
wire [$clog2(448):0] op1_col;
wire [$clog2(448):0] op1_row;
wire [16*32-1:0] op1_data;
LAYER2 layer2 (
.reset(reset),
.s_clk(clk),
.s_valid(op0_valid),
.s_chan(op0_chan),
.s_last(op0_last),
.s_col(op0_col),
.s_row(op0_row),
.s_data(op0_data),
.m_clk(clk),
.m_valid(op1_valid),
.m_chan(op1_chan),
.m_last(op1_last),
.m_col(op1_col),
.m_row(op1_row),
.m_data(op1_data)
);

wire op2_valid;
wire [$clog2(1):0] op2_chan;
wire op2_last;
wire [$clog2(448):0] op2_col;
wire [$clog2(448):0] op2_row;
wire [16*32-1:0] op2_data;
LAYER3 layer3 (
.reset(reset),
.s_clk(clk),
.s_valid(op1_valid),
.s_chan(op1_chan),
.s_last(op1_last),
.s_col(op1_col),
.s_row(op1_row),
.s_data(op1_data),
.m_clk(clk),
.m_valid(op2_valid),
.m_chan(op2_chan),
.m_last(op2_last),
.m_col(op2_col),
.m_row(op2_row),
.m_data(op2_data)
);

wire op3_valid;
wire [$clog2(4):0] op3_chan;
wire op3_last;
wire [$clog2(224):0] op3_col;
wire [$clog2(224):0] op3_row;
wire [8*32-1:0] op3_data;
LAYER4 layer4 (
.reset(reset),
.s_clk(clk),
.s_valid(op2_valid),
.s_chan(op2_chan),
.s_last(op2_last),
.s_col(op2_col),
.s_row(op2_row),
.s_data(op2_data),
.m_clk(clk),
.m_valid(op3_valid),
.m_chan(op3_chan),
.m_last(op3_last),
.m_col(op3_col),
.m_row(op3_row),
.m_data(op3_data)
);

wire op4_valid;
wire [$clog2(2):0] op4_chan;
wire op4_last;
wire [$clog2(224):0] op4_col;
wire [$clog2(224):0] op4_row;
wire [16*32-1:0] op4_data;
LAYER5 layer5 (
.reset(reset),
.s_clk(clk),
.s_valid(op3_valid),
.s_chan(op3_chan),
.s_last(op3_last),
.s_col(op3_col),
.s_row(op3_row),
.s_data(op3_data),
.m_clk(clk),
.m_valid(op4_valid),
.m_chan(op4_chan),
.m_last(op4_last),
.m_col(op4_col),
.m_row(op4_row),
.m_data(op4_data)
);

wire op5_valid;
wire [$clog2(2):0] op5_chan;
wire op5_last;
wire [$clog2(224):0] op5_col;
wire [$clog2(224):0] op5_row;
wire [16*32-1:0] op5_data;
LAYER6 layer6 (
.reset(reset),
.s_clk(clk),
.s_valid(op4_valid),
.s_chan(op4_chan),
.s_last(op4_last),
.s_col(op4_col),
.s_row(op4_row),
.s_data(op4_data),
.m_clk(clk),
.m_valid(op5_valid),
.m_chan(op5_chan),
.m_last(op5_last),
.m_col(op5_col),
.m_row(op5_row),
.m_data(op5_data)
);

wire op6_valid;
wire [$clog2(8):0] op6_chan;
wire op6_last;
wire [$clog2(112):0] op6_col;
wire [$clog2(112):0] op6_row;
wire [12*32-1:0] op6_data;
LAYER7 layer7 (
.reset(reset),
.s_clk(clk),
.s_valid(op5_valid),
.s_chan(op5_chan),
.s_last(op5_last),
.s_col(op5_col),
.s_row(op5_row),
.s_data(op5_data),
.m_clk(clk),
.m_valid(op6_valid),
.m_chan(op6_chan),
.m_last(op6_last),
.m_col(op6_col),
.m_row(op6_row),
.m_data(op6_data)
);

wire op7_valid;
wire [$clog2(1):0] op7_chan;
wire op7_last;
wire [$clog2(112):0] op7_col;
wire [$clog2(112):0] op7_row;
wire [96*32-1:0] op7_data;
LAYER8 layer8 (
.reset(reset),
.s_clk(clk),
.s_valid(op6_valid),
.s_chan(op6_chan),
.s_last(op6_last),
.s_col(op6_col),
.s_row(op6_row),
.s_data(op6_data),
.m_clk(clk),
.m_valid(op7_valid),
.m_chan(op7_chan),
.m_last(op7_last),
.m_col(op7_col),
.m_row(op7_row),
.m_data(op7_data)
);

wire op8_valid;
wire [$clog2(1):0] op8_chan;
wire op8_last;
wire [$clog2(112):0] op8_col;
wire [$clog2(112):0] op8_row;
wire [96*32-1:0] op8_data;
LAYER9 layer9 (
.reset(reset),
.s_clk(clk),
.s_valid(op7_valid),
.s_chan(op7_chan),
.s_last(op7_last),
.s_col(op7_col),
.s_row(op7_row),
.s_data(op7_data),
.m_clk(clk),
.m_valid(op8_valid),
.m_chan(op8_chan),
.m_last(op8_last),
.m_col(op8_col),
.m_row(op8_row),
.m_data(op8_data)
);

wire op9_valid;
wire [$clog2(4):0] op9_chan;
wire op9_last;
wire [$clog2(56):0] op9_col;
wire [$clog2(56):0] op9_row;
wire [24*32-1:0] op9_data;
LAYER10 layer10 (
.reset(reset),
.s_clk(clk),
.s_valid(op8_valid),
.s_chan(op8_chan),
.s_last(op8_last),
.s_col(op8_col),
.s_row(op8_row),
.s_data(op8_data),
.m_clk(clk),
.m_valid(op9_valid),
.m_chan(op9_chan),
.m_last(op9_last),
.m_col(op9_col),
.m_row(op9_row),
.m_data(op9_data)
);

wire op10_valid;
wire [$clog2(2):0] op10_chan;
wire op10_last;
wire [$clog2(56):0] op10_col;
wire [$clog2(56):0] op10_row;
wire [48*32-1:0] op10_data;
LAYER11 layer11 (
.reset(reset),
.s_clk(clk),
.s_valid(op9_valid),
.s_chan(op9_chan),
.s_last(op9_last),
.s_col(op9_col),
.s_row(op9_row),
.s_data(op9_data),
.m_clk(clk),
.m_valid(op10_valid),
.m_chan(op10_chan),
.m_last(op10_last),
.m_col(op10_col),
.m_row(op10_row),
.m_data(op10_data)
);

wire op11_valid;
wire [$clog2(2):0] op11_chan;
wire op11_last;
wire [$clog2(56):0] op11_col;
wire [$clog2(56):0] op11_row;
wire [48*32-1:0] op11_data;
LAYER12 layer12 (
.reset(reset),
.s_clk(clk),
.s_valid(op10_valid),
.s_chan(op10_chan),
.s_last(op10_last),
.s_col(op10_col),
.s_row(op10_row),
.s_data(op10_data),
.m_clk(clk),
.m_valid(op11_valid),
.m_chan(op11_chan),
.m_last(op11_last),
.m_col(op11_col),
.m_row(op11_row),
.m_data(op11_data)
);

wire op12_valid;
wire [$clog2(8):0] op12_chan;
wire op12_last;
wire [$clog2(28):0] op12_col;
wire [$clog2(28):0] op12_row;
wire [24*32-1:0] op12_data;
LAYER13 layer13 (
.reset(reset),
.s_clk(clk),
.s_valid(op11_valid),
.s_chan(op11_chan),
.s_last(op11_last),
.s_col(op11_col),
.s_row(op11_row),
.s_data(op11_data),
.m_clk(clk),
.m_valid(op12_valid),
.m_chan(op12_chan),
.m_last(op12_last),
.m_col(op12_col),
.m_row(op12_row),
.m_data(op12_data)
);

wire op13_valid;
wire [$clog2(2):0] op13_chan;
wire op13_last;
wire [$clog2(28):0] op13_col;
wire [$clog2(28):0] op13_row;
wire [96*32-1:0] op13_data;
LAYER14 layer14 (
.reset(reset),
.s_clk(clk),
.s_valid(op12_valid),
.s_chan(op12_chan),
.s_last(op12_last),
.s_col(op12_col),
.s_row(op12_row),
.s_data(op12_data),
.m_clk(clk),
.m_valid(op13_valid),
.m_chan(op13_chan),
.m_last(op13_last),
.m_col(op13_col),
.m_row(op13_row),
.m_data(op13_data)
);

wire op14_valid;
wire [$clog2(2):0] op14_chan;
wire op14_last;
wire [$clog2(28):0] op14_col;
wire [$clog2(28):0] op14_row;
wire [96*32-1:0] op14_data;
LAYER15 layer15 (
.reset(reset),
.s_clk(clk),
.s_valid(op13_valid),
.s_chan(op13_chan),
.s_last(op13_last),
.s_col(op13_col),
.s_row(op13_row),
.s_data(op13_data),
.m_clk(clk),
.m_valid(op14_valid),
.m_chan(op14_chan),
.m_last(op14_last),
.m_col(op14_col),
.m_row(op14_row),
.m_data(op14_data)
);

wire op15_valid;
wire [$clog2(8):0] op15_chan;
wire op15_last;
wire [$clog2(14):0] op15_col;
wire [$clog2(14):0] op15_row;
wire [40*32-1:0] op15_data;
LAYER16 layer16 (
.reset(reset),
.s_clk(clk),
.s_valid(op14_valid),
.s_chan(op14_chan),
.s_last(op14_last),
.s_col(op14_col),
.s_row(op14_row),
.s_data(op14_data),
.m_clk(clk),
.m_valid(op15_valid),
.m_chan(op15_chan),
.m_last(op15_last),
.m_col(op15_col),
.m_row(op15_row),
.m_data(op15_data)
);

wire op16_valid;
wire [$clog2(2):0] op16_chan;
wire op16_last;
wire [$clog2(14):0] op16_col;
wire [$clog2(14):0] op16_row;
wire [160*32-1:0] op16_data;
LAYER17 layer17 (
.reset(reset),
.s_clk(clk),
.s_valid(op15_valid),
.s_chan(op15_chan),
.s_last(op15_last),
.s_col(op15_col),
.s_row(op15_row),
.s_data(op15_data),
.m_clk(clk),
.m_valid(op16_valid),
.m_chan(op16_chan),
.m_last(op16_last),
.m_col(op16_col),
.m_row(op16_row),
.m_data(op16_data)
);

wire op17_valid;
wire [$clog2(2):0] op17_chan;
wire op17_last;
wire [$clog2(14):0] op17_col;
wire [$clog2(14):0] op17_row;
wire [160*32-1:0] op17_data;
LAYER18 layer18 (
.reset(reset),
.s_clk(clk),
.s_valid(op16_valid),
.s_chan(op16_chan),
.s_last(op16_last),
.s_col(op16_col),
.s_row(op16_row),
.s_data(op16_data),
.m_clk(clk),
.m_valid(op17_valid),
.m_chan(op17_chan),
.m_last(op17_last),
.m_col(op17_col),
.m_row(op17_row),
.m_data(op17_data)
);

wire op18_valid;
wire [$clog2(8):0] op18_chan;
wire op18_last;
wire [$clog2(7):0] op18_col;
wire [$clog2(7):0] op18_row;
wire [64*32-1:0] op18_data;
LAYER19 layer19 (
.reset(reset),
.s_clk(clk),
.s_valid(op17_valid),
.s_chan(op17_chan),
.s_last(op17_last),
.s_col(op17_col),
.s_row(op17_row),
.s_data(op17_data),
.m_clk(clk),
.m_valid(op18_valid),
.m_chan(op18_chan),
.m_last(op18_last),
.m_col(op18_col),
.m_row(op18_row),
.m_data(op18_data)
);

wire op19_valid;
wire [$clog2(8):0] op19_chan;
wire op19_last;
wire [$clog2(7):0] op19_col;
wire [$clog2(7):0] op19_row;
wire [64*32-1:0] op19_data;
LAYER20 layer20 (
.reset(reset),
.s_clk(clk),
.s_valid(op18_valid),
.s_chan(op18_chan),
.s_last(op18_last),
.s_col(op18_col),
.s_row(op18_row),
.s_data(op18_data),
.m_clk(clk),
.m_valid(op19_valid),
.m_chan(op19_chan),
.m_last(op19_last),
.m_col(op19_col),
.m_row(op19_row),
.m_data(op19_data)
);

wire op20_valid;
wire [$clog2(8):0] op20_chan;
wire op20_last;
wire [$clog2(7):0] op20_col;
wire [$clog2(7):0] op20_row;
wire [64*32-1:0] op20_data;
LAYER21 layer21 (
.reset(reset),
.s_clk(clk),
.s_valid(op19_valid),
.s_chan(op19_chan),
.s_last(op19_last),
.s_col(op19_col),
.s_row(op19_row),
.s_data(op19_data),
.m_clk(clk),
.m_valid(op20_valid),
.m_chan(op20_chan),
.m_last(op20_last),
.m_col(op20_col),
.m_row(op20_row),
.m_data(op20_data)
);

wire op21_valid;
wire [$clog2(64):0] op21_chan;
wire op21_last;
wire [$clog2(7):0] op21_col;
wire [$clog2(7):0] op21_row;
wire [8*32-1:0] op21_data;
LAYER22 layer22 (
.reset(reset),
.s_clk(clk),
.s_valid(op20_valid),
.s_chan(op20_chan),
.s_last(op20_last),
.s_col(op20_col),
.s_row(op20_row),
.s_data(op20_data),
.m_clk(clk),
.m_valid(op21_valid),
.m_chan(op21_chan),
.m_last(op21_last),
.m_col(op21_col),
.m_row(op21_row),
.m_data(op21_data)
);

assign m_valid=op21_valid;
assign m_chan=op21_chan;
assign m_last=op21_last;
assign m_col=op21_col;
assign m_row=op21_row;
assign m_data=op21_data;

endmodule

module LAYER1 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(1):0] s_chan,
    input wire s_last,
    input wire [$clog2(896):0] s_col,
    input wire [$clog2(896):0] s_row,
    input wire [3*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(1):0] m_chan,
    output reg m_last,
    output reg [$clog2(448):0] m_col,
    output reg [$clog2(448):0] m_row,
    output reg [16*32-1:0] m_data
);

parameter OCMUX=1,OCHAN=16,OWIDTH=448,TDMPAD=     408;

reg [$clog2(1575):0] strip_wa [4-1:0];
reg strip_wen [4-1:0];
reg signed [$clog2(1575)+1:0] strip_ra [4-1:0];
reg signed [$clog2(27)+1:0] weight_ra;
reg [4-1:0] strip_zpad;
reg [4-1:0] strip_zpad_q;
reg signed [$clog2(3)+1:0] ic;
reg [$clog2(3):0] ic_q,ic_qq;
reg [$clog2(1):0] ochan_sel;
reg [$clog2(4):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(1):0] s_chan_q;
reg [$clog2(896):0] s_col_q;
reg [$clog2(896):0] s_row_q;
reg [3*32-1:0] s_data_q;
reg [3*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(224+1)*1+(s_col_q-(0*224-1))*1+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*224) && (s_col_q < (0+1)*224+1-1);
    strip_wa[1] <= (s_row_q%7)*(224+1)*1+(s_col_q-(1*224-1))*1+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*224-1) && (s_col_q < (1+1)*224+1-1);
    strip_wa[2] <= (s_row_q%7)*(224+1)*1+(s_col_q-(2*224-1))*1+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*224-1) && (s_col_q < (2+1)*224+1-1);
    strip_wa[3] <= (s_row_q%7)*(224+1)*1+(s_col_q-(3*224-1))*1+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*224-1) && (s_col_q < (3+1)*224+1-1);
end
wire [3*32-1:0] strip_rd [4-1:0];
reg [32-1:0] patch [4-1:0];
generate
for (i=0; i<4; i=i+1) begin : STRIP
STRIP #(1575,96) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(1575):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(3):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/1)*32 +:32];
    end
end
endgenerate

wire [32*16-1:0] weight_rd;
wire [32*16-1:0] bias_rd;

WEIGHT1 weight (.clk(m_clk),.ra(weight_ra[$clog2(27):0]),.rd(weight_rd));
BIAS1 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*1+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [16*32-1:0] feat [4-1:0];
generate
for (i=0; i<4; i=i+1) begin : ALU_NS
    for (j=0; j<16; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(896):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==896-1) begin
            icount <= 'd0;
            if ((s_row_q >= 1) && ((s_row_q%2) == (3%2)))
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(448)+1:0] ocol;
reg signed [$clog2(448)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0));
strip_ra[0] <= ((ky+(orow*2))%7)*(224+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0));
strip_ra[1] <= ((ky+(orow*2))%7)*(224+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0));
strip_ra[2] <= ((ky+(orow*2))%7)*(224+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0));
strip_ra[3] <= ((ky+(orow*2))%7)*(224+1)*1+kx*1+ocol*2*1+(ic%1)+1;
weight_ra <= (ky+1)*3*3+(kx+1)*3+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==2) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<4) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*112+ocol < 448) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*112+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==1-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==1-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==112-1) begin
                        ocol <= 'd0;
                        if (orow==448-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           m_row_ack <= 1'b1;
           if (~m_row_req) begin
               m_row_ack <= 1'b0;
               m_state<= 'd0;
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS1 (
    input wire clk,
    output reg [16*32-1:0] rd
);
reg [16*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT1 (
    input wire clk,
    input wire [$clog2(27):0] ra,
    output reg [16*32-1:0] rd
);
reg [16*32-1:0] spram [0:27-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER2 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(1):0] s_chan,
    input wire s_last,
    input wire [$clog2(448):0] s_col,
    input wire [$clog2(448):0] s_row,
    input wire [16*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(1):0] m_chan,
    output reg m_last,
    output reg [$clog2(448):0] m_col,
    output reg [$clog2(448):0] m_row,
    output reg [16*32-1:0] m_data
);

parameter OCMUX=1,OCHAN=16,OWIDTH=448,TDMPAD=     240;

reg [$clog2(210):0] strip_wa [16-1:0];
reg strip_wen [16-1:0];
reg signed [$clog2(210)+1:0] strip_ra [16-1:0];
reg signed [$clog2(144)+1:0] weight_ra;
reg [16-1:0] strip_zpad;
reg [16-1:0] strip_zpad_q;
reg signed [$clog2(16)+1:0] ic;
reg [$clog2(16):0] ic_q,ic_qq;
reg [$clog2(1):0] ochan_sel;
reg [$clog2(16):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(1):0] s_chan_q;
reg [$clog2(448):0] s_col_q;
reg [$clog2(448):0] s_row_q;
reg [16*32-1:0] s_data_q;
reg [16*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(28+2)*1+(s_col_q-(0*28-1))*1+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*28) && (s_col_q < (0+1)*28+2-1);
    strip_wa[1] <= (s_row_q%7)*(28+2)*1+(s_col_q-(1*28-1))*1+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*28-1) && (s_col_q < (1+1)*28+2-1);
    strip_wa[2] <= (s_row_q%7)*(28+2)*1+(s_col_q-(2*28-1))*1+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*28-1) && (s_col_q < (2+1)*28+2-1);
    strip_wa[3] <= (s_row_q%7)*(28+2)*1+(s_col_q-(3*28-1))*1+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*28-1) && (s_col_q < (3+1)*28+2-1);
    strip_wa[4] <= (s_row_q%7)*(28+2)*1+(s_col_q-(4*28-1))*1+s_chan_q;
    strip_wen[4] <= s_valid_q && (s_col_q >= 4*28-1) && (s_col_q < (4+1)*28+2-1);
    strip_wa[5] <= (s_row_q%7)*(28+2)*1+(s_col_q-(5*28-1))*1+s_chan_q;
    strip_wen[5] <= s_valid_q && (s_col_q >= 5*28-1) && (s_col_q < (5+1)*28+2-1);
    strip_wa[6] <= (s_row_q%7)*(28+2)*1+(s_col_q-(6*28-1))*1+s_chan_q;
    strip_wen[6] <= s_valid_q && (s_col_q >= 6*28-1) && (s_col_q < (6+1)*28+2-1);
    strip_wa[7] <= (s_row_q%7)*(28+2)*1+(s_col_q-(7*28-1))*1+s_chan_q;
    strip_wen[7] <= s_valid_q && (s_col_q >= 7*28-1) && (s_col_q < (7+1)*28+2-1);
    strip_wa[8] <= (s_row_q%7)*(28+2)*1+(s_col_q-(8*28-1))*1+s_chan_q;
    strip_wen[8] <= s_valid_q && (s_col_q >= 8*28-1) && (s_col_q < (8+1)*28+2-1);
    strip_wa[9] <= (s_row_q%7)*(28+2)*1+(s_col_q-(9*28-1))*1+s_chan_q;
    strip_wen[9] <= s_valid_q && (s_col_q >= 9*28-1) && (s_col_q < (9+1)*28+2-1);
    strip_wa[10] <= (s_row_q%7)*(28+2)*1+(s_col_q-(10*28-1))*1+s_chan_q;
    strip_wen[10] <= s_valid_q && (s_col_q >= 10*28-1) && (s_col_q < (10+1)*28+2-1);
    strip_wa[11] <= (s_row_q%7)*(28+2)*1+(s_col_q-(11*28-1))*1+s_chan_q;
    strip_wen[11] <= s_valid_q && (s_col_q >= 11*28-1) && (s_col_q < (11+1)*28+2-1);
    strip_wa[12] <= (s_row_q%7)*(28+2)*1+(s_col_q-(12*28-1))*1+s_chan_q;
    strip_wen[12] <= s_valid_q && (s_col_q >= 12*28-1) && (s_col_q < (12+1)*28+2-1);
    strip_wa[13] <= (s_row_q%7)*(28+2)*1+(s_col_q-(13*28-1))*1+s_chan_q;
    strip_wen[13] <= s_valid_q && (s_col_q >= 13*28-1) && (s_col_q < (13+1)*28+2-1);
    strip_wa[14] <= (s_row_q%7)*(28+2)*1+(s_col_q-(14*28-1))*1+s_chan_q;
    strip_wen[14] <= s_valid_q && (s_col_q >= 14*28-1) && (s_col_q < (14+1)*28+2-1);
    strip_wa[15] <= (s_row_q%7)*(28+2)*1+(s_col_q-(15*28-1))*1+s_chan_q;
    strip_wen[15] <= s_valid_q && (s_col_q >= 15*28-1) && (s_col_q < (15+1)*28+2-1);
end
wire [16*32-1:0] strip_rd [16-1:0];
reg [32-1:0] patch [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : STRIP
STRIP #(210,512) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(210):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(16):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/1)*32 +:32];
    end
end
endgenerate

wire [32*16-1:0] weight_rd;
wire [32*16-1:0] bias_rd;

WEIGHT2 weight (.clk(m_clk),.ra(weight_ra[$clog2(144):0]),.rd(weight_rd));
BIAS2 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*1+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [16*32-1:0] feat [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : ALU_NS
    for (j=0; j<16; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(448):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==448-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(448)+1:0] ocol;
reg signed [$clog2(448)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==447)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[2] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[3] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[4] <= strip_zpad[4];
strip_zpad[4] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[4] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[5] <= strip_zpad[5];
strip_zpad[5] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[5] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[6] <= strip_zpad[6];
strip_zpad[6] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[6] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[7] <= strip_zpad[7];
strip_zpad[7] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[7] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[8] <= strip_zpad[8];
strip_zpad[8] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[8] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[9] <= strip_zpad[9];
strip_zpad[9] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[9] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[10] <= strip_zpad[10];
strip_zpad[10] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[10] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[11] <= strip_zpad[11];
strip_zpad[11] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[11] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[12] <= strip_zpad[12];
strip_zpad[12] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[12] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[13] <= strip_zpad[13];
strip_zpad[13] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[13] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[14] <= strip_zpad[14];
strip_zpad[14] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[14] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[15] <= strip_zpad[15];
strip_zpad[15] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0)) || ((ocol==27)&&(kx>0));
strip_ra[15] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
weight_ra <= (ky+1)*3*16+(kx+1)*16+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==15) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<16) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*28+ocol < 448) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*28+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==1-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==1-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==28-1) begin
                        ocol <= 'd0;
                        if (orow==448-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==448-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS2 (
    input wire clk,
    output reg [16*32-1:0] rd
);
reg [16*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT2 (
    input wire clk,
    input wire [$clog2(144):0] ra,
    output reg [16*32-1:0] rd
);
reg [16*32-1:0] spram [0:144-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER3 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(1):0] s_chan,
    input wire s_last,
    input wire [$clog2(448):0] s_col,
    input wire [$clog2(448):0] s_row,
    input wire [16*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(1):0] m_chan,
    output reg m_last,
    output reg [$clog2(448):0] m_col,
    output reg [$clog2(448):0] m_row,
    output reg [16*32-1:0] m_data
);

parameter OCMUX=1,OCHAN=16,OWIDTH=448,TDMPAD=     240;

reg [$clog2(210):0] strip_wa [16-1:0];
reg strip_wen [16-1:0];
reg signed [$clog2(210)+1:0] strip_ra [16-1:0];
reg signed [$clog2(144)+1:0] weight_ra;
reg [16-1:0] strip_zpad;
reg [16-1:0] strip_zpad_q;
reg signed [$clog2(16)+1:0] ic;
reg [$clog2(16):0] ic_q,ic_qq;
reg [$clog2(1):0] ochan_sel;
reg [$clog2(16):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(1):0] s_chan_q;
reg [$clog2(448):0] s_col_q;
reg [$clog2(448):0] s_row_q;
reg [16*32-1:0] s_data_q;
reg [16*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(28+2)*1+(s_col_q-(0*28-1))*1+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*28) && (s_col_q < (0+1)*28+2-1);
    strip_wa[1] <= (s_row_q%7)*(28+2)*1+(s_col_q-(1*28-1))*1+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*28-1) && (s_col_q < (1+1)*28+2-1);
    strip_wa[2] <= (s_row_q%7)*(28+2)*1+(s_col_q-(2*28-1))*1+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*28-1) && (s_col_q < (2+1)*28+2-1);
    strip_wa[3] <= (s_row_q%7)*(28+2)*1+(s_col_q-(3*28-1))*1+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*28-1) && (s_col_q < (3+1)*28+2-1);
    strip_wa[4] <= (s_row_q%7)*(28+2)*1+(s_col_q-(4*28-1))*1+s_chan_q;
    strip_wen[4] <= s_valid_q && (s_col_q >= 4*28-1) && (s_col_q < (4+1)*28+2-1);
    strip_wa[5] <= (s_row_q%7)*(28+2)*1+(s_col_q-(5*28-1))*1+s_chan_q;
    strip_wen[5] <= s_valid_q && (s_col_q >= 5*28-1) && (s_col_q < (5+1)*28+2-1);
    strip_wa[6] <= (s_row_q%7)*(28+2)*1+(s_col_q-(6*28-1))*1+s_chan_q;
    strip_wen[6] <= s_valid_q && (s_col_q >= 6*28-1) && (s_col_q < (6+1)*28+2-1);
    strip_wa[7] <= (s_row_q%7)*(28+2)*1+(s_col_q-(7*28-1))*1+s_chan_q;
    strip_wen[7] <= s_valid_q && (s_col_q >= 7*28-1) && (s_col_q < (7+1)*28+2-1);
    strip_wa[8] <= (s_row_q%7)*(28+2)*1+(s_col_q-(8*28-1))*1+s_chan_q;
    strip_wen[8] <= s_valid_q && (s_col_q >= 8*28-1) && (s_col_q < (8+1)*28+2-1);
    strip_wa[9] <= (s_row_q%7)*(28+2)*1+(s_col_q-(9*28-1))*1+s_chan_q;
    strip_wen[9] <= s_valid_q && (s_col_q >= 9*28-1) && (s_col_q < (9+1)*28+2-1);
    strip_wa[10] <= (s_row_q%7)*(28+2)*1+(s_col_q-(10*28-1))*1+s_chan_q;
    strip_wen[10] <= s_valid_q && (s_col_q >= 10*28-1) && (s_col_q < (10+1)*28+2-1);
    strip_wa[11] <= (s_row_q%7)*(28+2)*1+(s_col_q-(11*28-1))*1+s_chan_q;
    strip_wen[11] <= s_valid_q && (s_col_q >= 11*28-1) && (s_col_q < (11+1)*28+2-1);
    strip_wa[12] <= (s_row_q%7)*(28+2)*1+(s_col_q-(12*28-1))*1+s_chan_q;
    strip_wen[12] <= s_valid_q && (s_col_q >= 12*28-1) && (s_col_q < (12+1)*28+2-1);
    strip_wa[13] <= (s_row_q%7)*(28+2)*1+(s_col_q-(13*28-1))*1+s_chan_q;
    strip_wen[13] <= s_valid_q && (s_col_q >= 13*28-1) && (s_col_q < (13+1)*28+2-1);
    strip_wa[14] <= (s_row_q%7)*(28+2)*1+(s_col_q-(14*28-1))*1+s_chan_q;
    strip_wen[14] <= s_valid_q && (s_col_q >= 14*28-1) && (s_col_q < (14+1)*28+2-1);
    strip_wa[15] <= (s_row_q%7)*(28+2)*1+(s_col_q-(15*28-1))*1+s_chan_q;
    strip_wen[15] <= s_valid_q && (s_col_q >= 15*28-1) && (s_col_q < (15+1)*28+2-1);
end
wire [16*32-1:0] strip_rd [16-1:0];
reg [32-1:0] patch [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : STRIP
STRIP #(210,512) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(210):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(16):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/1)*32 +:32];
    end
end
endgenerate

wire [32*16-1:0] weight_rd;
wire [32*16-1:0] bias_rd;

WEIGHT3 weight (.clk(m_clk),.ra(weight_ra[$clog2(144):0]),.rd(weight_rd));
BIAS3 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*1+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [16*32-1:0] feat [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : ALU_NS
    for (j=0; j<16; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(448):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==448-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(448)+1:0] ocol;
reg signed [$clog2(448)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==447)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[2] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[3] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[4] <= strip_zpad[4];
strip_zpad[4] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[4] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[5] <= strip_zpad[5];
strip_zpad[5] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[5] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[6] <= strip_zpad[6];
strip_zpad[6] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[6] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[7] <= strip_zpad[7];
strip_zpad[7] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[7] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[8] <= strip_zpad[8];
strip_zpad[8] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[8] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[9] <= strip_zpad[9];
strip_zpad[9] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[9] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[10] <= strip_zpad[10];
strip_zpad[10] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[10] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[11] <= strip_zpad[11];
strip_zpad[11] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[11] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[12] <= strip_zpad[12];
strip_zpad[12] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[12] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[13] <= strip_zpad[13];
strip_zpad[13] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[13] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[14] <= strip_zpad[14];
strip_zpad[14] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0));
strip_ra[14] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[15] <= strip_zpad[15];
strip_zpad[15] <= ((orow==0)&&(ky<0)) || ((orow==447)&&(ky>0)) || ((ocol==27)&&(kx>0));
strip_ra[15] <= ((ky+(orow*1))%7)*(28+2)*1+kx*1+ocol*1*1+(ic%1)+1;
weight_ra <= (ky+1)*3*16+(kx+1)*16+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==15) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<16) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*28+ocol < 448) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*28+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==1-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==1-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==28-1) begin
                        ocol <= 'd0;
                        if (orow==448-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==448-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS3 (
    input wire clk,
    output reg [16*32-1:0] rd
);
reg [16*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT3 (
    input wire clk,
    input wire [$clog2(144):0] ra,
    output reg [16*32-1:0] rd
);
reg [16*32-1:0] spram [0:144-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER4 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(1):0] s_chan,
    input wire s_last,
    input wire [$clog2(448):0] s_col,
    input wire [$clog2(448):0] s_row,
    input wire [16*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(4):0] m_chan,
    output reg m_last,
    output reg [$clog2(224):0] m_col,
    output reg [$clog2(224):0] m_row,
    output reg [8*32-1:0] m_data
);

parameter OCMUX=4,OCHAN=32,OWIDTH=224,TDMPAD=     480;

reg [$clog2(203):0] strip_wa [16-1:0];
reg strip_wen [16-1:0];
reg signed [$clog2(203)+1:0] strip_ra [16-1:0];
reg signed [$clog2(144)+1:0] weight_ra;
reg [16-1:0] strip_zpad;
reg [16-1:0] strip_zpad_q;
reg signed [$clog2(16)+1:0] ic;
reg [$clog2(16):0] ic_q,ic_qq;
reg [$clog2(4):0] ochan_sel;
reg [$clog2(16):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(1):0] s_chan_q;
reg [$clog2(448):0] s_col_q;
reg [$clog2(448):0] s_row_q;
reg [16*32-1:0] s_data_q;
reg [16*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(28+1)*1+(s_col_q-(0*28-1))*1+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*28) && (s_col_q < (0+1)*28+1-1);
    strip_wa[1] <= (s_row_q%7)*(28+1)*1+(s_col_q-(1*28-1))*1+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*28-1) && (s_col_q < (1+1)*28+1-1);
    strip_wa[2] <= (s_row_q%7)*(28+1)*1+(s_col_q-(2*28-1))*1+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*28-1) && (s_col_q < (2+1)*28+1-1);
    strip_wa[3] <= (s_row_q%7)*(28+1)*1+(s_col_q-(3*28-1))*1+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*28-1) && (s_col_q < (3+1)*28+1-1);
    strip_wa[4] <= (s_row_q%7)*(28+1)*1+(s_col_q-(4*28-1))*1+s_chan_q;
    strip_wen[4] <= s_valid_q && (s_col_q >= 4*28-1) && (s_col_q < (4+1)*28+1-1);
    strip_wa[5] <= (s_row_q%7)*(28+1)*1+(s_col_q-(5*28-1))*1+s_chan_q;
    strip_wen[5] <= s_valid_q && (s_col_q >= 5*28-1) && (s_col_q < (5+1)*28+1-1);
    strip_wa[6] <= (s_row_q%7)*(28+1)*1+(s_col_q-(6*28-1))*1+s_chan_q;
    strip_wen[6] <= s_valid_q && (s_col_q >= 6*28-1) && (s_col_q < (6+1)*28+1-1);
    strip_wa[7] <= (s_row_q%7)*(28+1)*1+(s_col_q-(7*28-1))*1+s_chan_q;
    strip_wen[7] <= s_valid_q && (s_col_q >= 7*28-1) && (s_col_q < (7+1)*28+1-1);
    strip_wa[8] <= (s_row_q%7)*(28+1)*1+(s_col_q-(8*28-1))*1+s_chan_q;
    strip_wen[8] <= s_valid_q && (s_col_q >= 8*28-1) && (s_col_q < (8+1)*28+1-1);
    strip_wa[9] <= (s_row_q%7)*(28+1)*1+(s_col_q-(9*28-1))*1+s_chan_q;
    strip_wen[9] <= s_valid_q && (s_col_q >= 9*28-1) && (s_col_q < (9+1)*28+1-1);
    strip_wa[10] <= (s_row_q%7)*(28+1)*1+(s_col_q-(10*28-1))*1+s_chan_q;
    strip_wen[10] <= s_valid_q && (s_col_q >= 10*28-1) && (s_col_q < (10+1)*28+1-1);
    strip_wa[11] <= (s_row_q%7)*(28+1)*1+(s_col_q-(11*28-1))*1+s_chan_q;
    strip_wen[11] <= s_valid_q && (s_col_q >= 11*28-1) && (s_col_q < (11+1)*28+1-1);
    strip_wa[12] <= (s_row_q%7)*(28+1)*1+(s_col_q-(12*28-1))*1+s_chan_q;
    strip_wen[12] <= s_valid_q && (s_col_q >= 12*28-1) && (s_col_q < (12+1)*28+1-1);
    strip_wa[13] <= (s_row_q%7)*(28+1)*1+(s_col_q-(13*28-1))*1+s_chan_q;
    strip_wen[13] <= s_valid_q && (s_col_q >= 13*28-1) && (s_col_q < (13+1)*28+1-1);
    strip_wa[14] <= (s_row_q%7)*(28+1)*1+(s_col_q-(14*28-1))*1+s_chan_q;
    strip_wen[14] <= s_valid_q && (s_col_q >= 14*28-1) && (s_col_q < (14+1)*28+1-1);
    strip_wa[15] <= (s_row_q%7)*(28+1)*1+(s_col_q-(15*28-1))*1+s_chan_q;
    strip_wen[15] <= s_valid_q && (s_col_q >= 15*28-1) && (s_col_q < (15+1)*28+1-1);
end
wire [16*32-1:0] strip_rd [16-1:0];
reg [32-1:0] patch [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : STRIP
STRIP #(203,512) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(203):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(16):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/1)*32 +:32];
    end
end
endgenerate

wire [32*32-1:0] weight_rd;
wire [32*32-1:0] bias_rd;

WEIGHT4 weight (.clk(m_clk),.ra(weight_ra[$clog2(144):0]),.rd(weight_rd));
BIAS4 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [8-1:0];
reg [32-1:0] bias_mux [8-1:0];
generate
for (i=0; i<8; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*4+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*4+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [8*32-1:0] feat [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : ALU_NS
    for (j=0; j<8; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(448):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==448-1) begin
            icount <= 'd0;
            if ((s_row_q >= 1) && ((s_row_q%2) == (3%2)))
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(224)+1:0] ocol;
reg signed [$clog2(224)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0));
strip_ra[0] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0));
strip_ra[1] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0));
strip_ra[2] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0));
strip_ra[3] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[4] <= strip_zpad[4];
strip_zpad[4] <= ((orow==0)&&(ky<0));
strip_ra[4] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[5] <= strip_zpad[5];
strip_zpad[5] <= ((orow==0)&&(ky<0));
strip_ra[5] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[6] <= strip_zpad[6];
strip_zpad[6] <= ((orow==0)&&(ky<0));
strip_ra[6] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[7] <= strip_zpad[7];
strip_zpad[7] <= ((orow==0)&&(ky<0));
strip_ra[7] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[8] <= strip_zpad[8];
strip_zpad[8] <= ((orow==0)&&(ky<0));
strip_ra[8] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[9] <= strip_zpad[9];
strip_zpad[9] <= ((orow==0)&&(ky<0));
strip_ra[9] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[10] <= strip_zpad[10];
strip_zpad[10] <= ((orow==0)&&(ky<0));
strip_ra[10] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[11] <= strip_zpad[11];
strip_zpad[11] <= ((orow==0)&&(ky<0));
strip_ra[11] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[12] <= strip_zpad[12];
strip_zpad[12] <= ((orow==0)&&(ky<0));
strip_ra[12] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[13] <= strip_zpad[13];
strip_zpad[13] <= ((orow==0)&&(ky<0));
strip_ra[13] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[14] <= strip_zpad[14];
strip_zpad[14] <= ((orow==0)&&(ky<0));
strip_ra[14] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[15] <= strip_zpad[15];
strip_zpad[15] <= ((orow==0)&&(ky<0));
strip_ra[15] <= ((ky+(orow*2))%7)*(28+1)*1+kx*1+ocol*2*1+(ic%1)+1;
weight_ra <= (ky+1)*3*16+(kx+1)*16+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==15) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<16) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*14+ocol < 224) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*14+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==4-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==4-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==14-1) begin
                        ocol <= 'd0;
                        if (orow==224-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           m_row_ack <= 1'b1;
           if (~m_row_req) begin
               m_row_ack <= 1'b0;
               m_state<= 'd0;
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS4 (
    input wire clk,
    output reg [32*32-1:0] rd
);
reg [32*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT4 (
    input wire clk,
    input wire [$clog2(144):0] ra,
    output reg [32*32-1:0] rd
);
reg [32*32-1:0] spram [0:144-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER5 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(4):0] s_chan,
    input wire s_last,
    input wire [$clog2(224):0] s_col,
    input wire [$clog2(224):0] s_row,
    input wire [8*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(2):0] m_chan,
    output reg m_last,
    output reg [$clog2(224):0] m_col,
    output reg [$clog2(224):0] m_row,
    output reg [16*32-1:0] m_data
);

parameter OCMUX=2,OCHAN=32,OWIDTH=224,TDMPAD=      16;

reg [$clog2(504):0] strip_wa [14-1:0];
reg strip_wen [14-1:0];
reg signed [$clog2(504)+1:0] strip_ra [14-1:0];
reg signed [$clog2(288)+1:0] weight_ra;
reg [14-1:0] strip_zpad;
reg [14-1:0] strip_zpad_q;
reg signed [$clog2(32)+1:0] ic;
reg [$clog2(32):0] ic_q,ic_qq;
reg [$clog2(2):0] ochan_sel;
reg [$clog2(14):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(4):0] s_chan_q;
reg [$clog2(224):0] s_col_q;
reg [$clog2(224):0] s_row_q;
reg [8*32-1:0] s_data_q;
reg [8*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(16+2)*4+(s_col_q-(0*16-1))*4+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*16) && (s_col_q < (0+1)*16+2-1);
    strip_wa[1] <= (s_row_q%7)*(16+2)*4+(s_col_q-(1*16-1))*4+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*16-1) && (s_col_q < (1+1)*16+2-1);
    strip_wa[2] <= (s_row_q%7)*(16+2)*4+(s_col_q-(2*16-1))*4+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*16-1) && (s_col_q < (2+1)*16+2-1);
    strip_wa[3] <= (s_row_q%7)*(16+2)*4+(s_col_q-(3*16-1))*4+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*16-1) && (s_col_q < (3+1)*16+2-1);
    strip_wa[4] <= (s_row_q%7)*(16+2)*4+(s_col_q-(4*16-1))*4+s_chan_q;
    strip_wen[4] <= s_valid_q && (s_col_q >= 4*16-1) && (s_col_q < (4+1)*16+2-1);
    strip_wa[5] <= (s_row_q%7)*(16+2)*4+(s_col_q-(5*16-1))*4+s_chan_q;
    strip_wen[5] <= s_valid_q && (s_col_q >= 5*16-1) && (s_col_q < (5+1)*16+2-1);
    strip_wa[6] <= (s_row_q%7)*(16+2)*4+(s_col_q-(6*16-1))*4+s_chan_q;
    strip_wen[6] <= s_valid_q && (s_col_q >= 6*16-1) && (s_col_q < (6+1)*16+2-1);
    strip_wa[7] <= (s_row_q%7)*(16+2)*4+(s_col_q-(7*16-1))*4+s_chan_q;
    strip_wen[7] <= s_valid_q && (s_col_q >= 7*16-1) && (s_col_q < (7+1)*16+2-1);
    strip_wa[8] <= (s_row_q%7)*(16+2)*4+(s_col_q-(8*16-1))*4+s_chan_q;
    strip_wen[8] <= s_valid_q && (s_col_q >= 8*16-1) && (s_col_q < (8+1)*16+2-1);
    strip_wa[9] <= (s_row_q%7)*(16+2)*4+(s_col_q-(9*16-1))*4+s_chan_q;
    strip_wen[9] <= s_valid_q && (s_col_q >= 9*16-1) && (s_col_q < (9+1)*16+2-1);
    strip_wa[10] <= (s_row_q%7)*(16+2)*4+(s_col_q-(10*16-1))*4+s_chan_q;
    strip_wen[10] <= s_valid_q && (s_col_q >= 10*16-1) && (s_col_q < (10+1)*16+2-1);
    strip_wa[11] <= (s_row_q%7)*(16+2)*4+(s_col_q-(11*16-1))*4+s_chan_q;
    strip_wen[11] <= s_valid_q && (s_col_q >= 11*16-1) && (s_col_q < (11+1)*16+2-1);
    strip_wa[12] <= (s_row_q%7)*(16+2)*4+(s_col_q-(12*16-1))*4+s_chan_q;
    strip_wen[12] <= s_valid_q && (s_col_q >= 12*16-1) && (s_col_q < (12+1)*16+2-1);
    strip_wa[13] <= (s_row_q%7)*(16+2)*4+(s_col_q-(13*16-1))*4+s_chan_q;
    strip_wen[13] <= s_valid_q && (s_col_q >= 13*16-1) && (s_col_q < (13+1)*16+2-1);
end
wire [8*32-1:0] strip_rd [14-1:0];
reg [32-1:0] patch [14-1:0];
generate
for (i=0; i<14; i=i+1) begin : STRIP
STRIP #(504,256) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(504):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(32):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/4)*32 +:32];
    end
end
endgenerate

wire [32*32-1:0] weight_rd;
wire [32*32-1:0] bias_rd;

WEIGHT5 weight (.clk(m_clk),.ra(weight_ra[$clog2(288):0]),.rd(weight_rd));
BIAS5 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*2+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [16*32-1:0] feat [14-1:0];
generate
for (i=0; i<14; i=i+1) begin : ALU_NS
    for (j=0; j<16; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(224):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==224-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(224)+1:0] ocol;
reg signed [$clog2(224)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==223)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[2] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[3] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[4] <= strip_zpad[4];
strip_zpad[4] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[4] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[5] <= strip_zpad[5];
strip_zpad[5] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[5] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[6] <= strip_zpad[6];
strip_zpad[6] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[6] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[7] <= strip_zpad[7];
strip_zpad[7] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[7] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[8] <= strip_zpad[8];
strip_zpad[8] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[8] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[9] <= strip_zpad[9];
strip_zpad[9] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[9] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[10] <= strip_zpad[10];
strip_zpad[10] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[10] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[11] <= strip_zpad[11];
strip_zpad[11] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[11] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[12] <= strip_zpad[12];
strip_zpad[12] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[12] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[13] <= strip_zpad[13];
strip_zpad[13] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0)) || ((ocol==15)&&(kx>0));
strip_ra[13] <= ((ky+(orow*1))%7)*(16+2)*4+kx*4+ocol*1*4+(ic%4)+4;
weight_ra <= (ky+1)*3*32+(kx+1)*32+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==31) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<14) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*16+ocol < 224) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*16+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==2-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==2-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==16-1) begin
                        ocol <= 'd0;
                        if (orow==224-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==224-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS5 (
    input wire clk,
    output reg [32*32-1:0] rd
);
reg [32*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT5 (
    input wire clk,
    input wire [$clog2(288):0] ra,
    output reg [32*32-1:0] rd
);
reg [32*32-1:0] spram [0:288-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER6 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(2):0] s_chan,
    input wire s_last,
    input wire [$clog2(224):0] s_col,
    input wire [$clog2(224):0] s_row,
    input wire [16*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(2):0] m_chan,
    output reg m_last,
    output reg [$clog2(224):0] m_col,
    output reg [$clog2(224):0] m_row,
    output reg [16*32-1:0] m_data
);

parameter OCMUX=2,OCHAN=32,OWIDTH=224,TDMPAD=      16;

reg [$clog2(252):0] strip_wa [14-1:0];
reg strip_wen [14-1:0];
reg signed [$clog2(252)+1:0] strip_ra [14-1:0];
reg signed [$clog2(288)+1:0] weight_ra;
reg [14-1:0] strip_zpad;
reg [14-1:0] strip_zpad_q;
reg signed [$clog2(32)+1:0] ic;
reg [$clog2(32):0] ic_q,ic_qq;
reg [$clog2(2):0] ochan_sel;
reg [$clog2(14):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(2):0] s_chan_q;
reg [$clog2(224):0] s_col_q;
reg [$clog2(224):0] s_row_q;
reg [16*32-1:0] s_data_q;
reg [16*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(16+2)*2+(s_col_q-(0*16-1))*2+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*16) && (s_col_q < (0+1)*16+2-1);
    strip_wa[1] <= (s_row_q%7)*(16+2)*2+(s_col_q-(1*16-1))*2+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*16-1) && (s_col_q < (1+1)*16+2-1);
    strip_wa[2] <= (s_row_q%7)*(16+2)*2+(s_col_q-(2*16-1))*2+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*16-1) && (s_col_q < (2+1)*16+2-1);
    strip_wa[3] <= (s_row_q%7)*(16+2)*2+(s_col_q-(3*16-1))*2+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*16-1) && (s_col_q < (3+1)*16+2-1);
    strip_wa[4] <= (s_row_q%7)*(16+2)*2+(s_col_q-(4*16-1))*2+s_chan_q;
    strip_wen[4] <= s_valid_q && (s_col_q >= 4*16-1) && (s_col_q < (4+1)*16+2-1);
    strip_wa[5] <= (s_row_q%7)*(16+2)*2+(s_col_q-(5*16-1))*2+s_chan_q;
    strip_wen[5] <= s_valid_q && (s_col_q >= 5*16-1) && (s_col_q < (5+1)*16+2-1);
    strip_wa[6] <= (s_row_q%7)*(16+2)*2+(s_col_q-(6*16-1))*2+s_chan_q;
    strip_wen[6] <= s_valid_q && (s_col_q >= 6*16-1) && (s_col_q < (6+1)*16+2-1);
    strip_wa[7] <= (s_row_q%7)*(16+2)*2+(s_col_q-(7*16-1))*2+s_chan_q;
    strip_wen[7] <= s_valid_q && (s_col_q >= 7*16-1) && (s_col_q < (7+1)*16+2-1);
    strip_wa[8] <= (s_row_q%7)*(16+2)*2+(s_col_q-(8*16-1))*2+s_chan_q;
    strip_wen[8] <= s_valid_q && (s_col_q >= 8*16-1) && (s_col_q < (8+1)*16+2-1);
    strip_wa[9] <= (s_row_q%7)*(16+2)*2+(s_col_q-(9*16-1))*2+s_chan_q;
    strip_wen[9] <= s_valid_q && (s_col_q >= 9*16-1) && (s_col_q < (9+1)*16+2-1);
    strip_wa[10] <= (s_row_q%7)*(16+2)*2+(s_col_q-(10*16-1))*2+s_chan_q;
    strip_wen[10] <= s_valid_q && (s_col_q >= 10*16-1) && (s_col_q < (10+1)*16+2-1);
    strip_wa[11] <= (s_row_q%7)*(16+2)*2+(s_col_q-(11*16-1))*2+s_chan_q;
    strip_wen[11] <= s_valid_q && (s_col_q >= 11*16-1) && (s_col_q < (11+1)*16+2-1);
    strip_wa[12] <= (s_row_q%7)*(16+2)*2+(s_col_q-(12*16-1))*2+s_chan_q;
    strip_wen[12] <= s_valid_q && (s_col_q >= 12*16-1) && (s_col_q < (12+1)*16+2-1);
    strip_wa[13] <= (s_row_q%7)*(16+2)*2+(s_col_q-(13*16-1))*2+s_chan_q;
    strip_wen[13] <= s_valid_q && (s_col_q >= 13*16-1) && (s_col_q < (13+1)*16+2-1);
end
wire [16*32-1:0] strip_rd [14-1:0];
reg [32-1:0] patch [14-1:0];
generate
for (i=0; i<14; i=i+1) begin : STRIP
STRIP #(252,512) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(252):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(32):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/2)*32 +:32];
    end
end
endgenerate

wire [32*32-1:0] weight_rd;
wire [32*32-1:0] bias_rd;

WEIGHT6 weight (.clk(m_clk),.ra(weight_ra[$clog2(288):0]),.rd(weight_rd));
BIAS6 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*2+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [16*32-1:0] feat [14-1:0];
generate
for (i=0; i<14; i=i+1) begin : ALU_NS
    for (j=0; j<16; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(224):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==224-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(224)+1:0] ocol;
reg signed [$clog2(224)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==223)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[2] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[3] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[4] <= strip_zpad[4];
strip_zpad[4] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[4] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[5] <= strip_zpad[5];
strip_zpad[5] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[5] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[6] <= strip_zpad[6];
strip_zpad[6] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[6] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[7] <= strip_zpad[7];
strip_zpad[7] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[7] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[8] <= strip_zpad[8];
strip_zpad[8] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[8] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[9] <= strip_zpad[9];
strip_zpad[9] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[9] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[10] <= strip_zpad[10];
strip_zpad[10] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[10] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[11] <= strip_zpad[11];
strip_zpad[11] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[11] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[12] <= strip_zpad[12];
strip_zpad[12] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0));
strip_ra[12] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[13] <= strip_zpad[13];
strip_zpad[13] <= ((orow==0)&&(ky<0)) || ((orow==223)&&(ky>0)) || ((ocol==15)&&(kx>0));
strip_ra[13] <= ((ky+(orow*1))%7)*(16+2)*2+kx*2+ocol*1*2+(ic%2)+2;
weight_ra <= (ky+1)*3*32+(kx+1)*32+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==31) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<14) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*16+ocol < 224) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*16+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==2-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==2-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==16-1) begin
                        ocol <= 'd0;
                        if (orow==224-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==224-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS6 (
    input wire clk,
    output reg [32*32-1:0] rd
);
reg [32*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT6 (
    input wire clk,
    input wire [$clog2(288):0] ra,
    output reg [32*32-1:0] rd
);
reg [32*32-1:0] spram [0:288-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER7 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(2):0] s_chan,
    input wire s_last,
    input wire [$clog2(224):0] s_col,
    input wire [$clog2(224):0] s_row,
    input wire [16*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(8):0] m_chan,
    output reg m_last,
    output reg [$clog2(112):0] m_col,
    output reg [$clog2(112):0] m_row,
    output reg [12*32-1:0] m_data
);

parameter OCMUX=8,OCHAN=96,OWIDTH=112,TDMPAD=      32;

reg [$clog2(238):0] strip_wa [14-1:0];
reg strip_wen [14-1:0];
reg signed [$clog2(238)+1:0] strip_ra [14-1:0];
reg signed [$clog2(288)+1:0] weight_ra;
reg [14-1:0] strip_zpad;
reg [14-1:0] strip_zpad_q;
reg signed [$clog2(32)+1:0] ic;
reg [$clog2(32):0] ic_q,ic_qq;
reg [$clog2(8):0] ochan_sel;
reg [$clog2(14):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(2):0] s_chan_q;
reg [$clog2(224):0] s_col_q;
reg [$clog2(224):0] s_row_q;
reg [16*32-1:0] s_data_q;
reg [16*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(16+1)*2+(s_col_q-(0*16-1))*2+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*16) && (s_col_q < (0+1)*16+1-1);
    strip_wa[1] <= (s_row_q%7)*(16+1)*2+(s_col_q-(1*16-1))*2+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*16-1) && (s_col_q < (1+1)*16+1-1);
    strip_wa[2] <= (s_row_q%7)*(16+1)*2+(s_col_q-(2*16-1))*2+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*16-1) && (s_col_q < (2+1)*16+1-1);
    strip_wa[3] <= (s_row_q%7)*(16+1)*2+(s_col_q-(3*16-1))*2+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*16-1) && (s_col_q < (3+1)*16+1-1);
    strip_wa[4] <= (s_row_q%7)*(16+1)*2+(s_col_q-(4*16-1))*2+s_chan_q;
    strip_wen[4] <= s_valid_q && (s_col_q >= 4*16-1) && (s_col_q < (4+1)*16+1-1);
    strip_wa[5] <= (s_row_q%7)*(16+1)*2+(s_col_q-(5*16-1))*2+s_chan_q;
    strip_wen[5] <= s_valid_q && (s_col_q >= 5*16-1) && (s_col_q < (5+1)*16+1-1);
    strip_wa[6] <= (s_row_q%7)*(16+1)*2+(s_col_q-(6*16-1))*2+s_chan_q;
    strip_wen[6] <= s_valid_q && (s_col_q >= 6*16-1) && (s_col_q < (6+1)*16+1-1);
    strip_wa[7] <= (s_row_q%7)*(16+1)*2+(s_col_q-(7*16-1))*2+s_chan_q;
    strip_wen[7] <= s_valid_q && (s_col_q >= 7*16-1) && (s_col_q < (7+1)*16+1-1);
    strip_wa[8] <= (s_row_q%7)*(16+1)*2+(s_col_q-(8*16-1))*2+s_chan_q;
    strip_wen[8] <= s_valid_q && (s_col_q >= 8*16-1) && (s_col_q < (8+1)*16+1-1);
    strip_wa[9] <= (s_row_q%7)*(16+1)*2+(s_col_q-(9*16-1))*2+s_chan_q;
    strip_wen[9] <= s_valid_q && (s_col_q >= 9*16-1) && (s_col_q < (9+1)*16+1-1);
    strip_wa[10] <= (s_row_q%7)*(16+1)*2+(s_col_q-(10*16-1))*2+s_chan_q;
    strip_wen[10] <= s_valid_q && (s_col_q >= 10*16-1) && (s_col_q < (10+1)*16+1-1);
    strip_wa[11] <= (s_row_q%7)*(16+1)*2+(s_col_q-(11*16-1))*2+s_chan_q;
    strip_wen[11] <= s_valid_q && (s_col_q >= 11*16-1) && (s_col_q < (11+1)*16+1-1);
    strip_wa[12] <= (s_row_q%7)*(16+1)*2+(s_col_q-(12*16-1))*2+s_chan_q;
    strip_wen[12] <= s_valid_q && (s_col_q >= 12*16-1) && (s_col_q < (12+1)*16+1-1);
    strip_wa[13] <= (s_row_q%7)*(16+1)*2+(s_col_q-(13*16-1))*2+s_chan_q;
    strip_wen[13] <= s_valid_q && (s_col_q >= 13*16-1) && (s_col_q < (13+1)*16+1-1);
end
wire [16*32-1:0] strip_rd [14-1:0];
reg [32-1:0] patch [14-1:0];
generate
for (i=0; i<14; i=i+1) begin : STRIP
STRIP #(238,512) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(238):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(32):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/2)*32 +:32];
    end
end
endgenerate

wire [32*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT7 weight (.clk(m_clk),.ra(weight_ra[$clog2(288):0]),.rd(weight_rd));
BIAS7 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [12-1:0];
reg [32-1:0] bias_mux [12-1:0];
generate
for (i=0; i<12; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*8+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [12*32-1:0] feat [14-1:0];
generate
for (i=0; i<14; i=i+1) begin : ALU_NS
    for (j=0; j<12; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(224):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==224-1) begin
            icount <= 'd0;
            if ((s_row_q >= 1) && ((s_row_q%2) == (3%2)))
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(112)+1:0] ocol;
reg signed [$clog2(112)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0));
strip_ra[0] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0));
strip_ra[1] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0));
strip_ra[2] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0));
strip_ra[3] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[4] <= strip_zpad[4];
strip_zpad[4] <= ((orow==0)&&(ky<0));
strip_ra[4] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[5] <= strip_zpad[5];
strip_zpad[5] <= ((orow==0)&&(ky<0));
strip_ra[5] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[6] <= strip_zpad[6];
strip_zpad[6] <= ((orow==0)&&(ky<0));
strip_ra[6] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[7] <= strip_zpad[7];
strip_zpad[7] <= ((orow==0)&&(ky<0));
strip_ra[7] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[8] <= strip_zpad[8];
strip_zpad[8] <= ((orow==0)&&(ky<0));
strip_ra[8] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[9] <= strip_zpad[9];
strip_zpad[9] <= ((orow==0)&&(ky<0));
strip_ra[9] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[10] <= strip_zpad[10];
strip_zpad[10] <= ((orow==0)&&(ky<0));
strip_ra[10] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[11] <= strip_zpad[11];
strip_zpad[11] <= ((orow==0)&&(ky<0));
strip_ra[11] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[12] <= strip_zpad[12];
strip_zpad[12] <= ((orow==0)&&(ky<0));
strip_ra[12] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[13] <= strip_zpad[13];
strip_zpad[13] <= ((orow==0)&&(ky<0));
strip_ra[13] <= ((ky+(orow*2))%7)*(16+1)*2+kx*2+ocol*2*2+(ic%2)+2;
weight_ra <= (ky+1)*3*32+(kx+1)*32+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==31) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<14) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*8+ocol < 112) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*8+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==8-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==8-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==8-1) begin
                        ocol <= 'd0;
                        if (orow==112-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           m_row_ack <= 1'b1;
           if (~m_row_req) begin
               m_row_ack <= 1'b0;
               m_state<= 'd0;
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS7 (
    input wire clk,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT7 (
    input wire clk,
    input wire [$clog2(288):0] ra,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:288-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER8 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(8):0] s_chan,
    input wire s_last,
    input wire [$clog2(112):0] s_col,
    input wire [$clog2(112):0] s_row,
    input wire [12*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(1):0] m_chan,
    output reg m_last,
    output reg [$clog2(112):0] m_col,
    output reg [$clog2(112):0] m_row,
    output reg [96*32-1:0] m_data
);

parameter OCMUX=1,OCHAN=96,OWIDTH=112,TDMPAD=    3280;

reg [$clog2(1176):0] strip_wa [6-1:0];
reg strip_wen [6-1:0];
reg signed [$clog2(1176)+1:0] strip_ra [6-1:0];
reg signed [$clog2(864)+1:0] weight_ra;
reg [6-1:0] strip_zpad;
reg [6-1:0] strip_zpad_q;
reg signed [$clog2(96)+1:0] ic;
reg [$clog2(96):0] ic_q,ic_qq;
reg [$clog2(1):0] ochan_sel;
reg [$clog2(6):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(8):0] s_chan_q;
reg [$clog2(112):0] s_col_q;
reg [$clog2(112):0] s_row_q;
reg [12*32-1:0] s_data_q;
reg [12*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(19+2)*8+(s_col_q-(0*19-1))*8+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*19) && (s_col_q < (0+1)*19+2-1);
    strip_wa[1] <= (s_row_q%7)*(19+2)*8+(s_col_q-(1*19-1))*8+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*19-1) && (s_col_q < (1+1)*19+2-1);
    strip_wa[2] <= (s_row_q%7)*(19+2)*8+(s_col_q-(2*19-1))*8+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*19-1) && (s_col_q < (2+1)*19+2-1);
    strip_wa[3] <= (s_row_q%7)*(19+2)*8+(s_col_q-(3*19-1))*8+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*19-1) && (s_col_q < (3+1)*19+2-1);
    strip_wa[4] <= (s_row_q%7)*(19+2)*8+(s_col_q-(4*19-1))*8+s_chan_q;
    strip_wen[4] <= s_valid_q && (s_col_q >= 4*19-1) && (s_col_q < (4+1)*19+2-1);
    strip_wa[5] <= (s_row_q%7)*(19+2)*8+(s_col_q-(5*19-1))*8+s_chan_q;
    strip_wen[5] <= s_valid_q && (s_col_q >= 5*19-1) && (s_col_q < (5+1)*19+2-1);
end
wire [12*32-1:0] strip_rd [6-1:0];
reg [32-1:0] patch [6-1:0];
generate
for (i=0; i<6; i=i+1) begin : STRIP
STRIP #(1176,384) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(1176):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(96):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/8)*32 +:32];
    end
end
endgenerate

wire [32*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT8 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS8 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [96-1:0];
reg [32-1:0] bias_mux [96-1:0];
generate
for (i=0; i<96; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*1+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [96*32-1:0] feat [6-1:0];
generate
for (i=0; i<6; i=i+1) begin : ALU_NS
    for (j=0; j<96; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(112):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==112-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(112)+1:0] ocol;
reg signed [$clog2(112)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==111)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(19+2)*8+kx*8+ocol*1*8+(ic%8)+8;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(19+2)*8+kx*8+ocol*1*8+(ic%8)+8;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0));
strip_ra[2] <= ((ky+(orow*1))%7)*(19+2)*8+kx*8+ocol*1*8+(ic%8)+8;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0));
strip_ra[3] <= ((ky+(orow*1))%7)*(19+2)*8+kx*8+ocol*1*8+(ic%8)+8;
strip_zpad_q[4] <= strip_zpad[4];
strip_zpad[4] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0));
strip_ra[4] <= ((ky+(orow*1))%7)*(19+2)*8+kx*8+ocol*1*8+(ic%8)+8;
strip_zpad_q[5] <= strip_zpad[5];
strip_zpad[5] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0)) || ((ocol==16)&&(kx>0));
strip_ra[5] <= ((ky+(orow*1))%7)*(19+2)*8+kx*8+ocol*1*8+(ic%8)+8;
weight_ra <= (ky+1)*3*96+(kx+1)*96+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==95) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<6) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*19+ocol < 112) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*19+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==1-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==1-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==19-1) begin
                        ocol <= 'd0;
                        if (orow==112-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==112-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS8 (
    input wire clk,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT8 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:864-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER9 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(1):0] s_chan,
    input wire s_last,
    input wire [$clog2(112):0] s_col,
    input wire [$clog2(112):0] s_row,
    input wire [96*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(1):0] m_chan,
    output reg m_last,
    output reg [$clog2(112):0] m_col,
    output reg [$clog2(112):0] m_row,
    output reg [96*32-1:0] m_data
);

parameter OCMUX=1,OCHAN=96,OWIDTH=112,TDMPAD=    3280;

reg [$clog2(147):0] strip_wa [6-1:0];
reg strip_wen [6-1:0];
reg signed [$clog2(147)+1:0] strip_ra [6-1:0];
reg signed [$clog2(864)+1:0] weight_ra;
reg [6-1:0] strip_zpad;
reg [6-1:0] strip_zpad_q;
reg signed [$clog2(96)+1:0] ic;
reg [$clog2(96):0] ic_q,ic_qq;
reg [$clog2(1):0] ochan_sel;
reg [$clog2(6):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(1):0] s_chan_q;
reg [$clog2(112):0] s_col_q;
reg [$clog2(112):0] s_row_q;
reg [96*32-1:0] s_data_q;
reg [96*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(19+2)*1+(s_col_q-(0*19-1))*1+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*19) && (s_col_q < (0+1)*19+2-1);
    strip_wa[1] <= (s_row_q%7)*(19+2)*1+(s_col_q-(1*19-1))*1+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*19-1) && (s_col_q < (1+1)*19+2-1);
    strip_wa[2] <= (s_row_q%7)*(19+2)*1+(s_col_q-(2*19-1))*1+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*19-1) && (s_col_q < (2+1)*19+2-1);
    strip_wa[3] <= (s_row_q%7)*(19+2)*1+(s_col_q-(3*19-1))*1+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*19-1) && (s_col_q < (3+1)*19+2-1);
    strip_wa[4] <= (s_row_q%7)*(19+2)*1+(s_col_q-(4*19-1))*1+s_chan_q;
    strip_wen[4] <= s_valid_q && (s_col_q >= 4*19-1) && (s_col_q < (4+1)*19+2-1);
    strip_wa[5] <= (s_row_q%7)*(19+2)*1+(s_col_q-(5*19-1))*1+s_chan_q;
    strip_wen[5] <= s_valid_q && (s_col_q >= 5*19-1) && (s_col_q < (5+1)*19+2-1);
end
wire [96*32-1:0] strip_rd [6-1:0];
reg [32-1:0] patch [6-1:0];
generate
for (i=0; i<6; i=i+1) begin : STRIP
STRIP #(147,3072) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(147):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(96):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/1)*32 +:32];
    end
end
endgenerate

wire [32*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT9 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS9 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [96-1:0];
reg [32-1:0] bias_mux [96-1:0];
generate
for (i=0; i<96; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*1+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [96*32-1:0] feat [6-1:0];
generate
for (i=0; i<6; i=i+1) begin : ALU_NS
    for (j=0; j<96; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(112):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==112-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(112)+1:0] ocol;
reg signed [$clog2(112)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==111)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(19+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(19+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0));
strip_ra[2] <= ((ky+(orow*1))%7)*(19+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0));
strip_ra[3] <= ((ky+(orow*1))%7)*(19+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[4] <= strip_zpad[4];
strip_zpad[4] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0));
strip_ra[4] <= ((ky+(orow*1))%7)*(19+2)*1+kx*1+ocol*1*1+(ic%1)+1;
strip_zpad_q[5] <= strip_zpad[5];
strip_zpad[5] <= ((orow==0)&&(ky<0)) || ((orow==111)&&(ky>0)) || ((ocol==16)&&(kx>0));
strip_ra[5] <= ((ky+(orow*1))%7)*(19+2)*1+kx*1+ocol*1*1+(ic%1)+1;
weight_ra <= (ky+1)*3*96+(kx+1)*96+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==95) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<6) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*19+ocol < 112) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*19+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==1-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==1-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==19-1) begin
                        ocol <= 'd0;
                        if (orow==112-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==112-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS9 (
    input wire clk,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT9 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:864-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER10 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(1):0] s_chan,
    input wire s_last,
    input wire [$clog2(112):0] s_col,
    input wire [$clog2(112):0] s_row,
    input wire [96*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(4):0] m_chan,
    output reg m_last,
    output reg [$clog2(56):0] m_col,
    output reg [$clog2(56):0] m_row,
    output reg [24*32-1:0] m_data
);

parameter OCMUX=4,OCHAN=96,OWIDTH=56,TDMPAD=    4800;

reg [$clog2(147):0] strip_wa [6-1:0];
reg strip_wen [6-1:0];
reg signed [$clog2(147)+1:0] strip_ra [6-1:0];
reg signed [$clog2(864)+1:0] weight_ra;
reg [6-1:0] strip_zpad;
reg [6-1:0] strip_zpad_q;
reg signed [$clog2(96)+1:0] ic;
reg [$clog2(96):0] ic_q,ic_qq;
reg [$clog2(4):0] ochan_sel;
reg [$clog2(6):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(1):0] s_chan_q;
reg [$clog2(112):0] s_col_q;
reg [$clog2(112):0] s_row_q;
reg [96*32-1:0] s_data_q;
reg [96*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(20+1)*1+(s_col_q-(0*20-1))*1+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*20) && (s_col_q < (0+1)*20+1-1);
    strip_wa[1] <= (s_row_q%7)*(20+1)*1+(s_col_q-(1*20-1))*1+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*20-1) && (s_col_q < (1+1)*20+1-1);
    strip_wa[2] <= (s_row_q%7)*(20+1)*1+(s_col_q-(2*20-1))*1+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*20-1) && (s_col_q < (2+1)*20+1-1);
    strip_wa[3] <= (s_row_q%7)*(20+1)*1+(s_col_q-(3*20-1))*1+s_chan_q;
    strip_wen[3] <= s_valid_q && (s_col_q >= 3*20-1) && (s_col_q < (3+1)*20+1-1);
    strip_wa[4] <= (s_row_q%7)*(20+1)*1+(s_col_q-(4*20-1))*1+s_chan_q;
    strip_wen[4] <= s_valid_q && (s_col_q >= 4*20-1) && (s_col_q < (4+1)*20+1-1);
    strip_wa[5] <= (s_row_q%7)*(20+1)*1+(s_col_q-(5*20-1))*1+s_chan_q;
    strip_wen[5] <= s_valid_q && (s_col_q >= 5*20-1) && (s_col_q < (5+1)*20+1-1);
end
wire [96*32-1:0] strip_rd [6-1:0];
reg [32-1:0] patch [6-1:0];
generate
for (i=0; i<6; i=i+1) begin : STRIP
STRIP #(147,3072) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(147):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(96):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/1)*32 +:32];
    end
end
endgenerate

wire [32*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT10 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS10 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [24-1:0];
reg [32-1:0] bias_mux [24-1:0];
generate
for (i=0; i<24; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*4+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*4+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [24*32-1:0] feat [6-1:0];
generate
for (i=0; i<6; i=i+1) begin : ALU_NS
    for (j=0; j<24; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(112):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==112-1) begin
            icount <= 'd0;
            if ((s_row_q >= 1) && ((s_row_q%2) == (3%2)))
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(56)+1:0] ocol;
reg signed [$clog2(56)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0));
strip_ra[0] <= ((ky+(orow*2))%7)*(20+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0));
strip_ra[1] <= ((ky+(orow*2))%7)*(20+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0));
strip_ra[2] <= ((ky+(orow*2))%7)*(20+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[3] <= strip_zpad[3];
strip_zpad[3] <= ((orow==0)&&(ky<0));
strip_ra[3] <= ((ky+(orow*2))%7)*(20+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[4] <= strip_zpad[4];
strip_zpad[4] <= ((orow==0)&&(ky<0));
strip_ra[4] <= ((ky+(orow*2))%7)*(20+1)*1+kx*1+ocol*2*1+(ic%1)+1;
strip_zpad_q[5] <= strip_zpad[5];
strip_zpad[5] <= ((orow==0)&&(ky<0));
strip_ra[5] <= ((ky+(orow*2))%7)*(20+1)*1+kx*1+ocol*2*1+(ic%1)+1;
weight_ra <= (ky+1)*3*96+(kx+1)*96+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==95) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<6) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*10+ocol < 56) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*10+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==4-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==4-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==10-1) begin
                        ocol <= 'd0;
                        if (orow==56-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           m_row_ack <= 1'b1;
           if (~m_row_req) begin
               m_row_ack <= 1'b0;
               m_state<= 'd0;
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS10 (
    input wire clk,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT10 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:864-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER11 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(4):0] s_chan,
    input wire s_last,
    input wire [$clog2(56):0] s_col,
    input wire [$clog2(56):0] s_row,
    input wire [24*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(2):0] m_chan,
    output reg m_last,
    output reg [$clog2(56):0] m_col,
    output reg [$clog2(56):0] m_row,
    output reg [48*32-1:0] m_data
);

parameter OCMUX=2,OCHAN=96,OWIDTH=56,TDMPAD=    6674;

reg [$clog2(588):0] strip_wa [3-1:0];
reg strip_wen [3-1:0];
reg signed [$clog2(588)+1:0] strip_ra [3-1:0];
reg signed [$clog2(864)+1:0] weight_ra;
reg [3-1:0] strip_zpad;
reg [3-1:0] strip_zpad_q;
reg signed [$clog2(96)+1:0] ic;
reg [$clog2(96):0] ic_q,ic_qq;
reg [$clog2(2):0] ochan_sel;
reg [$clog2(3):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(4):0] s_chan_q;
reg [$clog2(56):0] s_col_q;
reg [$clog2(56):0] s_row_q;
reg [24*32-1:0] s_data_q;
reg [24*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(19+2)*4+(s_col_q-(0*19-1))*4+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*19) && (s_col_q < (0+1)*19+2-1);
    strip_wa[1] <= (s_row_q%7)*(19+2)*4+(s_col_q-(1*19-1))*4+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*19-1) && (s_col_q < (1+1)*19+2-1);
    strip_wa[2] <= (s_row_q%7)*(19+2)*4+(s_col_q-(2*19-1))*4+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*19-1) && (s_col_q < (2+1)*19+2-1);
end
wire [24*32-1:0] strip_rd [3-1:0];
reg [32-1:0] patch [3-1:0];
generate
for (i=0; i<3; i=i+1) begin : STRIP
STRIP #(588,768) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(588):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(96):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/4)*32 +:32];
    end
end
endgenerate

wire [32*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT11 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS11 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [48-1:0];
reg [32-1:0] bias_mux [48-1:0];
generate
for (i=0; i<48; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*2+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [48*32-1:0] feat [3-1:0];
generate
for (i=0; i<3; i=i+1) begin : ALU_NS
    for (j=0; j<48; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(56):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==56-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(56)+1:0] ocol;
reg signed [$clog2(56)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==55)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(19+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==55)&&(ky>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(19+2)*4+kx*4+ocol*1*4+(ic%4)+4;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0)) || ((orow==55)&&(ky>0)) || ((ocol==17)&&(kx>0));
strip_ra[2] <= ((ky+(orow*1))%7)*(19+2)*4+kx*4+ocol*1*4+(ic%4)+4;
weight_ra <= (ky+1)*3*96+(kx+1)*96+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==95) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<3) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*19+ocol < 56) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*19+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==2-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==2-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==19-1) begin
                        ocol <= 'd0;
                        if (orow==56-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==56-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS11 (
    input wire clk,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT11 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:864-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER12 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(2):0] s_chan,
    input wire s_last,
    input wire [$clog2(56):0] s_col,
    input wire [$clog2(56):0] s_row,
    input wire [48*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(2):0] m_chan,
    output reg m_last,
    output reg [$clog2(56):0] m_col,
    output reg [$clog2(56):0] m_row,
    output reg [48*32-1:0] m_data
);

parameter OCMUX=2,OCHAN=96,OWIDTH=56,TDMPAD=    6674;

reg [$clog2(294):0] strip_wa [3-1:0];
reg strip_wen [3-1:0];
reg signed [$clog2(294)+1:0] strip_ra [3-1:0];
reg signed [$clog2(864)+1:0] weight_ra;
reg [3-1:0] strip_zpad;
reg [3-1:0] strip_zpad_q;
reg signed [$clog2(96)+1:0] ic;
reg [$clog2(96):0] ic_q,ic_qq;
reg [$clog2(2):0] ochan_sel;
reg [$clog2(3):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(2):0] s_chan_q;
reg [$clog2(56):0] s_col_q;
reg [$clog2(56):0] s_row_q;
reg [48*32-1:0] s_data_q;
reg [48*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(19+2)*2+(s_col_q-(0*19-1))*2+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*19) && (s_col_q < (0+1)*19+2-1);
    strip_wa[1] <= (s_row_q%7)*(19+2)*2+(s_col_q-(1*19-1))*2+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*19-1) && (s_col_q < (1+1)*19+2-1);
    strip_wa[2] <= (s_row_q%7)*(19+2)*2+(s_col_q-(2*19-1))*2+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*19-1) && (s_col_q < (2+1)*19+2-1);
end
wire [48*32-1:0] strip_rd [3-1:0];
reg [32-1:0] patch [3-1:0];
generate
for (i=0; i<3; i=i+1) begin : STRIP
STRIP #(294,1536) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(294):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(96):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/2)*32 +:32];
    end
end
endgenerate

wire [32*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT12 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS12 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [48-1:0];
reg [32-1:0] bias_mux [48-1:0];
generate
for (i=0; i<48; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*2+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [48*32-1:0] feat [3-1:0];
generate
for (i=0; i<3; i=i+1) begin : ALU_NS
    for (j=0; j<48; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(56):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==56-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(56)+1:0] ocol;
reg signed [$clog2(56)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==55)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(19+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==55)&&(ky>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(19+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0)) || ((orow==55)&&(ky>0)) || ((ocol==17)&&(kx>0));
strip_ra[2] <= ((ky+(orow*1))%7)*(19+2)*2+kx*2+ocol*1*2+(ic%2)+2;
weight_ra <= (ky+1)*3*96+(kx+1)*96+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==95) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<3) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*19+ocol < 56) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*19+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==2-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==2-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==19-1) begin
                        ocol <= 'd0;
                        if (orow==56-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==56-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS12 (
    input wire clk,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT12 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output reg [96*32-1:0] rd
);
reg [96*32-1:0] spram [0:864-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER13 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(2):0] s_chan,
    input wire s_last,
    input wire [$clog2(56):0] s_col,
    input wire [$clog2(56):0] s_row,
    input wire [48*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(8):0] m_chan,
    output reg m_last,
    output reg [$clog2(28):0] m_col,
    output reg [$clog2(28):0] m_row,
    output reg [24*32-1:0] m_data
);

parameter OCMUX=8,OCHAN=192,OWIDTH=28,TDMPAD=    9840;

reg [$clog2(294):0] strip_wa [3-1:0];
reg strip_wen [3-1:0];
reg signed [$clog2(294)+1:0] strip_ra [3-1:0];
reg signed [$clog2(864)+1:0] weight_ra;
reg [3-1:0] strip_zpad;
reg [3-1:0] strip_zpad_q;
reg signed [$clog2(96)+1:0] ic;
reg [$clog2(96):0] ic_q,ic_qq;
reg [$clog2(8):0] ochan_sel;
reg [$clog2(3):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(2):0] s_chan_q;
reg [$clog2(56):0] s_col_q;
reg [$clog2(56):0] s_row_q;
reg [48*32-1:0] s_data_q;
reg [48*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(20+1)*2+(s_col_q-(0*20-1))*2+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*20) && (s_col_q < (0+1)*20+1-1);
    strip_wa[1] <= (s_row_q%7)*(20+1)*2+(s_col_q-(1*20-1))*2+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*20-1) && (s_col_q < (1+1)*20+1-1);
    strip_wa[2] <= (s_row_q%7)*(20+1)*2+(s_col_q-(2*20-1))*2+s_chan_q;
    strip_wen[2] <= s_valid_q && (s_col_q >= 2*20-1) && (s_col_q < (2+1)*20+1-1);
end
wire [48*32-1:0] strip_rd [3-1:0];
reg [32-1:0] patch [3-1:0];
generate
for (i=0; i<3; i=i+1) begin : STRIP
STRIP #(294,1536) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(294):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(96):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/2)*32 +:32];
    end
end
endgenerate

wire [32*192-1:0] weight_rd;
wire [32*192-1:0] bias_rd;

WEIGHT13 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS13 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [24-1:0];
reg [32-1:0] bias_mux [24-1:0];
generate
for (i=0; i<24; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*8+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [24*32-1:0] feat [3-1:0];
generate
for (i=0; i<3; i=i+1) begin : ALU_NS
    for (j=0; j<24; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(56):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==56-1) begin
            icount <= 'd0;
            if ((s_row_q >= 1) && ((s_row_q%2) == (3%2)))
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(28)+1:0] ocol;
reg signed [$clog2(28)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0));
strip_ra[0] <= ((ky+(orow*2))%7)*(20+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0));
strip_ra[1] <= ((ky+(orow*2))%7)*(20+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[2] <= strip_zpad[2];
strip_zpad[2] <= ((orow==0)&&(ky<0));
strip_ra[2] <= ((ky+(orow*2))%7)*(20+1)*2+kx*2+ocol*2*2+(ic%2)+2;
weight_ra <= (ky+1)*3*96+(kx+1)*96+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==95) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<3) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*10+ocol < 28) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*10+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==8-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==8-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==10-1) begin
                        ocol <= 'd0;
                        if (orow==28-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           m_row_ack <= 1'b1;
           if (~m_row_req) begin
               m_row_ack <= 1'b0;
               m_state<= 'd0;
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS13 (
    input wire clk,
    output reg [192*32-1:0] rd
);
reg [192*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT13 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output reg [192*32-1:0] rd
);
reg [192*32-1:0] spram [0:864-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER14 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(8):0] s_chan,
    input wire s_last,
    input wire [$clog2(28):0] s_col,
    input wire [$clog2(28):0] s_row,
    input wire [24*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(2):0] m_chan,
    output reg m_last,
    output reg [$clog2(28):0] m_col,
    output reg [$clog2(28):0] m_row,
    output reg [96*32-1:0] m_data
);

parameter OCMUX=2,OCHAN=192,OWIDTH=28,TDMPAD=   31280;

reg [$clog2(896):0] strip_wa [2-1:0];
reg strip_wen [2-1:0];
reg signed [$clog2(896)+1:0] strip_ra [2-1:0];
reg signed [$clog2(1728)+1:0] weight_ra;
reg [2-1:0] strip_zpad;
reg [2-1:0] strip_zpad_q;
reg signed [$clog2(192)+1:0] ic;
reg [$clog2(192):0] ic_q,ic_qq;
reg [$clog2(2):0] ochan_sel;
reg [$clog2(2):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(8):0] s_chan_q;
reg [$clog2(28):0] s_col_q;
reg [$clog2(28):0] s_row_q;
reg [24*32-1:0] s_data_q;
reg [24*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(14+2)*8+(s_col_q-(0*14-1))*8+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*14) && (s_col_q < (0+1)*14+2-1);
    strip_wa[1] <= (s_row_q%7)*(14+2)*8+(s_col_q-(1*14-1))*8+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*14-1) && (s_col_q < (1+1)*14+2-1);
end
wire [24*32-1:0] strip_rd [2-1:0];
reg [32-1:0] patch [2-1:0];
generate
for (i=0; i<2; i=i+1) begin : STRIP
STRIP #(896,768) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(896):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(192):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/8)*32 +:32];
    end
end
endgenerate

wire [32*192-1:0] weight_rd;
wire [32*192-1:0] bias_rd;

WEIGHT14 weight (.clk(m_clk),.ra(weight_ra[$clog2(1728):0]),.rd(weight_rd));
BIAS14 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [96-1:0];
reg [32-1:0] bias_mux [96-1:0];
generate
for (i=0; i<96; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*2+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [96*32-1:0] feat [2-1:0];
generate
for (i=0; i<2; i=i+1) begin : ALU_NS
    for (j=0; j<96; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(28):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==28-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(28)+1:0] ocol;
reg signed [$clog2(28)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==27)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(14+2)*8+kx*8+ocol*1*8+(ic%8)+8;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==27)&&(ky>0)) || ((ocol==13)&&(kx>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(14+2)*8+kx*8+ocol*1*8+(ic%8)+8;
weight_ra <= (ky+1)*3*192+(kx+1)*192+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==191) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<2) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*14+ocol < 28) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*14+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==2-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==2-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==14-1) begin
                        ocol <= 'd0;
                        if (orow==28-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==28-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS14 (
    input wire clk,
    output reg [192*32-1:0] rd
);
reg [192*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT14 (
    input wire clk,
    input wire [$clog2(1728):0] ra,
    output reg [192*32-1:0] rd
);
reg [192*32-1:0] spram [0:1728-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER15 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(2):0] s_chan,
    input wire s_last,
    input wire [$clog2(28):0] s_col,
    input wire [$clog2(28):0] s_row,
    input wire [96*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(2):0] m_chan,
    output reg m_last,
    output reg [$clog2(28):0] m_col,
    output reg [$clog2(28):0] m_row,
    output reg [96*32-1:0] m_data
);

parameter OCMUX=2,OCHAN=192,OWIDTH=28,TDMPAD=   31280;

reg [$clog2(224):0] strip_wa [2-1:0];
reg strip_wen [2-1:0];
reg signed [$clog2(224)+1:0] strip_ra [2-1:0];
reg signed [$clog2(1728)+1:0] weight_ra;
reg [2-1:0] strip_zpad;
reg [2-1:0] strip_zpad_q;
reg signed [$clog2(192)+1:0] ic;
reg [$clog2(192):0] ic_q,ic_qq;
reg [$clog2(2):0] ochan_sel;
reg [$clog2(2):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(2):0] s_chan_q;
reg [$clog2(28):0] s_col_q;
reg [$clog2(28):0] s_row_q;
reg [96*32-1:0] s_data_q;
reg [96*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(14+2)*2+(s_col_q-(0*14-1))*2+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*14) && (s_col_q < (0+1)*14+2-1);
    strip_wa[1] <= (s_row_q%7)*(14+2)*2+(s_col_q-(1*14-1))*2+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*14-1) && (s_col_q < (1+1)*14+2-1);
end
wire [96*32-1:0] strip_rd [2-1:0];
reg [32-1:0] patch [2-1:0];
generate
for (i=0; i<2; i=i+1) begin : STRIP
STRIP #(224,3072) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(224):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(192):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/2)*32 +:32];
    end
end
endgenerate

wire [32*192-1:0] weight_rd;
wire [32*192-1:0] bias_rd;

WEIGHT15 weight (.clk(m_clk),.ra(weight_ra[$clog2(1728):0]),.rd(weight_rd));
BIAS15 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [96-1:0];
reg [32-1:0] bias_mux [96-1:0];
generate
for (i=0; i<96; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*2+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [96*32-1:0] feat [2-1:0];
generate
for (i=0; i<2; i=i+1) begin : ALU_NS
    for (j=0; j<96; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(28):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==28-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(28)+1:0] ocol;
reg signed [$clog2(28)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==27)&&(ky>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(14+2)*2+kx*2+ocol*1*2+(ic%2)+2;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0)) || ((orow==27)&&(ky>0)) || ((ocol==13)&&(kx>0));
strip_ra[1] <= ((ky+(orow*1))%7)*(14+2)*2+kx*2+ocol*1*2+(ic%2)+2;
weight_ra <= (ky+1)*3*192+(kx+1)*192+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==191) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<2) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*14+ocol < 28) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*14+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==2-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==2-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==14-1) begin
                        ocol <= 'd0;
                        if (orow==28-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==28-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS15 (
    input wire clk,
    output reg [192*32-1:0] rd
);
reg [192*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT15 (
    input wire clk,
    input wire [$clog2(1728):0] ra,
    output reg [192*32-1:0] rd
);
reg [192*32-1:0] spram [0:1728-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER16 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(2):0] s_chan,
    input wire s_last,
    input wire [$clog2(28):0] s_col,
    input wire [$clog2(28):0] s_row,
    input wire [96*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(8):0] m_chan,
    output reg m_last,
    output reg [$clog2(14):0] m_col,
    output reg [$clog2(14):0] m_row,
    output reg [40*32-1:0] m_data
);

parameter OCMUX=8,OCHAN=320,OWIDTH=14,TDMPAD=   62560;

reg [$clog2(210):0] strip_wa [2-1:0];
reg strip_wen [2-1:0];
reg signed [$clog2(210)+1:0] strip_ra [2-1:0];
reg signed [$clog2(1728)+1:0] weight_ra;
reg [2-1:0] strip_zpad;
reg [2-1:0] strip_zpad_q;
reg signed [$clog2(192)+1:0] ic;
reg [$clog2(192):0] ic_q,ic_qq;
reg [$clog2(8):0] ochan_sel;
reg [$clog2(2):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(2):0] s_chan_q;
reg [$clog2(28):0] s_col_q;
reg [$clog2(28):0] s_row_q;
reg [96*32-1:0] s_data_q;
reg [96*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(14+1)*2+(s_col_q-(0*14-1))*2+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*14) && (s_col_q < (0+1)*14+1-1);
    strip_wa[1] <= (s_row_q%7)*(14+1)*2+(s_col_q-(1*14-1))*2+s_chan_q;
    strip_wen[1] <= s_valid_q && (s_col_q >= 1*14-1) && (s_col_q < (1+1)*14+1-1);
end
wire [96*32-1:0] strip_rd [2-1:0];
reg [32-1:0] patch [2-1:0];
generate
for (i=0; i<2; i=i+1) begin : STRIP
STRIP #(210,3072) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(210):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(192):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/2)*32 +:32];
    end
end
endgenerate

wire [32*320-1:0] weight_rd;
wire [32*320-1:0] bias_rd;

WEIGHT16 weight (.clk(m_clk),.ra(weight_ra[$clog2(1728):0]),.rd(weight_rd));
BIAS16 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [40-1:0];
reg [32-1:0] bias_mux [40-1:0];
generate
for (i=0; i<40; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*8+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [40*32-1:0] feat [2-1:0];
generate
for (i=0; i<2; i=i+1) begin : ALU_NS
    for (j=0; j<40; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(28):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==28-1) begin
            icount <= 'd0;
            if ((s_row_q >= 1) && ((s_row_q%2) == (3%2)))
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(14)+1:0] ocol;
reg signed [$clog2(14)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0));
strip_ra[0] <= ((ky+(orow*2))%7)*(14+1)*2+kx*2+ocol*2*2+(ic%2)+2;
strip_zpad_q[1] <= strip_zpad[1];
strip_zpad[1] <= ((orow==0)&&(ky<0));
strip_ra[1] <= ((ky+(orow*2))%7)*(14+1)*2+kx*2+ocol*2*2+(ic%2)+2;
weight_ra <= (ky+1)*3*192+(kx+1)*192+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==191) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<2) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*7+ocol < 14) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*7+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==8-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==8-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==7-1) begin
                        ocol <= 'd0;
                        if (orow==14-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           m_row_ack <= 1'b1;
           if (~m_row_req) begin
               m_row_ack <= 1'b0;
               m_state<= 'd0;
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS16 (
    input wire clk,
    output reg [320*32-1:0] rd
);
reg [320*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT16 (
    input wire clk,
    input wire [$clog2(1728):0] ra,
    output reg [320*32-1:0] rd
);
reg [320*32-1:0] spram [0:1728-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER17 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(8):0] s_chan,
    input wire s_last,
    input wire [$clog2(14):0] s_col,
    input wire [$clog2(14):0] s_row,
    input wire [40*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(2):0] m_chan,
    output reg m_last,
    output reg [$clog2(14):0] m_col,
    output reg [$clog2(14):0] m_row,
    output reg [160*32-1:0] m_data
);

parameter OCMUX=2,OCHAN=320,OWIDTH=14,TDMPAD=   79052;

reg [$clog2(896):0] strip_wa [1-1:0];
reg strip_wen [1-1:0];
reg signed [$clog2(896)+1:0] strip_ra [1-1:0];
reg signed [$clog2(2880)+1:0] weight_ra;
reg [1-1:0] strip_zpad;
reg [1-1:0] strip_zpad_q;
reg signed [$clog2(320)+1:0] ic;
reg [$clog2(320):0] ic_q,ic_qq;
reg [$clog2(2):0] ochan_sel;
reg [$clog2(1):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(8):0] s_chan_q;
reg [$clog2(14):0] s_col_q;
reg [$clog2(14):0] s_row_q;
reg [40*32-1:0] s_data_q;
reg [40*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(14+2)*8+(s_col_q-(0*14-1))*8+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*14) && (s_col_q < (0+1)*14+2-1);
end
wire [40*32-1:0] strip_rd [1-1:0];
reg [32-1:0] patch [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : STRIP
STRIP #(896,1280) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(896):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(320):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/8)*32 +:32];
    end
end
endgenerate

wire [32*320-1:0] weight_rd;
wire [32*320-1:0] bias_rd;

WEIGHT17 weight (.clk(m_clk),.ra(weight_ra[$clog2(2880):0]),.rd(weight_rd));
BIAS17 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [160-1:0];
reg [32-1:0] bias_mux [160-1:0];
generate
for (i=0; i<160; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*2+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [160*32-1:0] feat [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : ALU_NS
    for (j=0; j<160; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(14):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==14-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(14)+1:0] ocol;
reg signed [$clog2(14)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==13)&&(ky>0)) || ((ocol==13)&&(kx>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(14+2)*8+kx*8+ocol*1*8+(ic%8)+8;
weight_ra <= (ky+1)*3*320+(kx+1)*320+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==319) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<1) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*14+ocol < 14) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*14+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==2-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==2-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==14-1) begin
                        ocol <= 'd0;
                        if (orow==14-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==14-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS17 (
    input wire clk,
    output reg [320*32-1:0] rd
);
reg [320*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT17 (
    input wire clk,
    input wire [$clog2(2880):0] ra,
    output reg [320*32-1:0] rd
);
reg [320*32-1:0] spram [0:2880-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER18 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(2):0] s_chan,
    input wire s_last,
    input wire [$clog2(14):0] s_col,
    input wire [$clog2(14):0] s_row,
    input wire [160*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(2):0] m_chan,
    output reg m_last,
    output reg [$clog2(14):0] m_col,
    output reg [$clog2(14):0] m_row,
    output reg [160*32-1:0] m_data
);

parameter OCMUX=2,OCHAN=320,OWIDTH=14,TDMPAD=   79052;

reg [$clog2(224):0] strip_wa [1-1:0];
reg strip_wen [1-1:0];
reg signed [$clog2(224)+1:0] strip_ra [1-1:0];
reg signed [$clog2(2880)+1:0] weight_ra;
reg [1-1:0] strip_zpad;
reg [1-1:0] strip_zpad_q;
reg signed [$clog2(320)+1:0] ic;
reg [$clog2(320):0] ic_q,ic_qq;
reg [$clog2(2):0] ochan_sel;
reg [$clog2(1):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(2):0] s_chan_q;
reg [$clog2(14):0] s_col_q;
reg [$clog2(14):0] s_row_q;
reg [160*32-1:0] s_data_q;
reg [160*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(14+2)*2+(s_col_q-(0*14-1))*2+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*14) && (s_col_q < (0+1)*14+2-1);
end
wire [160*32-1:0] strip_rd [1-1:0];
reg [32-1:0] patch [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : STRIP
STRIP #(224,5120) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(224):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(320):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/2)*32 +:32];
    end
end
endgenerate

wire [32*320-1:0] weight_rd;
wire [32*320-1:0] bias_rd;

WEIGHT18 weight (.clk(m_clk),.ra(weight_ra[$clog2(2880):0]),.rd(weight_rd));
BIAS18 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [160-1:0];
reg [32-1:0] bias_mux [160-1:0];
generate
for (i=0; i<160; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*2+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [160*32-1:0] feat [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : ALU_NS
    for (j=0; j<160; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(14):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==14-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(14)+1:0] ocol;
reg signed [$clog2(14)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==13)&&(ky>0)) || ((ocol==13)&&(kx>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(14+2)*2+kx*2+ocol*1*2+(ic%2)+2;
weight_ra <= (ky+1)*3*320+(kx+1)*320+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==319) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<1) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*14+ocol < 14) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*14+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==2-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==2-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==14-1) begin
                        ocol <= 'd0;
                        if (orow==14-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==14-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS18 (
    input wire clk,
    output reg [320*32-1:0] rd
);
reg [320*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT18 (
    input wire clk,
    input wire [$clog2(2880):0] ra,
    output reg [320*32-1:0] rd
);
reg [320*32-1:0] spram [0:2880-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER19 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(2):0] s_chan,
    input wire s_last,
    input wire [$clog2(14):0] s_col,
    input wire [$clog2(14):0] s_row,
    input wire [160*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(8):0] m_chan,
    output reg m_last,
    output reg [$clog2(7):0] m_col,
    output reg [$clog2(7):0] m_row,
    output reg [64*32-1:0] m_data
);

parameter OCMUX=8,OCHAN=512,OWIDTH=7,TDMPAD=  158104;

reg [$clog2(210):0] strip_wa [1-1:0];
reg strip_wen [1-1:0];
reg signed [$clog2(210)+1:0] strip_ra [1-1:0];
reg signed [$clog2(2880)+1:0] weight_ra;
reg [1-1:0] strip_zpad;
reg [1-1:0] strip_zpad_q;
reg signed [$clog2(320)+1:0] ic;
reg [$clog2(320):0] ic_q,ic_qq;
reg [$clog2(8):0] ochan_sel;
reg [$clog2(1):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(2):0] s_chan_q;
reg [$clog2(14):0] s_col_q;
reg [$clog2(14):0] s_row_q;
reg [160*32-1:0] s_data_q;
reg [160*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(14+1)*2+(s_col_q-(0*14-1))*2+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*14) && (s_col_q < (0+1)*14+1-1);
end
wire [160*32-1:0] strip_rd [1-1:0];
reg [32-1:0] patch [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : STRIP
STRIP #(210,5120) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(210):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(320):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/2)*32 +:32];
    end
end
endgenerate

wire [32*512-1:0] weight_rd;
wire [32*512-1:0] bias_rd;

WEIGHT19 weight (.clk(m_clk),.ra(weight_ra[$clog2(2880):0]),.rd(weight_rd));
BIAS19 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [64-1:0];
reg [32-1:0] bias_mux [64-1:0];
generate
for (i=0; i<64; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*8+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [64*32-1:0] feat [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : ALU_NS
    for (j=0; j<64; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(14):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==14-1) begin
            icount <= 'd0;
            if ((s_row_q >= 1) && ((s_row_q%2) == (3%2)))
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(7)+1:0] ocol;
reg signed [$clog2(7)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0));
strip_ra[0] <= ((ky+(orow*2))%7)*(14+1)*2+kx*2+ocol*2*2+(ic%2)+2;
weight_ra <= (ky+1)*3*320+(kx+1)*320+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==319) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<1) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*7+ocol < 7) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*7+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==8-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==8-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==7-1) begin
                        ocol <= 'd0;
                        if (orow==7-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           m_row_ack <= 1'b1;
           if (~m_row_req) begin
               m_row_ack <= 1'b0;
               m_state<= 'd0;
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS19 (
    input wire clk,
    output reg [512*32-1:0] rd
);
reg [512*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT19 (
    input wire clk,
    input wire [$clog2(2880):0] ra,
    output reg [512*32-1:0] rd
);
reg [512*32-1:0] spram [0:2880-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER20 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(8):0] s_chan,
    input wire s_last,
    input wire [$clog2(7):0] s_col,
    input wire [$clog2(7):0] s_row,
    input wire [64*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(8):0] m_chan,
    output reg m_last,
    output reg [$clog2(7):0] m_col,
    output reg [$clog2(7):0] m_row,
    output reg [64*32-1:0] m_data
);

parameter OCMUX=8,OCHAN=512,OWIDTH=7,TDMPAD=   61336;

reg [$clog2(504):0] strip_wa [1-1:0];
reg strip_wen [1-1:0];
reg signed [$clog2(504)+1:0] strip_ra [1-1:0];
reg signed [$clog2(4608)+1:0] weight_ra;
reg [1-1:0] strip_zpad;
reg [1-1:0] strip_zpad_q;
reg signed [$clog2(512)+1:0] ic;
reg [$clog2(512):0] ic_q,ic_qq;
reg [$clog2(8):0] ochan_sel;
reg [$clog2(1):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(8):0] s_chan_q;
reg [$clog2(7):0] s_col_q;
reg [$clog2(7):0] s_row_q;
reg [64*32-1:0] s_data_q;
reg [64*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(7+2)*8+(s_col_q-(0*7-1))*8+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*7) && (s_col_q < (0+1)*7+2-1);
end
wire [64*32-1:0] strip_rd [1-1:0];
reg [32-1:0] patch [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : STRIP
STRIP #(504,2048) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(504):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(512):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/8)*32 +:32];
    end
end
endgenerate

wire [32*512-1:0] weight_rd;
wire [32*512-1:0] bias_rd;

WEIGHT20 weight (.clk(m_clk),.ra(weight_ra[$clog2(4608):0]),.rd(weight_rd));
BIAS20 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [64-1:0];
reg [32-1:0] bias_mux [64-1:0];
generate
for (i=0; i<64; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*8+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [64*32-1:0] feat [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : ALU_NS
    for (j=0; j<64; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(7):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==7-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(7)+1:0] ocol;
reg signed [$clog2(7)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==6)&&(ky>0)) || ((ocol==6)&&(kx>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(7+2)*8+kx*8+ocol*1*8+(ic%8)+8;
weight_ra <= (ky+1)*3*512+(kx+1)*512+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==511) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<1) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*7+ocol < 7) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*7+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==8-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==8-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==7-1) begin
                        ocol <= 'd0;
                        if (orow==7-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==7-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS20 (
    input wire clk,
    output reg [512*32-1:0] rd
);
reg [512*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT20 (
    input wire clk,
    input wire [$clog2(4608):0] ra,
    output reg [512*32-1:0] rd
);
reg [512*32-1:0] spram [0:4608-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER21 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(8):0] s_chan,
    input wire s_last,
    input wire [$clog2(7):0] s_col,
    input wire [$clog2(7):0] s_row,
    input wire [64*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(8):0] m_chan,
    output reg m_last,
    output reg [$clog2(7):0] m_col,
    output reg [$clog2(7):0] m_row,
    output reg [64*32-1:0] m_data
);

parameter OCMUX=8,OCHAN=512,OWIDTH=7,TDMPAD=   61336;

reg [$clog2(504):0] strip_wa [1-1:0];
reg strip_wen [1-1:0];
reg signed [$clog2(504)+1:0] strip_ra [1-1:0];
reg signed [$clog2(4608)+1:0] weight_ra;
reg [1-1:0] strip_zpad;
reg [1-1:0] strip_zpad_q;
reg signed [$clog2(512)+1:0] ic;
reg [$clog2(512):0] ic_q,ic_qq;
reg [$clog2(8):0] ochan_sel;
reg [$clog2(1):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(8):0] s_chan_q;
reg [$clog2(7):0] s_col_q;
reg [$clog2(7):0] s_row_q;
reg [64*32-1:0] s_data_q;
reg [64*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%7)*(7+2)*8+(s_col_q-(0*7-1))*8+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*7) && (s_col_q < (0+1)*7+2-1);
end
wire [64*32-1:0] strip_rd [1-1:0];
reg [32-1:0] patch [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : STRIP
STRIP #(504,2048) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(504):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(512):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/8)*32 +:32];
    end
end
endgenerate

wire [32*512-1:0] weight_rd;
wire [32*512-1:0] bias_rd;

WEIGHT21 weight (.clk(m_clk),.ra(weight_ra[$clog2(4608):0]),.rd(weight_rd));
BIAS21 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [64-1:0];
reg [32-1:0] bias_mux [64-1:0];
generate
for (i=0; i<64; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*8+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [64*32-1:0] feat [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : ALU_NS
    for (j=0; j<64; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(7):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==7-1) begin
            icount <= 'd0;
            if (s_row_q >= 1)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(3)+1:0] ky;
reg signed [$clog2(3)+1:0] kx;
reg signed [$clog2(7)+1:0] ocol;
reg signed [$clog2(7)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= ((orow==0)&&(ky<0)) || ((ocol==0)&&(kx<0)) || ((orow==6)&&(ky>0)) || ((ocol==6)&&(kx>0));
strip_ra[0] <= ((ky+(orow*1))%7)*(7+2)*8+kx*8+ocol*1*8+(ic%8)+8;
weight_ra <= (ky+1)*3*512+(kx+1)*512+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==511) begin
                if (kx==1) begin
                    if (ky==1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd6;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd6;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd6;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd6;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<1) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*7+ocol < 7) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*7+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==8-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==8-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==7-1) begin
                        ocol <= 'd0;
                        if (orow==7-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           if (orow==7-1) begin
               ocol <= 'd0;
               ochan_sel <= 'd0;
               alu_op <= 'd0;
               m_rowwait_count <= 0;
               m_state<= 'd10;
           end
           else begin
               m_row_ack <= 1'b1;
               if (~m_row_req) begin
                   m_row_ack <= 1'b0;
                   m_state<= 'd0;
               end
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS21 (
    input wire clk,
    output reg [512*32-1:0] rd
);
reg [512*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT21 (
    input wire clk,
    input wire [$clog2(4608):0] ra,
    output reg [512*32-1:0] rd
);
reg [512*32-1:0] spram [0:4608-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module LAYER22 (
    input wire s_clk,
    input wire m_clk,
    input wire reset,
    input wire s_valid,
    input wire [$clog2(8):0] s_chan,
    input wire s_last,
    input wire [$clog2(7):0] s_col,
    input wire [$clog2(7):0] s_row,
    input wire [64*32-1:0] s_data,
    output reg m_valid,
    output reg [$clog2(64):0] m_chan,
    output reg m_last,
    output reg [$clog2(7):0] m_col,
    output reg [$clog2(7):0] m_row,
    output reg [8*32-1:0] m_data
);

parameter OCMUX=64,OCHAN=512,OWIDTH=7,TDMPAD=   85696;

reg [$clog2(360):0] strip_wa [1-1:0];
reg strip_wen [1-1:0];
reg signed [$clog2(360)+1:0] strip_ra [1-1:0];
reg signed [$clog2(512)+1:0] weight_ra;
reg [1-1:0] strip_zpad;
reg [1-1:0] strip_zpad_q;
reg signed [$clog2(512)+1:0] ic;
reg [$clog2(512):0] ic_q,ic_qq;
reg [$clog2(64):0] ochan_sel;
reg [$clog2(1):0] strip_sel;
reg [4:0] alu_op;

genvar i,j;
reg s_valid_q;
reg s_last_q;
reg [$clog2(8):0] s_chan_q;
reg [$clog2(7):0] s_col_q;
reg [$clog2(7):0] s_row_q;
reg [64*32-1:0] s_data_q;
reg [64*32-1:0] s_data_qq;
always @(posedge s_clk) begin
    s_valid_q <= s_valid;
    s_chan_q <= s_chan;
    s_last_q <= s_last;
    s_col_q <= s_col;
    s_row_q <= s_row;
    s_data_q <= s_data;
    s_data_qq <= s_data_q;
end
always @ (posedge s_clk) begin
    strip_wa[0] <= (s_row_q%5)*(7+2)*8+(s_col_q-(0*7-1))*8+s_chan_q;
    strip_wen[0] <= s_valid_q && (s_col_q >= 0*7) && (s_col_q < (0+1)*7+2-1);
end
wire [64*32-1:0] strip_rd [1-1:0];
reg [32-1:0] patch [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : STRIP
STRIP #(360,2048) strip (.wclk(s_clk),.rclk(m_clk),.reset(reset),.ra(strip_ra[i][$clog2(360):0]),.rd(strip_rd[i]),.wen(strip_wen[i]),.wa(strip_wa[i]),.wd(s_data_qq));
    always @(posedge m_clk) begin
        ic_q <= ic[$clog2(512):0];
        ic_qq <= ic_q;
        patch[i] <= strip_zpad_q[i] ? 'd0 : strip_rd[i][(ic_qq/8)*32 +:32];
    end
end
endgenerate

wire [32*512-1:0] weight_rd;
wire [32*512-1:0] bias_rd;

WEIGHT22 weight (.clk(m_clk),.ra(weight_ra[$clog2(512):0]),.rd(weight_rd));
BIAS22 bias (.clk(m_clk),.rd(bias_rd));

reg [32-1:0] weight_mux [8-1:0];
reg [32-1:0] bias_mux [8-1:0];
generate
for (i=0; i<8; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*64+ochan_sel)*32 +:32];
        bias_mux[i] <= bias_rd[(i*64+ochan_sel)*32 +:32];
    end
end
endgenerate

wire [8*32-1:0] feat [1-1:0];
generate
for (i=0; i<1; i=i+1) begin : ALU_NS
    for (j=0; j<8; j=j+1) begin : ALU_OC
        ALU alu (
        .clk(m_clk),
        .reset(reset),
        .alu_op(alu_op),
        .patch(patch[i]),
        .weight(weight_mux[j]),
        .bias(bias_mux[j]),
        .feat(feat[i][32*j +:32]));
    end
end
endgenerate

always @(posedge m_clk) begin
    m_data <= feat[strip_sel];
end


reg [$clog2(7):0] icount;
reg row_cyc;
always @ (posedge s_clk) begin : S_ICOUNT
    if (reset) begin
        icount <= 'd0;
        row_cyc <= 'b0;
    end
    else if (s_last_q) begin
        if (icount==7-1) begin
            icount <= 'd0;
            if (s_row_q >= 0)
                row_cyc <= 1'b1;
            else
                row_cyc <= 1'b0;
        end
        else begin
            icount <= icount+'d1;
            row_cyc <= 1'b0;
        end
    end
    else begin
        row_cyc <= 1'b0;
    end
end

reg s_row_req;
reg m_row_ack;
reg m_row_req0,m_row_req1,m_row_req;
reg s_row_ack0,s_row_ack1,s_row_ack;
always @(posedge m_clk) begin : M_SYNC
    m_row_req0 <= s_row_req;
    m_row_req1 <= m_row_req0;
    m_row_req <= m_row_req1;
end
always @(posedge s_clk) begin : S_SYNC
    s_row_ack0 <= m_row_ack;
    s_row_ack1 <= s_row_ack0;
    s_row_ack <= s_row_ack1;
end

reg [1:0] s_state;
reg row_go, row_clr;
always @ (posedge s_clk) begin : S_FSM
    if (reset | row_clr)
        row_go <= 1'b0;
    else if (row_cyc)
        row_go <= 1'b1;
    if (reset) begin
        s_state <= 'd0;
        row_clr <= 1'b0;
    end
    else if (s_state=='d0) begin
        if (row_go) begin
            s_state <= 'd1;
            row_clr <= 1'b1;
        end
    end
    else if (s_state=='d1) begin
        row_clr <= 1'b0;
        s_row_req <= 1'b1;
        if (s_row_ack) begin
            s_state <= 'd2;
        end
    end
    else if (s_state=='d2) begin
        s_row_req <= 1'b0;
        if (~s_row_ack) begin
            s_state <= 'd0;
        end
    end
end

reg [4:0] m_state;
reg [3:0] pipe_count;
reg signed [$clog2(1)+1:0] ky;
reg signed [$clog2(1)+1:0] kx;
reg signed [$clog2(7)+1:0] ocol;
reg signed [$clog2(7)+1:0] orow;
reg [$clog2(TDMPAD):0] m_rowwait_count;

always @ (posedge m_clk) begin
strip_zpad_q[0] <= strip_zpad[0];
strip_zpad[0] <= 'b0;
strip_ra[0] <= (((ky+1)+(orow*1))%5)*(7+2)*8+(kx+1)*8+ocol*1*8+(ic%8)+8;
weight_ra <= (ky+1)*1*512+(kx+1)*512+ic;
end

always @(posedge m_clk) begin
    if (reset) begin
        m_state <= 'd0;
        orow <= 'd0;
        m_row_ack <= 1'b0;
        m_valid <= 1'b0;
        m_last <= 1'b0;
    end
    else begin
        case (m_state)
        'd0: begin
            ocol <= 'd0;
            ochan_sel <= 'd0;
            alu_op <= 'd0;
            if (m_row_req) begin
                m_state <= 'd1;
            end
        end
        'd1: begin
            ky <= -1;
            kx <= -1;
            ic <= 0;
            pipe_count <= 'd0;
            alu_op <= 'd1;
            m_state <= 'd2;
        end
        'd2: begin
            alu_op <= 'd2;
            if (ic==511) begin
                if (kx==-1) begin
                    if (ky==-1) begin
                        m_state <= 'd3;
                    end
                    else begin
                        ky <= ky+'d1;
                        kx <= -1;
                        ic <= 'd0;
                    end
                end
                else begin
                    kx <= kx+'d1;
                    ic <= 'd0;
                end
            end
            else begin
                ic <= ic+'d1;
            end
        end
        'd3: begin
            if (pipe_count==2) begin
                alu_op <= 'd4;
                m_state <= 'd4;
            end
            else
                pipe_count <= pipe_count+'d1;
        end
        'd4: begin
            alu_op <= 'd5;
            m_state <= 'd8;
            strip_sel <= 'd0;
        end
        'd8: begin
            alu_op <= 'd5;
            m_state <= 'd9;
            strip_sel <= 'd0;
        end
        'd9: begin
            alu_op <= 'd5;
            m_state <= 'd5;
            strip_sel <= 'd0;
        end
        'd5: begin
            alu_op <= 'd5;
            m_state <= 'd6;
        end
        'd6: begin
            alu_op <= 'd0;
            if (strip_sel<1) begin
                strip_sel <= strip_sel+'d1;
                if (strip_sel*7+ocol < 7) begin
                    m_valid <= 1'b1;
                    m_chan <= ochan_sel;
                    m_col <= strip_sel*7+ocol;
                    m_row <= orow;
                    m_last <= (ochan_sel==64-1);
                end
                else begin
                    m_valid <= 1'b0;
                    m_last <= 1'b0;
                end
            end
            else begin
                m_valid <= 1'b0;
                m_last <= 1'b0;
                if (ochan_sel==64-1) begin
                    ochan_sel <= 'd0;
                    if (ocol==7-1) begin
                        ocol <= 'd0;
                        if (orow==7-1)
                            orow <= 'd0;
                        else
                            orow <= orow+'d1;
                        m_state <= 'd7;
                    end
                    else begin
                        ocol <= ocol+'d1;
                        m_state <= 'd1;
                    end
                end
                else begin
                        m_state <= 'd1;
                    ochan_sel <= ochan_sel+'d1;
                end
            end
       end
       'd7: begin
           m_row_ack <= 1'b1;
           if (~m_row_req) begin
               m_row_ack <= 1'b0;
               m_state<= 'd0;
           end
       end
       'd10: begin
           if (m_rowwait_count==TDMPAD)
                m_state <= 'd1;
           else
               m_rowwait_count <= m_rowwait_count+1;
       end
       endcase
   end
end
endmodule

module BIAS22 (
    input wire clk,
    output reg [512*32-1:0] rd
);
reg [512*32-1:0] spram [0:0];
always @(posedge clk) begin
    rd <= spram['d0];
end
endmodule

module WEIGHT22 (
    input wire clk,
    input wire [$clog2(512):0] ra,
    output reg [512*32-1:0] rd
);
reg [512*32-1:0] spram [0:512-1];
always @(posedge clk) begin
    rd <= spram[ra];
end
endmodule

module STRIP #(parameter SDEPTH=0,SWIDTH=0) (
    input wire wclk,
    input wire rclk,
    input wire reset,
    input wire [$clog2(SDEPTH):0] ra,
    output reg [SWIDTH-1:0] rd,
    input wire wen,
    input wire [$clog2(SDEPTH):0] wa,
    input wire [SWIDTH-1:0] wd
);
(* ramstyle = "no_rw_check" *) reg [SWIDTH-1:0] dpram [0:SDEPTH-1];
always @(posedge rclk) begin
    rd <= dpram[ra];
end
always @(posedge wclk) begin
    if (wen) begin
        dpram[wa] <= wd;
    end
end
endmodule

module ALU (
    input wire clk,
    input wire reset,
    input wire [4:0] alu_op,
    input wire [32-1:0] patch,
    input wire [32-1:0] weight,
    input wire [32-1:0] bias,
    output wire [32-1:0] feat
);
wire [32-1:0] mult_a;
wire [32-1:0] mult_b;
shortreal reg_a;
shortreal reg_b;
shortreal reg_p;
shortreal result;
wire [32-1:0] result_bits;
reg [32-1:0] reg_z;
reg acc1, acc2, acc3, acc4, acc5;
assign mult_a = (alu_op=='d2)||(alu_op=='d1) ? patch : (alu_op=='d4) ? 32'h3f800000 : 32'h00000000;
assign mult_b = (alu_op=='d4) ? bias : weight;
assign result_bits = $shortrealtobits(result);
always @(posedge clk) begin
    acc1 <= (alu_op=='d1) ? 1'b0 : 1'b1;
    acc2 <= acc1;
    acc3 <= acc2;
    acc4 <= acc3;
    acc5 <= acc4;
    if (alu_op != 'd0) begin
        reg_a <= $bitstoshortreal(mult_a);
        reg_b <= $bitstoshortreal(mult_b);
        reg_p <= reg_a * reg_b;
        result <= acc5 ? result + reg_p : reg_p;
        if (alu_op=='d6)
            reg_z <= result_bits[31] ? 32'b0 : result_bits;
        else if (alu_op=='d5)
            reg_z <= result_bits;
    end
end
assign feat = reg_z;
endmodule


