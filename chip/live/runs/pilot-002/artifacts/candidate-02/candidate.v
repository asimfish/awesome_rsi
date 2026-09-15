module design(input wire [63:0] req, output wire valid, output wire [5:0] index, output wire [63:0] grant);

  // Group valid signals: each group of 4 bits
  wire [15:0] gv;
  assign gv[0] = |req[3:0];
  assign gv[1] = |req[7:4];
  assign gv[2] = |req[11:8];
  assign gv[3] = |req[15:12];
  assign gv[4] = |req[19:16];
  assign gv[5] = |req[23:20];
  assign gv[6] = |req[27:24];
  assign gv[7] = |req[31:28];
  assign gv[8] = |req[35:32];
  assign gv[9] = |req[39:36];
  assign gv[10] = |req[43:40];
  assign gv[11] = |req[47:44];
  assign gv[12] = |req[51:48];
  assign gv[13] = |req[55:52];
  assign gv[14] = |req[59:56];
  assign gv[15] = |req[63:60];

  // Group select: win[g] is 1 if group g is the highest group with any request
  wire [15:0] win;
  assign win[0] = gv[0] & ~(|gv[15:1]);
  assign win[1] = gv[1] & ~(|gv[15:2]);
  assign win[2] = gv[2] & ~(|gv[15:3]);
  assign win[3] = gv[3] & ~(|gv[15:4]);
  assign win[4] = gv[4] & ~(|gv[15:5]);
  assign win[5] = gv[5] & ~(|gv[15:6]);
  assign win[6] = gv[6] & ~(|gv[15:7]);
  assign win[7] = gv[7] & ~(|gv[15:8]);
  assign win[8] = gv[8] & ~(|gv[15:9]);
  assign win[9] = gv[9] & ~(|gv[15:10]);
  assign win[10] = gv[10] & ~(|gv[15:11]);
  assign win[11] = gv[11] & ~(|gv[15:12]);
  assign win[12] = gv[12] & ~(|gv[15:13]);
  assign win[13] = gv[13] & ~(|gv[15:14]);
  assign win[14] = gv[14] & ~(|gv[15:15]);
  assign win[15] = gv[15];

  // Grant generation: for each bit, grant[i] = win[group] & req[i] & ~(|req[group_base+3 : i+1])
  // This ensures only the highest set bit within the winning group is granted.
  // We use explicit assignments for clarity and to avoid generate loops with variable part-selects.
  assign grant[0] = ~(|req[63:1]); // only when req==0
  assign grant[1] = win[0] & req[1] & ~(|req[3:2]);
  assign grant[2] = win[0] & req[2] & ~(|req[3:3]);
  assign grant[3] = win[0] & req[3];
  assign grant[4] = win[1] & req[4] & ~(|req[7:5]);
  assign grant[5] = win[1] & req[5] & ~(|req[7:6]);
  assign grant[6] = win[1] & req[6] & ~(|req[7:7]);
  assign grant[7] = win[1] & req[7];
  assign grant[8] = win[2] & req[8] & ~(|req[11:9]);
  assign grant[9] = win[2] & req[9] & ~(|req[11:10]);
  assign grant[10] = win[2] & req[10] & ~(|req[11:11]);
  assign grant[11] = win[2] & req[11];
  assign grant[12] = win[3] & req[12] & ~(|req[15:13]);
  assign grant[13] = win[3] & req[13] & ~(|req[15:14]);
  assign grant[14] = win[3] & req[14] & ~(|req[15:15]);
  assign grant[15] = win[3] & req[15];
  assign grant[16] = win[4] & req[16] & ~(|req[19:17]);
  assign grant[17] = win[4] & req[17] & ~(|req[19:18]);
  assign grant[18] = win[4] & req[18] & ~(|req[19:19]);
  assign grant[19] = win[4] & req[19];
  assign grant[20] = win[5] & req[20] & ~(|req[23:21]);
  assign grant[21] = win[5] & req[21] & ~(|req[23:22]);
  assign grant[22] = win[5] & req[22] & ~(|req[23:23]);
  assign grant[23] = win[5] & req[23];
  assign grant[24] = win[6] & req[24] & ~(|req[27:25]);
  assign grant[25] = win[6] & req[25] & ~(|req[27:26]);
  assign grant[26] = win[6] & req[26] & ~(|req[27:27]);
  assign grant[27] = win[6] & req[27];
  assign grant[28] = win[7] & req[28] & ~(|req[31:29]);
  assign grant[29] = win[7] & req[29] & ~(|req[31:30]);
  assign grant[30] = win[7] & req[30] & ~(|req[31:31]);
  assign grant[31] = win[7] & req[31];
  assign grant[32] = win[8] & req[32] & ~(|req[35:33]);
  assign grant[33] = win[8] & req[33] & ~(|req[35:34]);
  assign grant[34] = win[8] & req[34] & ~(|req[35:35]);
  assign grant[35] = win[8] & req[35];
  assign grant[36] = win[9] & req[36] & ~(|req[39:37]);
  assign grant[37] = win[9] & req[37] & ~(|req[39:38]);
  assign grant[38] = win[9] & req[38] & ~(|req[39:39]);
  assign grant[39] = win[9] & req[39];
  assign grant[40] = win[10] & req[40] & ~(|req[43:41]);
  assign grant[41] = win[10] & req[41] & ~(|req[43:42]);
  assign grant[42] = win[10] & req[42] & ~(|req[43:43]);
  assign grant[43] = win[10] & req[43];
  assign grant[44] = win[11] & req[44] & ~(|req[47:45]);
  assign grant[45] = win[11] & req[45] & ~(|req[47:46]);
  assign grant[46] = win[11] & req[46] & ~(|req[47:47]);
  assign grant[47] = win[11] & req[47];
  assign grant[48] = win[12] & req[48] & ~(|req[51:49]);
  assign grant[49] = win[12] & req[49] & ~(|req[51:50]);
  assign grant[50] = win[12] & req[50] & ~(|req[51:51]);
  assign grant[51] = win[12] & req[51];
  assign grant[52] = win[13] & req[52] & ~(|req[55:53]);
  assign grant[53] = win[13] & req[53] & ~(|req[55:54]);
  assign grant[54] = win[13] & req[54] & ~(|req[55:55]);
  assign grant[55] = win[13] & req[55];
  assign grant[56] = win[14] & req[56] & ~(|req[59:57]);
  assign grant[57] = win[14] & req[57] & ~(|req[59:58]);
  assign grant[58] = win[14] & req[58] & ~(|req[59:59]);
  assign grant[59] = win[14] & req[59];
  assign grant[60] = win[15] & req[60] & ~(|req[63:61]);
  assign grant[61] = win[15] & req[61] & ~(|req[63:62]);
  assign grant[62] = win[15] & req[62] & ~(|req[63:63]);
  assign grant[63] = win[15] & req[63];

  // Index encoding: index bits are OR of grant bits with corresponding bit set in binary representation.
  // We use the same pattern as seed but with direct grant signals.
  assign index[0] = grant[1] | grant[3] | grant[5] | grant[7] | grant[9] | grant[11] | grant[13] | grant[15] |
                    grant[17] | grant[19] | grant[21] | grant[23] | grant[25] | grant[27] | grant[29] | grant[31] |
                    grant[33] | grant[35] | grant[37] | grant[39] | grant[41] | grant[43] | grant[45] | grant[47] |
                    grant[49] | grant[51] | grant[53] | grant[55] | grant[57] | grant[59] | grant[61] | grant[63];
  assign index[1] = grant[2] | grant[3] | grant[6] | grant[7] | grant[10] | grant[11] | grant[14] | grant[15] |
                    grant[18] | grant[19] | grant[22] | grant[23] | grant[26] | grant[27] | grant[30] | grant[31] |
                    grant[34] | grant[35] | grant[38] | grant[39] | grant[42] | grant[43] | grant[46] | grant[47] |
                    grant[50] | grant[51] | grant[54] | grant[55] | grant[58] | grant[59] | grant[62] | grant[63];
  assign index[2] = win[1] | win[3] | win[5] | win[7] | win[9] | win[11] | win[13] | win[15];
  assign index[3] = win[2] | win[3] | win[6] | win[7] | win[10] | win[11] | win[14] | win[15];
  assign index[4] = win[4] | win[5] | win[6] | win[7] | win[12] | win[13] | win[14] | win[15];
  assign index[5] = win[8] | win[9] | win[10] | win[11] | win[12] | win[13] | win[14] | win[15];

  assign valid = |req;

endmodule