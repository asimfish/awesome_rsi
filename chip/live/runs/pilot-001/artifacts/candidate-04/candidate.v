/*
 * 64-bit priority encoder with highest bit priority.
 * Uses parallel prefix structure for reduced logic depth.
 */
module design(
    input wire [63:0] req,
    output wire valid,
    output wire [5:0] index,
    output wire [63:0] grant
);

// Group the 64 bits into 8 groups of 8 bits each.
wire [7:0] group_valid;
wire [2:0] group_index [7:0];

genvar i;
generate
    for (i = 0; i < 8; i = i + 1) begin : group_enc
        // Within each group, find the highest set bit.
        // Since 8 bits, we can use casez for clarity and let synthesis optimize.
        reg [2:0] idx;
        reg vld;
        always @(*) begin
            casez (req[i*8 +: 8])
                8'b1???????: begin idx = 3'd7; vld = 1'b1; end
                8'b01??????: begin idx = 3'd6; vld = 1'b1; end
                8'b001?????: begin idx = 3'd5; vld = 1'b1; end
                8'b0001????: begin idx = 3'd4; vld = 1'b1; end
                8'b00001???: begin idx = 3'd3; vld = 1'b1; end
                8'b000001??: begin idx = 3'd2; vld = 1'b1; end
                8'b0000001?: begin idx = 3'd1; vld = 1'b1; end
                8'b00000001: begin idx = 3'd0; vld = 1'b1; end
                default: begin idx = 3'd0; vld = 1'b0; end
            endcase
        end
        assign group_valid[i] = vld;
        assign group_index[i] = idx;
    end
endgenerate

// Compute prefix OR of group_valid from highest group to lowest.
// We want the highest group that has any bit set.
wire [7:0] prefix_or;
assign prefix_or[7] = group_valid[7];
genvar j;
generate
    for (j = 6; j >= 0; j = j - 1) begin : prefix_gen
        assign prefix_or[j] = group_valid[j] | prefix_or[j+1];
    end
endgenerate

// Determine the highest priority group: the first group from MSB where group_valid is 1.
// We can compute a one-hot for the group.
wire [7:0] group_onehot;
genvar k;
generate
    for (k = 0; k < 8; k = k + 1) begin : group_onehot_gen
        if (k == 7) begin
            assign group_onehot[k] = group_valid[k];
        end else begin
            assign group_onehot[k] = group_valid[k] & ~prefix_or[k+1];
        end
    end
endgenerate

// Encode the group index from one-hot.
wire [2:0] group_sel;
assign group_sel[2] = group_onehot[7] | group_onehot[6] | group_onehot[5] | group_onehot[4];
assign group_sel[1] = group_onehot[7] | group_onehot[6] | group_onehot[3] | group_onehot[2];
assign group_sel[0] = group_onehot[7] | group_onehot[5] | group_onehot[3] | group_onehot[1];

// Select the group index of the winning group.
wire [2:0] selected_group_index;
assign selected_group_index = group_index[group_sel];

// Combine group index and within-group index to form 6-bit index.
assign index = {group_sel, selected_group_index};

// valid is OR of all group_valid.
assign valid = |group_valid;

// grant is one-hot on the winning bit.
// We can generate by decoding index.
assign grant = (64'b1 << index);

endmodule
