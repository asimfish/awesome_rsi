/*
 * 64-bit priority encoder with parallel prefix
 * Highest set bit has priority.
 * valid = |req
 * index = highest set bit index, or 0 if req=0
 * grant = 1 << index (including when req=0, grant=1)
 */
module design(
    input wire [63:0] req,
    output wire valid,
    output wire [5:0] index,
    output wire [63:0] grant
);

// Group the 64 bits into 8 groups of 8 bits each.
wire [7:0] group_valid;      // valid if any bit in group is set
wire [2:0] group_index [7:0]; // index of highest set bit within group (0-7)

genvar g;
generate
    for (g = 0; g < 8; g = g + 1) begin : group_enc
        // group_valid[g] = |req[g*8 +: 8]
        assign group_valid[g] = |req[g*8 +: 8];

        // Priority encoder within group: find highest set bit index (0-7)
        // Use ternary chain: if bit7 set -> 7, else if bit6 set -> 6, ... else 0
        assign group_index[g] = req[g*8+7] ? 3'd7 :
                                req[g*8+6] ? 3'd6 :
                                req[g*8+5] ? 3'd5 :
                                req[g*8+4] ? 3'd4 :
                                req[g*8+3] ? 3'd3 :
                                req[g*8+2] ? 3'd2 :
                                req[g*8+1] ? 3'd1 :
                                req[g*8+0] ? 3'd0 : 3'd0; // default 0 if none set
    end
endgenerate

// Determine the highest priority group (group with highest index that is valid)
wire [2:0] highest_group;
wire group_any_valid;

// Parallel prefix: compute for each group whether it is the highest valid group.
// We can use a chain of ORs from high to low, but parallel prefix is more efficient.
// For 8 groups, we can compute a "prefix OR" from high to low.
wire [7:0] prefix_or_high; // prefix_or_high[i] = OR of group_valid[7:i]
assign prefix_or_high[7] = group_valid[7];
genvar i;
generate
    for (i = 6; i >= 0; i = i - 1) begin : prefix_or_gen
        assign prefix_or_high[i] = group_valid[i] | prefix_or_high[i+1];
    end
endgenerate

// highest_group is the index of the highest valid group, or 0 if none valid.
// Use a priority encoder on prefix_or_high? Actually, we can find the first group from high to low that is valid.
// We can use a chain of muxes: if group_valid[7] then 7, else if group_valid[6] then 6, ...
assign highest_group = group_valid[7] ? 3'd7 :
                       group_valid[6] ? 3'd6 :
                       group_valid[5] ? 3'd5 :
                       group_valid[4] ? 3'd4 :
                       group_valid[3] ? 3'd3 :
                       group_valid[2] ? 3'd2 :
                       group_valid[1] ? 3'd1 :
                       group_valid[0] ? 3'd0 : 3'd0;

// Overall valid: any group valid
assign group_any_valid = |group_valid;
assign valid = group_any_valid;

// Combine group index and group-internal index to get final 6-bit index.
// If no valid, index should be 0 (as per spec).
assign index = group_any_valid ? {highest_group, group_index[highest_group]} : 6'd0;

// Generate one-hot grant: 1 << index. If req=0, index=0, grant=1.
// We can use a decoder: grant[index] = 1, others 0.
// Since index is 6 bits, we can implement as a 6-to-64 decoder.
// To reduce logic, we can use a shift: grant = 64'b1 << index, but shift by variable may be large.
// Alternatively, use a generate loop to assign each bit.
wire [63:0] grant;
genvar j;
generate
    for (j = 0; j < 64; j = j + 1) begin : grant_gen
        assign grant[j] = (index == j);
    end
endgenerate

endmodule
