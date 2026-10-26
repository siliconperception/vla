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


// layer    1 nstrip    4 ocmux    1 m_clk  250000000 req     4592 avail     5000 util   0.9184 nalu     64 wmem      7776 smem    604800 oshape [448, 448, 16]
// layer    2 nstrip   16 ocmux    1 m_clk  250000000 req     4760 avail     5000 util   0.9520 nalu    256 wmem     41472 smem   1720320 oshape [448, 448, 16]
// layer    3 nstrip   16 ocmux    1 m_clk  250000000 req     4760 avail     5000 util   0.9520 nalu    256 wmem     41472 smem   1720320 oshape [448, 448, 16]
// layer    4 nstrip   16 ocmux    4 m_clk  250000000 req     9520 avail    10000 util   0.9520 nalu    128 wmem     82944 smem   1662976 oshape [224, 224, 32]
// layer    5 nstrip   14 ocmux    2 m_clk  250000000 req     9984 avail    10000 util   0.9984 nalu    224 wmem    165888 smem   1806336 oshape [224, 224, 32]
// layer    6 nstrip   14 ocmux    2 m_clk  250000000 req     9984 avail    10000 util   0.9984 nalu    224 wmem    165888 smem   1806336 oshape [224, 224, 32]
// layer    7 nstrip   14 ocmux    8 m_clk  250000000 req    19968 avail    20000 util   0.9984 nalu    168 wmem    497664 smem   1705984 oshape [112, 112, 96]
// layer    8 nstrip    6 ocmux    1 m_clk  250000000 req    16720 avail    20000 util   0.8360 nalu    576 wmem   1492992 smem   2709504 oshape [112, 112, 96]
// layer    9 nstrip    6 ocmux    1 m_clk  250000000 req    16720 avail    20000 util   0.8360 nalu    576 wmem   1492992 smem   2709504 oshape [112, 112, 96]
// layer   10 nstrip    6 ocmux    4 m_clk  250000000 req    35200 avail    40000 util   0.8800 nalu    144 wmem   1492992 smem   2709504 oshape [56, 56, 96]
// layer   11 nstrip    3 ocmux    2 m_clk  250000000 req    33326 avail    40000 util   0.8331 nalu    144 wmem   1492992 smem   1354752 oshape [56, 56, 96]
// layer   12 nstrip    3 ocmux    2 m_clk  250000000 req    33326 avail    40000 util   0.8331 nalu    144 wmem   1492992 smem   1354752 oshape [56, 56, 96]
// layer   13 nstrip    3 ocmux    8 m_clk  250000000 req    70160 avail    80000 util   0.8770 nalu     72 wmem   2985984 smem   1354752 oshape [28, 28, 192]
// layer   14 nstrip    2 ocmux    2 m_clk  250000000 req    48720 avail    80000 util   0.6090 nalu    192 wmem   5971968 smem   1376256 oshape [28, 28, 192]
// layer   15 nstrip    2 ocmux    2 m_clk  250000000 req    48720 avail    80000 util   0.6090 nalu    192 wmem   5971968 smem   1376256 oshape [28, 28, 192]
// layer   16 nstrip    2 ocmux    8 m_clk  250000000 req    97440 avail   160000 util   0.6090 nalu     80 wmem   9953280 smem   1290240 oshape [14, 14, 320]
// layer   17 nstrip    1 ocmux    2 m_clk  250000000 req    80948 avail   160000 util   0.5059 nalu    160 wmem  16588800 smem   1146880 oshape [14, 14, 320]
// layer   18 nstrip    1 ocmux    2 m_clk  250000000 req    80948 avail   160000 util   0.5059 nalu    160 wmem  16588800 smem   1146880 oshape [14, 14, 320]
// layer   19 nstrip    1 ocmux    8 m_clk  250000000 req   161896 avail   320000 util   0.5059 nalu     64 wmem  26542080 smem   1075200 oshape [7, 7, 512]
// layer   20 nstrip    1 ocmux    8 m_clk  250000000 req   258664 avail   320000 util   0.8083 nalu     64 wmem  42467328 smem   1032192 oshape [7, 7, 512]
// layer   21 nstrip    1 ocmux    8 m_clk  250000000 req   258664 avail   320000 util   0.8083 nalu     64 wmem  42467328 smem   1032192 oshape [7, 7, 512]
// layer   22 nstrip    1 ocmux   64 m_clk  250000000 req   234304 avail   320000 util   0.7322 nalu      8 wmem   4718592 smem    737280 oshape [7, 7, 512]

// nalu   3960
// wmem 182724192
// smem 33433216

// op    0 nstrip    4 sdepth   1575 swidth     96 wdepth     27 wwidth    288 bwidth    512
// op    1 nstrip   16 sdepth    210 swidth    512 wdepth    144 wwidth    288 bwidth    512
// op    2 nstrip   16 sdepth    210 swidth    512 wdepth    144 wwidth    288 bwidth    512
// op    3 nstrip   16 sdepth    203 swidth    512 wdepth    144 wwidth    576 bwidth   1024
// op    4 nstrip   14 sdepth    504 swidth    256 wdepth    288 wwidth    576 bwidth   1024
// op    5 nstrip   14 sdepth    252 swidth    512 wdepth    288 wwidth    576 bwidth   1024
// op    6 nstrip   14 sdepth    238 swidth    512 wdepth    288 wwidth   1728 bwidth   3072
// op    7 nstrip    6 sdepth   1176 swidth    384 wdepth    864 wwidth   1728 bwidth   3072
// op    8 nstrip    6 sdepth    147 swidth   3072 wdepth    864 wwidth   1728 bwidth   3072
// op    9 nstrip    6 sdepth    147 swidth   3072 wdepth    864 wwidth   1728 bwidth   3072
// op   10 nstrip    3 sdepth    588 swidth    768 wdepth    864 wwidth   1728 bwidth   3072
// op   11 nstrip    3 sdepth    294 swidth   1536 wdepth    864 wwidth   1728 bwidth   3072
// op   12 nstrip    3 sdepth    294 swidth   1536 wdepth    864 wwidth   3456 bwidth   6144
// op   13 nstrip    2 sdepth    896 swidth    768 wdepth   1728 wwidth   3456 bwidth   6144
// op   14 nstrip    2 sdepth    224 swidth   3072 wdepth   1728 wwidth   3456 bwidth   6144
// op   15 nstrip    2 sdepth    210 swidth   3072 wdepth   1728 wwidth   5760 bwidth  10240
// op   16 nstrip    1 sdepth    896 swidth   1280 wdepth   2880 wwidth   5760 bwidth  10240
// op   17 nstrip    1 sdepth    224 swidth   5120 wdepth   2880 wwidth   5760 bwidth  10240
// op   18 nstrip    1 sdepth    210 swidth   5120 wdepth   2880 wwidth   9216 bwidth  16384
// op   19 nstrip    1 sdepth    504 swidth   2048 wdepth   4608 wwidth   9216 bwidth  16384
// op   20 nstrip    1 sdepth    504 swidth   2048 wdepth   4608 wwidth   9216 bwidth  16384
// op   21 nstrip    1 sdepth    360 swidth   2048 wdepth    512 wwidth   9216 bwidth  16384

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

// ninst      1 wdepth     27 wwidth    288
// ninst      2 wdepth    144 wwidth    288
// ninst      1 wdepth    144 wwidth    576
// ninst      2 wdepth    288 wwidth    576
// ninst      1 wdepth    288 wwidth   1728
// ninst      5 wdepth    864 wwidth   1728
// ninst      1 wdepth    864 wwidth   3456
// ninst      1 wdepth    512 wwidth   9216
// ninst      2 wdepth   1728 wwidth   3456
// ninst      1 wdepth   1728 wwidth   5760
// ninst      2 wdepth   2880 wwidth   5760
// ninst      1 wdepth   2880 wwidth   9216
// ninst      2 wdepth   4608 wwidth   9216

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

wire [18*16-1:0] weight_rd;
wire [32*16-1:0] bias_rd;

