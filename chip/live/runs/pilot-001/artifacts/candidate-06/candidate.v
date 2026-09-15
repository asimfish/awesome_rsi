/*
Copyright (c) 2024
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
*/

`resetall
`timescale 1ns / 1ps
`default_nettype none

module design(
    input wire [63:0] req,
    output wire valid,
    output wire [5:0] index,
    output wire [63:0] grant
);

// Group the 64-bit request into 8 groups of 8 bits each.
wire [7:0] group_valid;   // group_valid[i] = |req[i*8 +: 8]
wire [2:0] group_index [0:7]; // group_index[i] = highest set bit within group i (0-7)

genvar g, i;

// For each group, compute valid and index of highest set bit.
generate
    for (g = 0; g < 8; g = g + 1) begin : group_logic
        assign group_valid[g] = |req[g*8 +: 8];
        // Priority encoder within 8 bits: highest bit has priority.
        // Use a simple chain of if-else in a function-like manner via assign.
        // Since we need a 3-bit index, we can use a casez or nested ternary.
        // To keep it synthesizable and simple, use a ternary tree.
        assign group_index[g] = 
            req[g*8+7] ? 3'd7 :
            req[g*8+6] ? 3'd6 :
            req[g*8+5] ? 3'd5 :
            req[g*8+4] ? 3'd4 :
            req[g*8+3] ? 3'd3 :
            req[g*8+2] ? 3'd2 :
            req[g*8+1] ? 3'd1 :
            req[g*8+0] ? 3'd0 :
            3'd0; // default when group_valid=0, but this value is don't care in that case.
    end
endgenerate

// Determine the highest priority group that has any valid bit.
// We need a 3-bit group index (0-7) and a valid signal.
wire [2:0] group_sel;
wire any_group_valid;

// Use a priority chain among groups: group 7 highest priority down to 0.
// This can be implemented as a series of muxes or a casez.
// We'll use a nested ternary for clarity.
assign any_group_valid = |group_valid;
assign group_sel = 
    group_valid[7] ? 3'd7 :
    group_valid[6] ? 3'd6 :
    group_valid[5] ? 3'd5 :
    group_valid[4] ? 3'd4 :
    group_valid[3] ? 3'd3 :
    group_valid[2] ? 3'd2 :
    group_valid[1] ? 3'd1 :
    group_valid[0] ? 3'd0 :
    3'd0; // default when no group valid.

// Combine group index and group-internal index to get final 6-bit index.
assign index = {group_sel, group_index[group_sel]};

// Generate one-hot grant from index.
// grant = 1 << index, but when req==0, grant must be 1 (per spec: grant=1 when req=0).
// Since valid = |req, we can use valid to select: if valid, grant = 1<<index; else grant = 1.
// Alternatively, we can compute 1<<index and then OR with !valid.
wire [63:0] grant_pre;
assign grant_pre = 64'd1 << index;
assign grant = valid ? grant_pre : 64'd1;

assign valid = any_group_valid;

endmodule

`resetall
