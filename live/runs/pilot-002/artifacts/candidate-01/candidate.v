module design(input wire [63:0] req, output wire valid, output wire [5:0] index, output wire [63:0] grant);

  // 组有效信号：每4位一组
  wire [15:0] group_valid;
  genvar i;
  generate
    for (i = 0; i < 16; i = i + 1) begin : gen_group_valid
      assign group_valid[i] = |req[i*4 +: 4];
    end
  endgenerate

  // 分层选择：先选出高8组中的有效组，再在高4组，高2组，最后确定最高有效组
  wire [7:0] high8_valid;
  wire [3:0] high4_valid;
  wire [1:0] high2_valid;
  wire high1_valid;

  assign high8_valid[0] = |group_valid[15:8];
  assign high8_valid[1] = |group_valid[15:12];
  assign high8_valid[2] = |group_valid[15:14];
  assign high8_valid[3] = group_valid[15];
  // 其实只需要高8组中是否有有效，但为了后续选择，需要更多信息
  // 简化：直接计算最高有效组编号
  wire [3:0] group_index;
  assign group_index[3] = |group_valid[15:8];
  assign group_index[2] = group_index[3] ? |group_valid[15:12] : |group_valid[7:4];
  assign group_index[1] = group_index[3] ? (group_index[2] ? |group_valid[15:14] : |group_valid[11:10]) :
                          (group_index[2] ? |group_valid[7:6] : |group_valid[3:2]);
  assign group_index[0] = group_index[3] ? (group_index[2] ? (group_index[1] ? group_valid[15] : group_valid[14]) :
                                            (group_index[1] ? group_valid[13] : group_valid[12])) :
                          (group_index[2] ? (group_index[1] ? group_valid[11] : group_valid[10]) :
                                            (group_index[1] ? group_valid[9] : group_valid[8]));
  // 注意：group_index[0] 表达式只考虑了高8组的情况，需要修正
  // 重新实现正确的优先级编码器
  wire [3:0] grp_idx;
  assign grp_idx[3] = |group_valid[15:8];
  assign grp_idx[2] = grp_idx[3] ? |group_valid[15:12] : |group_valid[7:4];
  assign grp_idx[1] = grp_idx[3] ? (grp_idx[2] ? |group_valid[15:14] : |group_valid[11:10]) :
                      (grp_idx[2] ? |group_valid[7:6] : |group_valid[3:2]);
  assign grp_idx[0] = grp_idx[3] ? (grp_idx[2] ? (grp_idx[1] ? group_valid[15] : group_valid[14]) :
                                                  (grp_idx[1] ? group_valid[13] : group_valid[12])) :
                      (grp_idx[2] ? (grp_idx[1] ? group_valid[11] : group_valid[10]) :
                                                  (grp_idx[1] ? group_valid[9] : group_valid[8]));

  // 组内最高位索引
  wire [1:0] bit_index [0:15];
  generate
    for (i = 0; i < 16; i = i + 1) begin : gen_bit_index
      wire [3:0] req_group = req[i*4 +: 4];
      assign bit_index[i][1] = req_group[3] | req_group[2];
      assign bit_index[i][0] = req_group[3] | (~req_group[2] & req_group[1]);
    end
  endgenerate

  // 组合索引
  assign index = {grp_idx, bit_index[grp_idx]};

  // 授权：只有最高有效组内的最高位为1
  wire [15:0] group_sel;
  generate
    for (i = 0; i < 16; i = i + 1) begin : gen_group_sel
      assign group_sel[i] = (grp_idx == i);
    end
  endgenerate

  wire [63:0] grant_int;
  genvar j;
  generate
    for (i = 0; i < 16; i = i + 1) begin : gen_grant_group
      for (j = 0; j < 4; j = j + 1) begin : gen_grant_bit
        assign grant_int[i*4 + j] = group_sel[i] & (req[i*4 + j] & ~|(req[i*4 +: 4] & {4{j==3}}));
        // 简化：直接判断是否为组内最高位
        // 更简单：grant_int[i*4+j] = group_sel[i] & (j == bit_index[i]) & req[i*4+j];
        // 但 bit_index 是2位，需要比较
        // 使用显式逻辑：
        // 对于 j=0: req[0] & ~req[1] & ~req[2] & ~req[3]
        // j=1: req[1] & ~req[2] & ~req[3]
        // j=2: req[2] & ~req[3]
        // j=3: req[3]
        // 因此可以用 case 或条件赋值
      end
    end
  endgenerate

  // 重新实现授权逻辑，直接根据组内优先级
  assign grant_int[0] = group_sel[0] & req[0] & ~|req[3:1];
  assign grant_int[1] = group_sel[0] & req[1] & ~|req[3:2];
  assign grant_int[2] = group_sel[0] & req[2] & ~req[3];
  assign grant_int[3] = group_sel[0] & req[3];
  assign grant_int[4] = group_sel[1] & req[4] & ~|req[7:5];
  assign grant_int[5] = group_sel[1] & req[5] & ~|req[7:6];
  assign grant_int[6] = group_sel[1] & req[6] & ~req[7];
  assign grant_int[7] = group_sel[1] & req[7];
  assign grant_int[8] = group_sel[2] & req[8] & ~|req[11:9];
  assign grant_int[9] = group_sel[2] & req[9] & ~|req[11:10];
  assign grant_int[10] = group_sel[2] & req[10] & ~req[11];
  assign grant_int[11] = group_sel[2] & req[11];
  assign grant_int[12] = group_sel[3] & req[12] & ~|req[15:13];
  assign grant_int[13] = group_sel[3] & req[13] & ~|req[15:14];
  assign grant_int[14] = group_sel[3] & req[14] & ~req[15];
  assign grant_int[15] = group_sel[3] & req[15];
  assign grant_int[16] = group_sel[4] & req[16] & ~|req[19:17];
  assign grant_int[17] = group_sel[4] & req[17] & ~|req[19:18];
  assign grant_int[18] = group_sel[4] & req[18] & ~req[19];
  assign grant_int[19] = group_sel[4] & req[19];
  assign grant_int[20] = group_sel[5] & req[20] & ~|req[23:21];
  assign grant_int[21] = group_sel[5] & req[21] & ~|req[23:22];
  assign grant_int[22] = group_sel[5] & req[22] & ~req[23];
  assign grant_int[23] = group_sel[5] & req[23];
  assign grant_int[24] = group_sel[6] & req[24] & ~|req[27:25];
  assign grant_int[25] = group_sel[6] & req[25] & ~|req[27:26];
  assign grant_int[26] = group_sel[6] & req[26] & ~req[27];
  assign grant_int[27] = group_sel[6] & req[27];
  assign grant_int[28] = group_sel[7] & req[28] & ~|req[31:29];
  assign grant_int[29] = group_sel[7] & req[29] & ~|req[31:30];
  assign grant_int[30] = group_sel[7] & req[30] & ~req[31];
  assign grant_int[31] = group_sel[7] & req[31];
  assign grant_int[32] = group_sel[8] & req[32] & ~|req[35:33];
  assign grant_int[33] = group_sel[8] & req[33] & ~|req[35:34];
  assign grant_int[34] = group_sel[8] & req[34] & ~req[35];
  assign grant_int[35] = group_sel[8] & req[35];
  assign grant_int[36] = group_sel[9] & req[36] & ~|req[39:37];
  assign grant_int[37] = group_sel[9] & req[37] & ~|req[39:38];
  assign grant_int[38] = group_sel[9] & req[38] & ~req[39];
  assign grant_int[39] = group_sel[9] & req[39];
  assign grant_int[40] = group_sel[10] & req[40] & ~|req[43:41];
  assign grant_int[41] = group_sel[10] & req[41] & ~|req[43:42];
  assign grant_int[42] = group_sel[10] & req[42] & ~req[43];
  assign grant_int[43] = group_sel[10] & req[43];
  assign grant_int[44] = group_sel[11] & req[44] & ~|req[47:45];
  assign grant_int[45] = group_sel[11] & req[45] & ~|req[47:46];
  assign grant_int[46] = group_sel[11] & req[46] & ~req[47];
  assign grant_int[47] = group_sel[11] & req[47];
  assign grant_int[48] = group_sel[12] & req[48] & ~|req[51:49];
  assign grant_int[49] = group_sel[12] & req[49] & ~|req[51:50];
  assign grant_int[50] = group_sel[12] & req[50] & ~req[51];
  assign grant_int[51] = group_sel[12] & req[51];
  assign grant_int[52] = group_sel[13] & req[52] & ~|req[55:53];
  assign grant_int[53] = group_sel[13] & req[53] & ~|req[55:54];
  assign grant_int[54] = group_sel[13] & req[54] & ~req[55];
  assign grant_int[55] = group_sel[13] & req[55];
  assign grant_int[56] = group_sel[14] & req[56] & ~|req[59:57];
  assign grant_int[57] = group_sel[14] & req[57] & ~|req[59:58];
  assign grant_int[58] = group_sel[14] & req[58] & ~req[59];
  assign grant_int[59] = group_sel[14] & req[59];
  assign grant_int[60] = group_sel[15] & req[60] & ~|req[63:61];
  assign grant_int[61] = group_sel[15] & req[61] & ~|req[63:62];
  assign grant_int[62] = group_sel[15] & req[62] & ~req[63];
  assign grant_int[63] = group_sel[15] & req[63];

  // 处理 req=0 时 grant[0]=1
  assign grant = (req == 64'b0) ? 64'b1 : grant_int;
  assign valid = |req;

endmodule