WEIGHT1 weight (.clk(m_clk),.ra(weight_ra[$clog2(27):0]),.rd(weight_rd));
BIAS1 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*18 +:18];
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
    output wire [16*32-1:0] rd
);
bias_L01 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT1 (
    input wire clk,
    input wire [$clog2(27):0] ra,
    output wire [16*18-1:0] rd
);
weight_L01O00 u0 (
    .q(rd[0*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O01 u1 (
    .q(rd[1*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O02 u2 (
    .q(rd[2*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O03 u3 (
    .q(rd[3*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O04 u4 (
    .q(rd[4*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O05 u5 (
    .q(rd[5*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O06 u6 (
    .q(rd[6*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O07 u7 (
    .q(rd[7*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O08 u8 (
    .q(rd[8*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O09 u9 (
    .q(rd[9*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O10 u10 (
    .q(rd[10*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O11 u11 (
    .q(rd[11*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O12 u12 (
    .q(rd[12*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O13 u13 (
    .q(rd[13*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O14 u14 (
    .q(rd[14*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L01O15 u15 (
    .q(rd[15*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
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

wire [18*16-1:0] weight_rd;
wire [32*16-1:0] bias_rd;

WEIGHT2 weight (.clk(m_clk),.ra(weight_ra[$clog2(144):0]),.rd(weight_rd));
BIAS2 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*18 +:18];
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
    output wire [16*32-1:0] rd
);
bias_L02 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT2 (
    input wire clk,
    input wire [$clog2(144):0] ra,
    output wire [16*18-1:0] rd
);
weight_L02O00 u0 (
    .q(rd[0*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O01 u1 (
    .q(rd[1*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O02 u2 (
    .q(rd[2*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O03 u3 (
    .q(rd[3*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O04 u4 (
    .q(rd[4*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O05 u5 (
    .q(rd[5*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O06 u6 (
    .q(rd[6*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O07 u7 (
    .q(rd[7*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O08 u8 (
    .q(rd[8*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O09 u9 (
    .q(rd[9*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O10 u10 (
    .q(rd[10*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O11 u11 (
    .q(rd[11*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O12 u12 (
    .q(rd[12*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O13 u13 (
    .q(rd[13*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O14 u14 (
    .q(rd[14*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L02O15 u15 (
    .q(rd[15*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
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

wire [18*16-1:0] weight_rd;
wire [32*16-1:0] bias_rd;

WEIGHT3 weight (.clk(m_clk),.ra(weight_ra[$clog2(144):0]),.rd(weight_rd));
BIAS3 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*18 +:18];
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
    output wire [16*32-1:0] rd
);
bias_L03 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT3 (
    input wire clk,
    input wire [$clog2(144):0] ra,
    output wire [16*18-1:0] rd
);
weight_L03O00 u0 (
    .q(rd[0*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O01 u1 (
    .q(rd[1*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O02 u2 (
    .q(rd[2*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O03 u3 (
    .q(rd[3*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O04 u4 (
    .q(rd[4*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O05 u5 (
    .q(rd[5*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O06 u6 (
    .q(rd[6*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O07 u7 (
    .q(rd[7*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O08 u8 (
    .q(rd[8*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O09 u9 (
    .q(rd[9*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O10 u10 (
    .q(rd[10*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O11 u11 (
    .q(rd[11*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O12 u12 (
    .q(rd[12*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O13 u13 (
    .q(rd[13*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O14 u14 (
    .q(rd[14*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L03O15 u15 (
    .q(rd[15*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
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

wire [18*32-1:0] weight_rd;
wire [32*32-1:0] bias_rd;

WEIGHT4 weight (.clk(m_clk),.ra(weight_ra[$clog2(144):0]),.rd(weight_rd));
BIAS4 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [8-1:0];
reg [32-1:0] bias_mux [8-1:0];
generate
for (i=0; i<8; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*4+ochan_sel)*18 +:18];
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
    output wire [32*32-1:0] rd
);
bias_L04 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT4 (
    input wire clk,
    input wire [$clog2(144):0] ra,
    output wire [32*18-1:0] rd
);
weight_L04O00 u0 (
    .q(rd[0*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L04O01 u1 (
    .q(rd[1*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L04O02 u2 (
    .q(rd[2*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L04O03 u3 (
    .q(rd[3*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L04O04 u4 (
    .q(rd[4*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L04O05 u5 (
    .q(rd[5*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L04O06 u6 (
    .q(rd[6*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L04O07 u7 (
    .q(rd[7*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
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

wire [18*32-1:0] weight_rd;
wire [32*32-1:0] bias_rd;

WEIGHT5 weight (.clk(m_clk),.ra(weight_ra[$clog2(288):0]),.rd(weight_rd));
BIAS5 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*18 +:18];
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
    output wire [32*32-1:0] rd
);
bias_L05 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT5 (
    input wire clk,
    input wire [$clog2(288):0] ra,
    output wire [32*18-1:0] rd
);
weight_L05O00 u0 (
    .q(rd[0*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O01 u1 (
    .q(rd[1*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O02 u2 (
    .q(rd[2*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O03 u3 (
    .q(rd[3*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O04 u4 (
    .q(rd[4*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O05 u5 (
    .q(rd[5*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O06 u6 (
    .q(rd[6*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O07 u7 (
    .q(rd[7*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O08 u8 (
    .q(rd[8*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O09 u9 (
    .q(rd[9*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O10 u10 (
    .q(rd[10*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O11 u11 (
    .q(rd[11*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O12 u12 (
    .q(rd[12*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O13 u13 (
    .q(rd[13*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O14 u14 (
    .q(rd[14*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L05O15 u15 (
    .q(rd[15*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
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

wire [18*32-1:0] weight_rd;
wire [32*32-1:0] bias_rd;

WEIGHT6 weight (.clk(m_clk),.ra(weight_ra[$clog2(288):0]),.rd(weight_rd));
BIAS6 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [16-1:0];
reg [32-1:0] bias_mux [16-1:0];
generate
for (i=0; i<16; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*18 +:18];
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
    output wire [32*32-1:0] rd
);
bias_L06 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT6 (
    input wire clk,
    input wire [$clog2(288):0] ra,
    output wire [32*18-1:0] rd
);
weight_L06O00 u0 (
    .q(rd[0*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O01 u1 (
    .q(rd[1*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O02 u2 (
    .q(rd[2*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O03 u3 (
    .q(rd[3*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O04 u4 (
    .q(rd[4*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O05 u5 (
    .q(rd[5*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O06 u6 (
    .q(rd[6*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O07 u7 (
    .q(rd[7*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O08 u8 (
    .q(rd[8*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O09 u9 (
    .q(rd[9*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O10 u10 (
    .q(rd[10*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O11 u11 (
    .q(rd[11*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O12 u12 (
    .q(rd[12*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O13 u13 (
    .q(rd[13*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O14 u14 (
    .q(rd[14*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L06O15 u15 (
    .q(rd[15*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
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

wire [18*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT7 weight (.clk(m_clk),.ra(weight_ra[$clog2(288):0]),.rd(weight_rd));
BIAS7 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [12-1:0];
reg [32-1:0] bias_mux [12-1:0];
generate
for (i=0; i<12; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*18 +:18];
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
    output wire [96*32-1:0] rd
);
bias_L07 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT7 (
    input wire clk,
    input wire [$clog2(288):0] ra,
    output wire [96*18-1:0] rd
);
weight_L07O00 u0 (
    .q(rd[0*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O01 u1 (
    .q(rd[1*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O02 u2 (
    .q(rd[2*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O03 u3 (
    .q(rd[3*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O04 u4 (
    .q(rd[4*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O05 u5 (
    .q(rd[5*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O06 u6 (
    .q(rd[6*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O07 u7 (
    .q(rd[7*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O08 u8 (
    .q(rd[8*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O09 u9 (
    .q(rd[9*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O10 u10 (
    .q(rd[10*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L07O11 u11 (
    .q(rd[11*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
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

wire [18*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT8 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS8 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [96-1:0];
reg [32-1:0] bias_mux [96-1:0];
generate
for (i=0; i<96; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*18 +:18];
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
    output wire [96*32-1:0] rd
);
bias_L08 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT8 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output wire [96*18-1:0] rd
);
weight_L08O00 u0 (
    .q(rd[0*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O01 u1 (
    .q(rd[1*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O02 u2 (
    .q(rd[2*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O03 u3 (
    .q(rd[3*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O04 u4 (
    .q(rd[4*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O05 u5 (
    .q(rd[5*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O06 u6 (
    .q(rd[6*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O07 u7 (
    .q(rd[7*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O08 u8 (
    .q(rd[8*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O09 u9 (
    .q(rd[9*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O10 u10 (
    .q(rd[10*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O11 u11 (
    .q(rd[11*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O12 u12 (
    .q(rd[12*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O13 u13 (
    .q(rd[13*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O14 u14 (
    .q(rd[14*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O15 u15 (
    .q(rd[15*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O16 u16 (
    .q(rd[16*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O17 u17 (
    .q(rd[17*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O18 u18 (
    .q(rd[18*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O19 u19 (
    .q(rd[19*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O20 u20 (
    .q(rd[20*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O21 u21 (
    .q(rd[21*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O22 u22 (
    .q(rd[22*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O23 u23 (
    .q(rd[23*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O24 u24 (
    .q(rd[24*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O25 u25 (
    .q(rd[25*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O26 u26 (
    .q(rd[26*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O27 u27 (
    .q(rd[27*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O28 u28 (
    .q(rd[28*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O29 u29 (
    .q(rd[29*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O30 u30 (
    .q(rd[30*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O31 u31 (
    .q(rd[31*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O32 u32 (
    .q(rd[32*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O33 u33 (
    .q(rd[33*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O34 u34 (
    .q(rd[34*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O35 u35 (
    .q(rd[35*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O36 u36 (
    .q(rd[36*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O37 u37 (
    .q(rd[37*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O38 u38 (
    .q(rd[38*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O39 u39 (
    .q(rd[39*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O40 u40 (
    .q(rd[40*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O41 u41 (
    .q(rd[41*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O42 u42 (
    .q(rd[42*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O43 u43 (
    .q(rd[43*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O44 u44 (
    .q(rd[44*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O45 u45 (
    .q(rd[45*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O46 u46 (
    .q(rd[46*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O47 u47 (
    .q(rd[47*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O48 u48 (
    .q(rd[48*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O49 u49 (
    .q(rd[49*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O50 u50 (
    .q(rd[50*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O51 u51 (
    .q(rd[51*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O52 u52 (
    .q(rd[52*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O53 u53 (
    .q(rd[53*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O54 u54 (
    .q(rd[54*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O55 u55 (
    .q(rd[55*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O56 u56 (
    .q(rd[56*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O57 u57 (
    .q(rd[57*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O58 u58 (
    .q(rd[58*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O59 u59 (
    .q(rd[59*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O60 u60 (
    .q(rd[60*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O61 u61 (
    .q(rd[61*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O62 u62 (
    .q(rd[62*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O63 u63 (
    .q(rd[63*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O64 u64 (
    .q(rd[64*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O65 u65 (
    .q(rd[65*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O66 u66 (
    .q(rd[66*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O67 u67 (
    .q(rd[67*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O68 u68 (
    .q(rd[68*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O69 u69 (
    .q(rd[69*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O70 u70 (
    .q(rd[70*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O71 u71 (
    .q(rd[71*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O72 u72 (
    .q(rd[72*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O73 u73 (
    .q(rd[73*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O74 u74 (
    .q(rd[74*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O75 u75 (
    .q(rd[75*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O76 u76 (
    .q(rd[76*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O77 u77 (
    .q(rd[77*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O78 u78 (
    .q(rd[78*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O79 u79 (
    .q(rd[79*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O80 u80 (
    .q(rd[80*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O81 u81 (
    .q(rd[81*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O82 u82 (
    .q(rd[82*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O83 u83 (
    .q(rd[83*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O84 u84 (
    .q(rd[84*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O85 u85 (
    .q(rd[85*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O86 u86 (
    .q(rd[86*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O87 u87 (
    .q(rd[87*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O88 u88 (
    .q(rd[88*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O89 u89 (
    .q(rd[89*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O90 u90 (
    .q(rd[90*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O91 u91 (
    .q(rd[91*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O92 u92 (
    .q(rd[92*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O93 u93 (
    .q(rd[93*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O94 u94 (
    .q(rd[94*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L08O95 u95 (
    .q(rd[95*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
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

wire [18*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT9 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS9 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [96-1:0];
reg [32-1:0] bias_mux [96-1:0];
generate
for (i=0; i<96; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*1+ochan_sel)*18 +:18];
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
    output wire [96*32-1:0] rd
);
bias_L09 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT9 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output wire [96*18-1:0] rd
);
weight_L09O00 u0 (
    .q(rd[0*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O01 u1 (
    .q(rd[1*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O02 u2 (
    .q(rd[2*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O03 u3 (
    .q(rd[3*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O04 u4 (
    .q(rd[4*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O05 u5 (
    .q(rd[5*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O06 u6 (
    .q(rd[6*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O07 u7 (
    .q(rd[7*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O08 u8 (
    .q(rd[8*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O09 u9 (
    .q(rd[9*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O10 u10 (
    .q(rd[10*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O11 u11 (
    .q(rd[11*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O12 u12 (
    .q(rd[12*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O13 u13 (
    .q(rd[13*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O14 u14 (
    .q(rd[14*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O15 u15 (
    .q(rd[15*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O16 u16 (
    .q(rd[16*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O17 u17 (
    .q(rd[17*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O18 u18 (
    .q(rd[18*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O19 u19 (
    .q(rd[19*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O20 u20 (
    .q(rd[20*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O21 u21 (
    .q(rd[21*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O22 u22 (
    .q(rd[22*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O23 u23 (
    .q(rd[23*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O24 u24 (
    .q(rd[24*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O25 u25 (
    .q(rd[25*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O26 u26 (
    .q(rd[26*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O27 u27 (
    .q(rd[27*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O28 u28 (
    .q(rd[28*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O29 u29 (
    .q(rd[29*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O30 u30 (
    .q(rd[30*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O31 u31 (
    .q(rd[31*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O32 u32 (
    .q(rd[32*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O33 u33 (
    .q(rd[33*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O34 u34 (
    .q(rd[34*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O35 u35 (
    .q(rd[35*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O36 u36 (
    .q(rd[36*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O37 u37 (
    .q(rd[37*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O38 u38 (
    .q(rd[38*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O39 u39 (
    .q(rd[39*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O40 u40 (
    .q(rd[40*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O41 u41 (
    .q(rd[41*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O42 u42 (
    .q(rd[42*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O43 u43 (
    .q(rd[43*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O44 u44 (
    .q(rd[44*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O45 u45 (
    .q(rd[45*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O46 u46 (
    .q(rd[46*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O47 u47 (
    .q(rd[47*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O48 u48 (
    .q(rd[48*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O49 u49 (
    .q(rd[49*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O50 u50 (
    .q(rd[50*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O51 u51 (
    .q(rd[51*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O52 u52 (
    .q(rd[52*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O53 u53 (
    .q(rd[53*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O54 u54 (
    .q(rd[54*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O55 u55 (
    .q(rd[55*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O56 u56 (
    .q(rd[56*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O57 u57 (
    .q(rd[57*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O58 u58 (
    .q(rd[58*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O59 u59 (
    .q(rd[59*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O60 u60 (
    .q(rd[60*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O61 u61 (
    .q(rd[61*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O62 u62 (
    .q(rd[62*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O63 u63 (
    .q(rd[63*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O64 u64 (
    .q(rd[64*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O65 u65 (
    .q(rd[65*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O66 u66 (
    .q(rd[66*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O67 u67 (
    .q(rd[67*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O68 u68 (
    .q(rd[68*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O69 u69 (
    .q(rd[69*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O70 u70 (
    .q(rd[70*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O71 u71 (
    .q(rd[71*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O72 u72 (
    .q(rd[72*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O73 u73 (
    .q(rd[73*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O74 u74 (
    .q(rd[74*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O75 u75 (
    .q(rd[75*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O76 u76 (
    .q(rd[76*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O77 u77 (
    .q(rd[77*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O78 u78 (
    .q(rd[78*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O79 u79 (
    .q(rd[79*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O80 u80 (
    .q(rd[80*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O81 u81 (
    .q(rd[81*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O82 u82 (
    .q(rd[82*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O83 u83 (
    .q(rd[83*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O84 u84 (
    .q(rd[84*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O85 u85 (
    .q(rd[85*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O86 u86 (
    .q(rd[86*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O87 u87 (
    .q(rd[87*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O88 u88 (
    .q(rd[88*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O89 u89 (
    .q(rd[89*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O90 u90 (
    .q(rd[90*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O91 u91 (
    .q(rd[91*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O92 u92 (
    .q(rd[92*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O93 u93 (
    .q(rd[93*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O94 u94 (
    .q(rd[94*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
weight_L09O95 u95 (
    .q(rd[95*18*1 +:18*1]),
    .address(ra),
    .clock(clk)
);
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

wire [18*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT10 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS10 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [24-1:0];
reg [32-1:0] bias_mux [24-1:0];
generate
for (i=0; i<24; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*4+ochan_sel)*18 +:18];
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
    output wire [96*32-1:0] rd
);
bias_L10 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT10 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output wire [96*18-1:0] rd
);
weight_L10O00 u0 (
    .q(rd[0*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O01 u1 (
    .q(rd[1*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O02 u2 (
    .q(rd[2*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O03 u3 (
    .q(rd[3*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O04 u4 (
    .q(rd[4*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O05 u5 (
    .q(rd[5*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O06 u6 (
    .q(rd[6*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O07 u7 (
    .q(rd[7*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O08 u8 (
    .q(rd[8*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O09 u9 (
    .q(rd[9*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O10 u10 (
    .q(rd[10*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O11 u11 (
    .q(rd[11*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O12 u12 (
    .q(rd[12*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O13 u13 (
    .q(rd[13*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O14 u14 (
    .q(rd[14*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O15 u15 (
    .q(rd[15*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O16 u16 (
    .q(rd[16*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O17 u17 (
    .q(rd[17*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O18 u18 (
    .q(rd[18*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O19 u19 (
    .q(rd[19*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O20 u20 (
    .q(rd[20*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O21 u21 (
    .q(rd[21*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O22 u22 (
    .q(rd[22*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
weight_L10O23 u23 (
    .q(rd[23*18*4 +:18*4]),
    .address(ra),
    .clock(clk)
);
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

wire [18*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT11 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS11 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [48-1:0];
reg [32-1:0] bias_mux [48-1:0];
generate
for (i=0; i<48; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*18 +:18];
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
    output wire [96*32-1:0] rd
);
bias_L11 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT11 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output wire [96*18-1:0] rd
);
weight_L11O00 u0 (
    .q(rd[0*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O01 u1 (
    .q(rd[1*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O02 u2 (
    .q(rd[2*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O03 u3 (
    .q(rd[3*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O04 u4 (
    .q(rd[4*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O05 u5 (
    .q(rd[5*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O06 u6 (
    .q(rd[6*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O07 u7 (
    .q(rd[7*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O08 u8 (
    .q(rd[8*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O09 u9 (
    .q(rd[9*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O10 u10 (
    .q(rd[10*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O11 u11 (
    .q(rd[11*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O12 u12 (
    .q(rd[12*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O13 u13 (
    .q(rd[13*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O14 u14 (
    .q(rd[14*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O15 u15 (
    .q(rd[15*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O16 u16 (
    .q(rd[16*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O17 u17 (
    .q(rd[17*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O18 u18 (
    .q(rd[18*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O19 u19 (
    .q(rd[19*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O20 u20 (
    .q(rd[20*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O21 u21 (
    .q(rd[21*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O22 u22 (
    .q(rd[22*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O23 u23 (
    .q(rd[23*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O24 u24 (
    .q(rd[24*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O25 u25 (
    .q(rd[25*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O26 u26 (
    .q(rd[26*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O27 u27 (
    .q(rd[27*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O28 u28 (
    .q(rd[28*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O29 u29 (
    .q(rd[29*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O30 u30 (
    .q(rd[30*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O31 u31 (
    .q(rd[31*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O32 u32 (
    .q(rd[32*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O33 u33 (
    .q(rd[33*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O34 u34 (
    .q(rd[34*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O35 u35 (
    .q(rd[35*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O36 u36 (
    .q(rd[36*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O37 u37 (
    .q(rd[37*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O38 u38 (
    .q(rd[38*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O39 u39 (
    .q(rd[39*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O40 u40 (
    .q(rd[40*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O41 u41 (
    .q(rd[41*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O42 u42 (
    .q(rd[42*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O43 u43 (
    .q(rd[43*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O44 u44 (
    .q(rd[44*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O45 u45 (
    .q(rd[45*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O46 u46 (
    .q(rd[46*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L11O47 u47 (
    .q(rd[47*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
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

wire [18*96-1:0] weight_rd;
wire [32*96-1:0] bias_rd;

WEIGHT12 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS12 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [48-1:0];
reg [32-1:0] bias_mux [48-1:0];
generate
for (i=0; i<48; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*18 +:18];
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
    output wire [96*32-1:0] rd
);
bias_L12 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT12 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output wire [96*18-1:0] rd
);
weight_L12O00 u0 (
    .q(rd[0*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O01 u1 (
    .q(rd[1*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O02 u2 (
    .q(rd[2*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O03 u3 (
    .q(rd[3*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O04 u4 (
    .q(rd[4*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O05 u5 (
    .q(rd[5*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O06 u6 (
    .q(rd[6*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O07 u7 (
    .q(rd[7*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O08 u8 (
    .q(rd[8*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O09 u9 (
    .q(rd[9*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O10 u10 (
    .q(rd[10*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O11 u11 (
    .q(rd[11*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O12 u12 (
    .q(rd[12*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O13 u13 (
    .q(rd[13*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O14 u14 (
    .q(rd[14*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O15 u15 (
    .q(rd[15*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O16 u16 (
    .q(rd[16*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O17 u17 (
    .q(rd[17*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O18 u18 (
    .q(rd[18*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O19 u19 (
    .q(rd[19*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O20 u20 (
    .q(rd[20*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O21 u21 (
    .q(rd[21*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O22 u22 (
    .q(rd[22*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O23 u23 (
    .q(rd[23*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O24 u24 (
    .q(rd[24*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O25 u25 (
    .q(rd[25*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O26 u26 (
    .q(rd[26*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O27 u27 (
    .q(rd[27*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O28 u28 (
    .q(rd[28*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O29 u29 (
    .q(rd[29*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O30 u30 (
    .q(rd[30*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O31 u31 (
    .q(rd[31*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O32 u32 (
    .q(rd[32*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O33 u33 (
    .q(rd[33*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O34 u34 (
    .q(rd[34*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O35 u35 (
    .q(rd[35*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O36 u36 (
    .q(rd[36*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O37 u37 (
    .q(rd[37*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O38 u38 (
    .q(rd[38*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O39 u39 (
    .q(rd[39*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O40 u40 (
    .q(rd[40*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O41 u41 (
    .q(rd[41*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O42 u42 (
    .q(rd[42*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O43 u43 (
    .q(rd[43*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O44 u44 (
    .q(rd[44*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O45 u45 (
    .q(rd[45*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O46 u46 (
    .q(rd[46*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L12O47 u47 (
    .q(rd[47*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
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

wire [18*192-1:0] weight_rd;
wire [32*192-1:0] bias_rd;

WEIGHT13 weight (.clk(m_clk),.ra(weight_ra[$clog2(864):0]),.rd(weight_rd));
BIAS13 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [24-1:0];
reg [32-1:0] bias_mux [24-1:0];
generate
for (i=0; i<24; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*18 +:18];
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
    output wire [192*32-1:0] rd
);
bias_L13 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT13 (
    input wire clk,
    input wire [$clog2(864):0] ra,
    output wire [192*18-1:0] rd
);
weight_L13O00 u0 (
    .q(rd[0*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O01 u1 (
    .q(rd[1*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O02 u2 (
    .q(rd[2*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O03 u3 (
    .q(rd[3*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O04 u4 (
    .q(rd[4*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O05 u5 (
    .q(rd[5*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O06 u6 (
    .q(rd[6*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O07 u7 (
    .q(rd[7*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O08 u8 (
    .q(rd[8*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O09 u9 (
    .q(rd[9*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O10 u10 (
    .q(rd[10*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O11 u11 (
    .q(rd[11*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O12 u12 (
    .q(rd[12*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O13 u13 (
    .q(rd[13*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O14 u14 (
    .q(rd[14*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O15 u15 (
    .q(rd[15*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O16 u16 (
    .q(rd[16*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O17 u17 (
    .q(rd[17*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O18 u18 (
    .q(rd[18*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O19 u19 (
    .q(rd[19*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O20 u20 (
    .q(rd[20*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O21 u21 (
    .q(rd[21*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O22 u22 (
    .q(rd[22*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L13O23 u23 (
    .q(rd[23*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
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

wire [18*192-1:0] weight_rd;
wire [32*192-1:0] bias_rd;

WEIGHT14 weight (.clk(m_clk),.ra(weight_ra[$clog2(1728):0]),.rd(weight_rd));
BIAS14 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [96-1:0];
reg [32-1:0] bias_mux [96-1:0];
generate
for (i=0; i<96; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*18 +:18];
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
    output wire [192*32-1:0] rd
);
bias_L14 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT14 (
    input wire clk,
    input wire [$clog2(1728):0] ra,
    output wire [192*18-1:0] rd
);
weight_L14O00 u0 (
    .q(rd[0*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O01 u1 (
    .q(rd[1*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O02 u2 (
    .q(rd[2*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O03 u3 (
    .q(rd[3*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O04 u4 (
    .q(rd[4*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O05 u5 (
    .q(rd[5*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O06 u6 (
    .q(rd[6*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O07 u7 (
    .q(rd[7*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O08 u8 (
    .q(rd[8*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O09 u9 (
    .q(rd[9*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O10 u10 (
    .q(rd[10*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O11 u11 (
    .q(rd[11*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O12 u12 (
    .q(rd[12*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O13 u13 (
    .q(rd[13*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O14 u14 (
    .q(rd[14*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O15 u15 (
    .q(rd[15*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O16 u16 (
    .q(rd[16*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O17 u17 (
    .q(rd[17*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O18 u18 (
    .q(rd[18*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O19 u19 (
    .q(rd[19*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O20 u20 (
    .q(rd[20*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O21 u21 (
    .q(rd[21*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O22 u22 (
    .q(rd[22*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O23 u23 (
    .q(rd[23*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O24 u24 (
    .q(rd[24*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O25 u25 (
    .q(rd[25*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O26 u26 (
    .q(rd[26*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O27 u27 (
    .q(rd[27*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O28 u28 (
    .q(rd[28*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O29 u29 (
    .q(rd[29*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O30 u30 (
    .q(rd[30*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O31 u31 (
    .q(rd[31*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O32 u32 (
    .q(rd[32*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O33 u33 (
    .q(rd[33*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O34 u34 (
    .q(rd[34*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O35 u35 (
    .q(rd[35*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O36 u36 (
    .q(rd[36*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O37 u37 (
    .q(rd[37*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O38 u38 (
    .q(rd[38*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O39 u39 (
    .q(rd[39*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O40 u40 (
    .q(rd[40*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O41 u41 (
    .q(rd[41*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O42 u42 (
    .q(rd[42*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O43 u43 (
    .q(rd[43*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O44 u44 (
    .q(rd[44*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O45 u45 (
    .q(rd[45*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O46 u46 (
    .q(rd[46*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O47 u47 (
    .q(rd[47*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O48 u48 (
    .q(rd[48*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O49 u49 (
    .q(rd[49*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O50 u50 (
    .q(rd[50*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O51 u51 (
    .q(rd[51*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O52 u52 (
    .q(rd[52*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O53 u53 (
    .q(rd[53*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O54 u54 (
    .q(rd[54*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O55 u55 (
    .q(rd[55*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O56 u56 (
    .q(rd[56*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O57 u57 (
    .q(rd[57*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O58 u58 (
    .q(rd[58*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O59 u59 (
    .q(rd[59*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O60 u60 (
    .q(rd[60*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O61 u61 (
    .q(rd[61*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O62 u62 (
    .q(rd[62*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O63 u63 (
    .q(rd[63*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O64 u64 (
    .q(rd[64*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O65 u65 (
    .q(rd[65*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O66 u66 (
    .q(rd[66*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O67 u67 (
    .q(rd[67*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O68 u68 (
    .q(rd[68*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O69 u69 (
    .q(rd[69*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O70 u70 (
    .q(rd[70*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O71 u71 (
    .q(rd[71*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O72 u72 (
    .q(rd[72*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O73 u73 (
    .q(rd[73*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O74 u74 (
    .q(rd[74*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O75 u75 (
    .q(rd[75*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O76 u76 (
    .q(rd[76*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O77 u77 (
    .q(rd[77*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O78 u78 (
    .q(rd[78*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O79 u79 (
    .q(rd[79*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O80 u80 (
    .q(rd[80*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O81 u81 (
    .q(rd[81*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O82 u82 (
    .q(rd[82*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O83 u83 (
    .q(rd[83*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O84 u84 (
    .q(rd[84*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O85 u85 (
    .q(rd[85*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O86 u86 (
    .q(rd[86*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O87 u87 (
    .q(rd[87*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O88 u88 (
    .q(rd[88*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O89 u89 (
    .q(rd[89*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O90 u90 (
    .q(rd[90*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O91 u91 (
    .q(rd[91*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O92 u92 (
    .q(rd[92*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O93 u93 (
    .q(rd[93*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O94 u94 (
    .q(rd[94*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L14O95 u95 (
    .q(rd[95*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
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

wire [18*192-1:0] weight_rd;
wire [32*192-1:0] bias_rd;

WEIGHT15 weight (.clk(m_clk),.ra(weight_ra[$clog2(1728):0]),.rd(weight_rd));
BIAS15 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [96-1:0];
reg [32-1:0] bias_mux [96-1:0];
generate
for (i=0; i<96; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*18 +:18];
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
    output wire [192*32-1:0] rd
);
bias_L15 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT15 (
    input wire clk,
    input wire [$clog2(1728):0] ra,
    output wire [192*18-1:0] rd
);
weight_L15O00 u0 (
    .q(rd[0*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O01 u1 (
    .q(rd[1*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O02 u2 (
    .q(rd[2*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O03 u3 (
    .q(rd[3*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O04 u4 (
    .q(rd[4*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O05 u5 (
    .q(rd[5*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O06 u6 (
    .q(rd[6*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O07 u7 (
    .q(rd[7*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O08 u8 (
    .q(rd[8*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O09 u9 (
    .q(rd[9*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O10 u10 (
    .q(rd[10*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O11 u11 (
    .q(rd[11*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O12 u12 (
    .q(rd[12*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O13 u13 (
    .q(rd[13*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O14 u14 (
    .q(rd[14*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O15 u15 (
    .q(rd[15*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O16 u16 (
    .q(rd[16*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O17 u17 (
    .q(rd[17*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O18 u18 (
    .q(rd[18*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O19 u19 (
    .q(rd[19*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O20 u20 (
    .q(rd[20*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O21 u21 (
    .q(rd[21*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O22 u22 (
    .q(rd[22*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O23 u23 (
    .q(rd[23*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O24 u24 (
    .q(rd[24*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O25 u25 (
    .q(rd[25*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O26 u26 (
    .q(rd[26*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O27 u27 (
    .q(rd[27*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O28 u28 (
    .q(rd[28*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O29 u29 (
    .q(rd[29*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O30 u30 (
    .q(rd[30*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O31 u31 (
    .q(rd[31*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O32 u32 (
    .q(rd[32*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O33 u33 (
    .q(rd[33*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O34 u34 (
    .q(rd[34*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O35 u35 (
    .q(rd[35*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O36 u36 (
    .q(rd[36*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O37 u37 (
    .q(rd[37*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O38 u38 (
    .q(rd[38*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O39 u39 (
    .q(rd[39*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O40 u40 (
    .q(rd[40*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O41 u41 (
    .q(rd[41*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O42 u42 (
    .q(rd[42*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O43 u43 (
    .q(rd[43*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O44 u44 (
    .q(rd[44*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O45 u45 (
    .q(rd[45*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O46 u46 (
    .q(rd[46*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O47 u47 (
    .q(rd[47*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O48 u48 (
    .q(rd[48*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O49 u49 (
    .q(rd[49*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O50 u50 (
    .q(rd[50*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O51 u51 (
    .q(rd[51*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O52 u52 (
    .q(rd[52*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O53 u53 (
    .q(rd[53*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O54 u54 (
    .q(rd[54*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O55 u55 (
    .q(rd[55*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O56 u56 (
    .q(rd[56*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O57 u57 (
    .q(rd[57*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O58 u58 (
    .q(rd[58*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O59 u59 (
    .q(rd[59*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O60 u60 (
    .q(rd[60*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O61 u61 (
    .q(rd[61*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O62 u62 (
    .q(rd[62*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O63 u63 (
    .q(rd[63*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O64 u64 (
    .q(rd[64*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O65 u65 (
    .q(rd[65*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O66 u66 (
    .q(rd[66*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O67 u67 (
    .q(rd[67*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O68 u68 (
    .q(rd[68*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O69 u69 (
    .q(rd[69*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O70 u70 (
    .q(rd[70*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O71 u71 (
    .q(rd[71*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O72 u72 (
    .q(rd[72*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O73 u73 (
    .q(rd[73*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O74 u74 (
    .q(rd[74*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O75 u75 (
    .q(rd[75*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O76 u76 (
    .q(rd[76*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O77 u77 (
    .q(rd[77*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O78 u78 (
    .q(rd[78*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O79 u79 (
    .q(rd[79*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O80 u80 (
    .q(rd[80*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O81 u81 (
    .q(rd[81*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O82 u82 (
    .q(rd[82*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O83 u83 (
    .q(rd[83*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O84 u84 (
    .q(rd[84*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O85 u85 (
    .q(rd[85*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O86 u86 (
    .q(rd[86*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O87 u87 (
    .q(rd[87*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O88 u88 (
    .q(rd[88*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O89 u89 (
    .q(rd[89*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O90 u90 (
    .q(rd[90*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O91 u91 (
    .q(rd[91*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O92 u92 (
    .q(rd[92*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O93 u93 (
    .q(rd[93*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O94 u94 (
    .q(rd[94*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L15O95 u95 (
    .q(rd[95*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
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

wire [18*320-1:0] weight_rd;
wire [32*320-1:0] bias_rd;

WEIGHT16 weight (.clk(m_clk),.ra(weight_ra[$clog2(1728):0]),.rd(weight_rd));
BIAS16 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [40-1:0];
reg [32-1:0] bias_mux [40-1:0];
generate
for (i=0; i<40; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*18 +:18];
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
    output wire [320*32-1:0] rd
);
bias_L16 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT16 (
    input wire clk,
    input wire [$clog2(1728):0] ra,
    output wire [320*18-1:0] rd
);
weight_L16O00 u0 (
    .q(rd[0*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O01 u1 (
    .q(rd[1*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O02 u2 (
    .q(rd[2*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O03 u3 (
    .q(rd[3*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O04 u4 (
    .q(rd[4*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O05 u5 (
    .q(rd[5*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O06 u6 (
    .q(rd[6*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O07 u7 (
    .q(rd[7*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O08 u8 (
    .q(rd[8*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O09 u9 (
    .q(rd[9*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O10 u10 (
    .q(rd[10*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O11 u11 (
    .q(rd[11*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O12 u12 (
    .q(rd[12*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O13 u13 (
    .q(rd[13*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O14 u14 (
    .q(rd[14*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O15 u15 (
    .q(rd[15*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O16 u16 (
    .q(rd[16*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O17 u17 (
    .q(rd[17*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O18 u18 (
    .q(rd[18*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O19 u19 (
    .q(rd[19*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O20 u20 (
    .q(rd[20*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O21 u21 (
    .q(rd[21*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O22 u22 (
    .q(rd[22*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O23 u23 (
    .q(rd[23*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O24 u24 (
    .q(rd[24*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O25 u25 (
    .q(rd[25*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O26 u26 (
    .q(rd[26*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O27 u27 (
    .q(rd[27*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O28 u28 (
    .q(rd[28*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O29 u29 (
    .q(rd[29*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O30 u30 (
    .q(rd[30*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O31 u31 (
    .q(rd[31*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O32 u32 (
    .q(rd[32*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O33 u33 (
    .q(rd[33*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O34 u34 (
    .q(rd[34*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O35 u35 (
    .q(rd[35*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O36 u36 (
    .q(rd[36*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O37 u37 (
    .q(rd[37*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O38 u38 (
    .q(rd[38*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L16O39 u39 (
    .q(rd[39*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
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

wire [18*320-1:0] weight_rd;
wire [32*320-1:0] bias_rd;

WEIGHT17 weight (.clk(m_clk),.ra(weight_ra[$clog2(2880):0]),.rd(weight_rd));
BIAS17 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [160-1:0];
reg [32-1:0] bias_mux [160-1:0];
generate
for (i=0; i<160; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*18 +:18];
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
    output wire [320*32-1:0] rd
);
bias_L17 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT17 (
    input wire clk,
    input wire [$clog2(2880):0] ra,
    output wire [320*18-1:0] rd
);
weight_L17O00 u0 (
    .q(rd[0*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O01 u1 (
    .q(rd[1*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O02 u2 (
    .q(rd[2*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O03 u3 (
    .q(rd[3*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O04 u4 (
    .q(rd[4*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O05 u5 (
    .q(rd[5*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O06 u6 (
    .q(rd[6*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O07 u7 (
    .q(rd[7*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O08 u8 (
    .q(rd[8*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O09 u9 (
    .q(rd[9*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O10 u10 (
    .q(rd[10*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O11 u11 (
    .q(rd[11*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O12 u12 (
    .q(rd[12*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O13 u13 (
    .q(rd[13*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O14 u14 (
    .q(rd[14*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O15 u15 (
    .q(rd[15*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O16 u16 (
    .q(rd[16*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O17 u17 (
    .q(rd[17*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O18 u18 (
    .q(rd[18*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O19 u19 (
    .q(rd[19*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O20 u20 (
    .q(rd[20*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O21 u21 (
    .q(rd[21*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O22 u22 (
    .q(rd[22*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O23 u23 (
    .q(rd[23*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O24 u24 (
    .q(rd[24*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O25 u25 (
    .q(rd[25*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O26 u26 (
    .q(rd[26*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O27 u27 (
    .q(rd[27*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O28 u28 (
    .q(rd[28*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O29 u29 (
    .q(rd[29*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O30 u30 (
    .q(rd[30*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O31 u31 (
    .q(rd[31*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O32 u32 (
    .q(rd[32*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O33 u33 (
    .q(rd[33*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O34 u34 (
    .q(rd[34*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O35 u35 (
    .q(rd[35*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O36 u36 (
    .q(rd[36*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O37 u37 (
    .q(rd[37*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O38 u38 (
    .q(rd[38*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O39 u39 (
    .q(rd[39*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O40 u40 (
    .q(rd[40*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O41 u41 (
    .q(rd[41*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O42 u42 (
    .q(rd[42*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O43 u43 (
    .q(rd[43*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O44 u44 (
    .q(rd[44*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O45 u45 (
    .q(rd[45*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O46 u46 (
    .q(rd[46*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O47 u47 (
    .q(rd[47*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O48 u48 (
    .q(rd[48*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O49 u49 (
    .q(rd[49*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O50 u50 (
    .q(rd[50*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O51 u51 (
    .q(rd[51*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O52 u52 (
    .q(rd[52*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O53 u53 (
    .q(rd[53*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O54 u54 (
    .q(rd[54*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O55 u55 (
    .q(rd[55*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O56 u56 (
    .q(rd[56*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O57 u57 (
    .q(rd[57*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O58 u58 (
    .q(rd[58*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O59 u59 (
    .q(rd[59*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O60 u60 (
    .q(rd[60*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O61 u61 (
    .q(rd[61*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O62 u62 (
    .q(rd[62*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O63 u63 (
    .q(rd[63*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O64 u64 (
    .q(rd[64*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O65 u65 (
    .q(rd[65*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O66 u66 (
    .q(rd[66*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O67 u67 (
    .q(rd[67*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O68 u68 (
    .q(rd[68*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O69 u69 (
    .q(rd[69*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O70 u70 (
    .q(rd[70*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O71 u71 (
    .q(rd[71*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O72 u72 (
    .q(rd[72*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O73 u73 (
    .q(rd[73*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O74 u74 (
    .q(rd[74*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O75 u75 (
    .q(rd[75*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O76 u76 (
    .q(rd[76*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O77 u77 (
    .q(rd[77*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O78 u78 (
    .q(rd[78*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O79 u79 (
    .q(rd[79*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O80 u80 (
    .q(rd[80*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O81 u81 (
    .q(rd[81*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O82 u82 (
    .q(rd[82*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O83 u83 (
    .q(rd[83*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O84 u84 (
    .q(rd[84*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O85 u85 (
    .q(rd[85*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O86 u86 (
    .q(rd[86*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O87 u87 (
    .q(rd[87*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O88 u88 (
    .q(rd[88*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O89 u89 (
    .q(rd[89*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O90 u90 (
    .q(rd[90*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O91 u91 (
    .q(rd[91*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O92 u92 (
    .q(rd[92*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O93 u93 (
    .q(rd[93*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O94 u94 (
    .q(rd[94*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O95 u95 (
    .q(rd[95*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O96 u96 (
    .q(rd[96*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O97 u97 (
    .q(rd[97*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O98 u98 (
    .q(rd[98*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O99 u99 (
    .q(rd[99*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O100 u100 (
    .q(rd[100*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O101 u101 (
    .q(rd[101*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O102 u102 (
    .q(rd[102*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O103 u103 (
    .q(rd[103*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O104 u104 (
    .q(rd[104*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O105 u105 (
    .q(rd[105*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O106 u106 (
    .q(rd[106*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O107 u107 (
    .q(rd[107*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O108 u108 (
    .q(rd[108*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O109 u109 (
    .q(rd[109*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O110 u110 (
    .q(rd[110*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O111 u111 (
    .q(rd[111*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O112 u112 (
    .q(rd[112*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O113 u113 (
    .q(rd[113*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O114 u114 (
    .q(rd[114*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O115 u115 (
    .q(rd[115*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O116 u116 (
    .q(rd[116*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O117 u117 (
    .q(rd[117*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O118 u118 (
    .q(rd[118*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O119 u119 (
    .q(rd[119*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O120 u120 (
    .q(rd[120*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O121 u121 (
    .q(rd[121*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O122 u122 (
    .q(rd[122*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O123 u123 (
    .q(rd[123*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O124 u124 (
    .q(rd[124*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O125 u125 (
    .q(rd[125*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O126 u126 (
    .q(rd[126*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O127 u127 (
    .q(rd[127*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O128 u128 (
    .q(rd[128*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O129 u129 (
    .q(rd[129*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O130 u130 (
    .q(rd[130*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O131 u131 (
    .q(rd[131*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O132 u132 (
    .q(rd[132*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O133 u133 (
    .q(rd[133*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O134 u134 (
    .q(rd[134*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O135 u135 (
    .q(rd[135*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O136 u136 (
    .q(rd[136*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O137 u137 (
    .q(rd[137*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O138 u138 (
    .q(rd[138*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O139 u139 (
    .q(rd[139*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O140 u140 (
    .q(rd[140*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O141 u141 (
    .q(rd[141*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O142 u142 (
    .q(rd[142*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O143 u143 (
    .q(rd[143*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O144 u144 (
    .q(rd[144*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O145 u145 (
    .q(rd[145*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O146 u146 (
    .q(rd[146*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O147 u147 (
    .q(rd[147*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O148 u148 (
    .q(rd[148*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O149 u149 (
    .q(rd[149*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O150 u150 (
    .q(rd[150*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O151 u151 (
    .q(rd[151*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O152 u152 (
    .q(rd[152*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O153 u153 (
    .q(rd[153*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O154 u154 (
    .q(rd[154*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O155 u155 (
    .q(rd[155*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O156 u156 (
    .q(rd[156*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O157 u157 (
    .q(rd[157*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O158 u158 (
    .q(rd[158*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L17O159 u159 (
    .q(rd[159*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
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

wire [18*320-1:0] weight_rd;
wire [32*320-1:0] bias_rd;

WEIGHT18 weight (.clk(m_clk),.ra(weight_ra[$clog2(2880):0]),.rd(weight_rd));
BIAS18 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [160-1:0];
reg [32-1:0] bias_mux [160-1:0];
generate
for (i=0; i<160; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*2+ochan_sel)*18 +:18];
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
    output wire [320*32-1:0] rd
);
bias_L18 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT18 (
    input wire clk,
    input wire [$clog2(2880):0] ra,
    output wire [320*18-1:0] rd
);
weight_L18O00 u0 (
    .q(rd[0*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O01 u1 (
    .q(rd[1*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O02 u2 (
    .q(rd[2*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O03 u3 (
    .q(rd[3*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O04 u4 (
    .q(rd[4*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O05 u5 (
    .q(rd[5*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O06 u6 (
    .q(rd[6*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O07 u7 (
    .q(rd[7*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O08 u8 (
    .q(rd[8*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O09 u9 (
    .q(rd[9*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O10 u10 (
    .q(rd[10*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O11 u11 (
    .q(rd[11*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O12 u12 (
    .q(rd[12*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O13 u13 (
    .q(rd[13*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O14 u14 (
    .q(rd[14*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O15 u15 (
    .q(rd[15*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O16 u16 (
    .q(rd[16*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O17 u17 (
    .q(rd[17*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O18 u18 (
    .q(rd[18*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O19 u19 (
    .q(rd[19*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O20 u20 (
    .q(rd[20*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O21 u21 (
    .q(rd[21*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O22 u22 (
    .q(rd[22*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O23 u23 (
    .q(rd[23*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O24 u24 (
    .q(rd[24*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O25 u25 (
    .q(rd[25*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O26 u26 (
    .q(rd[26*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O27 u27 (
    .q(rd[27*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O28 u28 (
    .q(rd[28*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O29 u29 (
    .q(rd[29*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O30 u30 (
    .q(rd[30*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O31 u31 (
    .q(rd[31*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O32 u32 (
    .q(rd[32*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O33 u33 (
    .q(rd[33*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O34 u34 (
    .q(rd[34*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O35 u35 (
    .q(rd[35*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O36 u36 (
    .q(rd[36*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O37 u37 (
    .q(rd[37*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O38 u38 (
    .q(rd[38*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O39 u39 (
    .q(rd[39*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O40 u40 (
    .q(rd[40*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O41 u41 (
    .q(rd[41*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O42 u42 (
    .q(rd[42*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O43 u43 (
    .q(rd[43*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O44 u44 (
    .q(rd[44*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O45 u45 (
    .q(rd[45*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O46 u46 (
    .q(rd[46*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O47 u47 (
    .q(rd[47*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O48 u48 (
    .q(rd[48*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O49 u49 (
    .q(rd[49*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O50 u50 (
    .q(rd[50*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O51 u51 (
    .q(rd[51*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O52 u52 (
    .q(rd[52*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O53 u53 (
    .q(rd[53*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O54 u54 (
    .q(rd[54*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O55 u55 (
    .q(rd[55*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O56 u56 (
    .q(rd[56*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O57 u57 (
    .q(rd[57*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O58 u58 (
    .q(rd[58*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O59 u59 (
    .q(rd[59*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O60 u60 (
    .q(rd[60*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O61 u61 (
    .q(rd[61*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O62 u62 (
    .q(rd[62*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O63 u63 (
    .q(rd[63*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O64 u64 (
    .q(rd[64*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O65 u65 (
    .q(rd[65*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O66 u66 (
    .q(rd[66*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O67 u67 (
    .q(rd[67*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O68 u68 (
    .q(rd[68*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O69 u69 (
    .q(rd[69*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O70 u70 (
    .q(rd[70*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O71 u71 (
    .q(rd[71*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O72 u72 (
    .q(rd[72*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O73 u73 (
    .q(rd[73*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O74 u74 (
    .q(rd[74*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O75 u75 (
    .q(rd[75*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O76 u76 (
    .q(rd[76*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O77 u77 (
    .q(rd[77*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O78 u78 (
    .q(rd[78*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O79 u79 (
    .q(rd[79*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O80 u80 (
    .q(rd[80*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O81 u81 (
    .q(rd[81*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O82 u82 (
    .q(rd[82*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O83 u83 (
    .q(rd[83*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O84 u84 (
    .q(rd[84*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O85 u85 (
    .q(rd[85*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O86 u86 (
    .q(rd[86*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O87 u87 (
    .q(rd[87*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O88 u88 (
    .q(rd[88*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O89 u89 (
    .q(rd[89*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O90 u90 (
    .q(rd[90*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O91 u91 (
    .q(rd[91*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O92 u92 (
    .q(rd[92*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O93 u93 (
    .q(rd[93*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O94 u94 (
    .q(rd[94*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O95 u95 (
    .q(rd[95*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O96 u96 (
    .q(rd[96*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O97 u97 (
    .q(rd[97*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O98 u98 (
    .q(rd[98*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O99 u99 (
    .q(rd[99*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O100 u100 (
    .q(rd[100*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O101 u101 (
    .q(rd[101*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O102 u102 (
    .q(rd[102*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O103 u103 (
    .q(rd[103*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O104 u104 (
    .q(rd[104*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O105 u105 (
    .q(rd[105*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O106 u106 (
    .q(rd[106*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O107 u107 (
    .q(rd[107*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O108 u108 (
    .q(rd[108*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O109 u109 (
    .q(rd[109*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O110 u110 (
    .q(rd[110*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O111 u111 (
    .q(rd[111*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O112 u112 (
    .q(rd[112*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O113 u113 (
    .q(rd[113*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O114 u114 (
    .q(rd[114*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O115 u115 (
    .q(rd[115*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O116 u116 (
    .q(rd[116*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O117 u117 (
    .q(rd[117*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O118 u118 (
    .q(rd[118*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O119 u119 (
    .q(rd[119*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O120 u120 (
    .q(rd[120*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O121 u121 (
    .q(rd[121*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O122 u122 (
    .q(rd[122*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O123 u123 (
    .q(rd[123*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O124 u124 (
    .q(rd[124*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O125 u125 (
    .q(rd[125*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O126 u126 (
    .q(rd[126*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O127 u127 (
    .q(rd[127*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O128 u128 (
    .q(rd[128*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O129 u129 (
    .q(rd[129*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O130 u130 (
    .q(rd[130*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O131 u131 (
    .q(rd[131*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O132 u132 (
    .q(rd[132*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O133 u133 (
    .q(rd[133*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O134 u134 (
    .q(rd[134*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O135 u135 (
    .q(rd[135*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O136 u136 (
    .q(rd[136*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O137 u137 (
    .q(rd[137*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O138 u138 (
    .q(rd[138*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O139 u139 (
    .q(rd[139*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O140 u140 (
    .q(rd[140*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O141 u141 (
    .q(rd[141*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O142 u142 (
    .q(rd[142*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O143 u143 (
    .q(rd[143*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O144 u144 (
    .q(rd[144*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O145 u145 (
    .q(rd[145*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O146 u146 (
    .q(rd[146*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O147 u147 (
    .q(rd[147*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O148 u148 (
    .q(rd[148*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O149 u149 (
    .q(rd[149*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O150 u150 (
    .q(rd[150*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O151 u151 (
    .q(rd[151*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O152 u152 (
    .q(rd[152*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O153 u153 (
    .q(rd[153*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O154 u154 (
    .q(rd[154*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O155 u155 (
    .q(rd[155*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O156 u156 (
    .q(rd[156*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O157 u157 (
    .q(rd[157*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O158 u158 (
    .q(rd[158*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
weight_L18O159 u159 (
    .q(rd[159*18*2 +:18*2]),
    .address(ra),
    .clock(clk)
);
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

wire [18*512-1:0] weight_rd;
wire [32*512-1:0] bias_rd;

WEIGHT19 weight (.clk(m_clk),.ra(weight_ra[$clog2(2880):0]),.rd(weight_rd));
BIAS19 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [64-1:0];
reg [32-1:0] bias_mux [64-1:0];
generate
for (i=0; i<64; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*18 +:18];
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
    output wire [512*32-1:0] rd
);
bias_L19 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT19 (
    input wire clk,
    input wire [$clog2(2880):0] ra,
    output wire [512*18-1:0] rd
);
weight_L19O00 u0 (
    .q(rd[0*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O01 u1 (
    .q(rd[1*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O02 u2 (
    .q(rd[2*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O03 u3 (
    .q(rd[3*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O04 u4 (
    .q(rd[4*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O05 u5 (
    .q(rd[5*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O06 u6 (
    .q(rd[6*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O07 u7 (
    .q(rd[7*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O08 u8 (
    .q(rd[8*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O09 u9 (
    .q(rd[9*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O10 u10 (
    .q(rd[10*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O11 u11 (
    .q(rd[11*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O12 u12 (
    .q(rd[12*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O13 u13 (
    .q(rd[13*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O14 u14 (
    .q(rd[14*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O15 u15 (
    .q(rd[15*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O16 u16 (
    .q(rd[16*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O17 u17 (
    .q(rd[17*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O18 u18 (
    .q(rd[18*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O19 u19 (
    .q(rd[19*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O20 u20 (
    .q(rd[20*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O21 u21 (
    .q(rd[21*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O22 u22 (
    .q(rd[22*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O23 u23 (
    .q(rd[23*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O24 u24 (
    .q(rd[24*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O25 u25 (
    .q(rd[25*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O26 u26 (
    .q(rd[26*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O27 u27 (
    .q(rd[27*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O28 u28 (
    .q(rd[28*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O29 u29 (
    .q(rd[29*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O30 u30 (
    .q(rd[30*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O31 u31 (
    .q(rd[31*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O32 u32 (
    .q(rd[32*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O33 u33 (
    .q(rd[33*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O34 u34 (
    .q(rd[34*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O35 u35 (
    .q(rd[35*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O36 u36 (
    .q(rd[36*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O37 u37 (
    .q(rd[37*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O38 u38 (
    .q(rd[38*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O39 u39 (
    .q(rd[39*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O40 u40 (
    .q(rd[40*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O41 u41 (
    .q(rd[41*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O42 u42 (
    .q(rd[42*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O43 u43 (
    .q(rd[43*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O44 u44 (
    .q(rd[44*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O45 u45 (
    .q(rd[45*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O46 u46 (
    .q(rd[46*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O47 u47 (
    .q(rd[47*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O48 u48 (
    .q(rd[48*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O49 u49 (
    .q(rd[49*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O50 u50 (
    .q(rd[50*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O51 u51 (
    .q(rd[51*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O52 u52 (
    .q(rd[52*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O53 u53 (
    .q(rd[53*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O54 u54 (
    .q(rd[54*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O55 u55 (
    .q(rd[55*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O56 u56 (
    .q(rd[56*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O57 u57 (
    .q(rd[57*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O58 u58 (
    .q(rd[58*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O59 u59 (
    .q(rd[59*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O60 u60 (
    .q(rd[60*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O61 u61 (
    .q(rd[61*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O62 u62 (
    .q(rd[62*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L19O63 u63 (
    .q(rd[63*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
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

wire [18*512-1:0] weight_rd;
wire [32*512-1:0] bias_rd;

WEIGHT20 weight (.clk(m_clk),.ra(weight_ra[$clog2(4608):0]),.rd(weight_rd));
BIAS20 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [64-1:0];
reg [32-1:0] bias_mux [64-1:0];
generate
for (i=0; i<64; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*18 +:18];
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
    output wire [512*32-1:0] rd
);
bias_L20 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT20 (
    input wire clk,
    input wire [$clog2(4608):0] ra,
    output wire [512*18-1:0] rd
);
weight_L20O00 u0 (
    .q(rd[0*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O01 u1 (
    .q(rd[1*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O02 u2 (
    .q(rd[2*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O03 u3 (
    .q(rd[3*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O04 u4 (
    .q(rd[4*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O05 u5 (
    .q(rd[5*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O06 u6 (
    .q(rd[6*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O07 u7 (
    .q(rd[7*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O08 u8 (
    .q(rd[8*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O09 u9 (
    .q(rd[9*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O10 u10 (
    .q(rd[10*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O11 u11 (
    .q(rd[11*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O12 u12 (
    .q(rd[12*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O13 u13 (
    .q(rd[13*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O14 u14 (
    .q(rd[14*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O15 u15 (
    .q(rd[15*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O16 u16 (
    .q(rd[16*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O17 u17 (
    .q(rd[17*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O18 u18 (
    .q(rd[18*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O19 u19 (
    .q(rd[19*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O20 u20 (
    .q(rd[20*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O21 u21 (
    .q(rd[21*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O22 u22 (
    .q(rd[22*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O23 u23 (
    .q(rd[23*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O24 u24 (
    .q(rd[24*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O25 u25 (
    .q(rd[25*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O26 u26 (
    .q(rd[26*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O27 u27 (
    .q(rd[27*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O28 u28 (
    .q(rd[28*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O29 u29 (
    .q(rd[29*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O30 u30 (
    .q(rd[30*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O31 u31 (
    .q(rd[31*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O32 u32 (
    .q(rd[32*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O33 u33 (
    .q(rd[33*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O34 u34 (
    .q(rd[34*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O35 u35 (
    .q(rd[35*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O36 u36 (
    .q(rd[36*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O37 u37 (
    .q(rd[37*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O38 u38 (
    .q(rd[38*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O39 u39 (
    .q(rd[39*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O40 u40 (
    .q(rd[40*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O41 u41 (
    .q(rd[41*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O42 u42 (
    .q(rd[42*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O43 u43 (
    .q(rd[43*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O44 u44 (
    .q(rd[44*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O45 u45 (
    .q(rd[45*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O46 u46 (
    .q(rd[46*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O47 u47 (
    .q(rd[47*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O48 u48 (
    .q(rd[48*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O49 u49 (
    .q(rd[49*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O50 u50 (
    .q(rd[50*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O51 u51 (
    .q(rd[51*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O52 u52 (
    .q(rd[52*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O53 u53 (
    .q(rd[53*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O54 u54 (
    .q(rd[54*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O55 u55 (
    .q(rd[55*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O56 u56 (
    .q(rd[56*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O57 u57 (
    .q(rd[57*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O58 u58 (
    .q(rd[58*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O59 u59 (
    .q(rd[59*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O60 u60 (
    .q(rd[60*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O61 u61 (
    .q(rd[61*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O62 u62 (
    .q(rd[62*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L20O63 u63 (
    .q(rd[63*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
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

wire [18*512-1:0] weight_rd;
wire [32*512-1:0] bias_rd;

WEIGHT21 weight (.clk(m_clk),.ra(weight_ra[$clog2(4608):0]),.rd(weight_rd));
BIAS21 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [64-1:0];
reg [32-1:0] bias_mux [64-1:0];
generate
for (i=0; i<64; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*8+ochan_sel)*18 +:18];
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
    output wire [512*32-1:0] rd
);
bias_L21 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT21 (
    input wire clk,
    input wire [$clog2(4608):0] ra,
    output wire [512*18-1:0] rd
);
weight_L21O00 u0 (
    .q(rd[0*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O01 u1 (
    .q(rd[1*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O02 u2 (
    .q(rd[2*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O03 u3 (
    .q(rd[3*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O04 u4 (
    .q(rd[4*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O05 u5 (
    .q(rd[5*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O06 u6 (
    .q(rd[6*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O07 u7 (
    .q(rd[7*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O08 u8 (
    .q(rd[8*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O09 u9 (
    .q(rd[9*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O10 u10 (
    .q(rd[10*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O11 u11 (
    .q(rd[11*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O12 u12 (
    .q(rd[12*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O13 u13 (
    .q(rd[13*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O14 u14 (
    .q(rd[14*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O15 u15 (
    .q(rd[15*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O16 u16 (
    .q(rd[16*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O17 u17 (
    .q(rd[17*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O18 u18 (
    .q(rd[18*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O19 u19 (
    .q(rd[19*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O20 u20 (
    .q(rd[20*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O21 u21 (
    .q(rd[21*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O22 u22 (
    .q(rd[22*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O23 u23 (
    .q(rd[23*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O24 u24 (
    .q(rd[24*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O25 u25 (
    .q(rd[25*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O26 u26 (
    .q(rd[26*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O27 u27 (
    .q(rd[27*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O28 u28 (
    .q(rd[28*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O29 u29 (
    .q(rd[29*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O30 u30 (
    .q(rd[30*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O31 u31 (
    .q(rd[31*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O32 u32 (
    .q(rd[32*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O33 u33 (
    .q(rd[33*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O34 u34 (
    .q(rd[34*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O35 u35 (
    .q(rd[35*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O36 u36 (
    .q(rd[36*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O37 u37 (
    .q(rd[37*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O38 u38 (
    .q(rd[38*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O39 u39 (
    .q(rd[39*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O40 u40 (
    .q(rd[40*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O41 u41 (
    .q(rd[41*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O42 u42 (
    .q(rd[42*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O43 u43 (
    .q(rd[43*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O44 u44 (
    .q(rd[44*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O45 u45 (
    .q(rd[45*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O46 u46 (
    .q(rd[46*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O47 u47 (
    .q(rd[47*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O48 u48 (
    .q(rd[48*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O49 u49 (
    .q(rd[49*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O50 u50 (
    .q(rd[50*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O51 u51 (
    .q(rd[51*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O52 u52 (
    .q(rd[52*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O53 u53 (
    .q(rd[53*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O54 u54 (
    .q(rd[54*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O55 u55 (
    .q(rd[55*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O56 u56 (
    .q(rd[56*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O57 u57 (
    .q(rd[57*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O58 u58 (
    .q(rd[58*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O59 u59 (
    .q(rd[59*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O60 u60 (
    .q(rd[60*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O61 u61 (
    .q(rd[61*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O62 u62 (
    .q(rd[62*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
weight_L21O63 u63 (
    .q(rd[63*18*8 +:18*8]),
    .address(ra),
    .clock(clk)
);
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

wire [18*512-1:0] weight_rd;
wire [32*512-1:0] bias_rd;

WEIGHT22 weight (.clk(m_clk),.ra(weight_ra[$clog2(512):0]),.rd(weight_rd));
BIAS22 bias (.clk(m_clk),.rd(bias_rd));

reg [18-1:0] weight_mux [8-1:0];
reg [32-1:0] bias_mux [8-1:0];
generate
for (i=0; i<8; i=i+1) begin : WEIGHT_MUX
    always @(posedge m_clk) begin
        weight_mux[i] <= weight_rd[(i*64+ochan_sel)*18 +:18];
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
    output wire [512*32-1:0] rd
);
bias_L22 u0 (
    .q(rd),
    .address('d0),
    .clock(clk)
);
endmodule

module WEIGHT22 (
    input wire clk,
    input wire [$clog2(512):0] ra,
    output wire [512*18-1:0] rd
);
weight_L22O00 u0 (
    .q(rd[0*18*64 +:18*64]),
    .address(ra),
    .clock(clk)
);
weight_L22O01 u1 (
    .q(rd[1*18*64 +:18*64]),
    .address(ra),
    .clock(clk)
);
weight_L22O02 u2 (
    .q(rd[2*18*64 +:18*64]),
    .address(ra),
    .clock(clk)
);
weight_L22O03 u3 (
    .q(rd[3*18*64 +:18*64]),
    .address(ra),
    .clock(clk)
);
weight_L22O04 u4 (
    .q(rd[4*18*64 +:18*64]),
    .address(ra),
    .clock(clk)
);
weight_L22O05 u5 (
    .q(rd[5*18*64 +:18*64]),
    .address(ra),
    .clock(clk)
);
weight_L22O06 u6 (
    .q(rd[6*18*64 +:18*64]),
    .address(ra),
    .clock(clk)
);
weight_L22O07 u7 (
    .q(rd[7*18*64 +:18*64]),
    .address(ra),
    .clock(clk)
);
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
    input wire [18-1:0] weight,
    input wire [32-1:0] bias,
    output wire [32-1:0] feat
);

wire acc;
wire [2:0] ena;
wire [32-1:0] mult_a;
wire [32-1:0] mult_b;
wire [32-1:0] result;
reg [32-1:0] reg_z;
mac_fp32 u0 (
    .accumulate  (acc),  //   input,   width = 1,  accumulate.accumulate
    .fp32_mult_a (mult_a), //   input,  width = 32, fp32_mult_a.fp32_mult_a
    .fp32_mult_b (mult_b), //   input,  width = 32, fp32_mult_b.fp32_mult_b
    .clk         (clk),         //   input,   width = 1,         clk.clk
    .ena         (ena),         //   input,   width = 3,         ena.ena
    .fp32_result (result)  //  output,  width = 32, fp32_result.fp32_result
);
assign mult_a = (alu_op=='d2)||(alu_op=='d1) ? patch : (alu_op=='d4) ? 32'h3f800000 : 32'h00000000;
assign mult_b = (alu_op=='d4) ? bias : {weight,14'b0};
assign ena = 3'b111;
assign acc = (alu_op=='d1) ? 1'b0 : 1'b1;
always @(posedge clk) begin
    if (alu_op=='d6)
        reg_z <= result[31] ? 32'b0 : result;
    else if (alu_op=='d5)
        reg_z <= result;
end
assign feat = reg_z;
endmodule


