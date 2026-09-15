/*
 * Optimized priority encoder for 64-bit input.
 * Groups: 8 groups of 8 bits each.
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

// Group valid flags
wire [7:0] group_valid;
// Group index (3 bits) of highest set bit within each group, valid only if group_valid
wire [2:0] group_idx [7:0];

genvar g, i;

// For each group of 8 bits, compute group_valid and group_idx
generate
    for (g = 0; g < 8; g = g + 1) begin : group_logic
        // group_valid = OR of bits in group
        assign group_valid[g] = |req[g*8 +: 8];

        // Priority encoder within group: find highest set bit index (0-7)
        // Use a chain of if-else style via ternary operators
        // Since Verilog-2005 doesn't allow procedural blocks in generate for combinational logic,
        // we use a function or assign with nested ternary.
        // For 8 bits, we can express as:
        // if bit7 set -> 7, else if bit6 set -> 6, ... else 0.
        // We'll use a recursive generate or just a large ternary expression.
        // To keep it synthesizable and simple, we'll use a local function.
        // But functions must be defined outside generate? Actually can define inside module.
        // We'll define a function to compute the index.
        // However, functions cannot be defined inside generate loops? They can be defined at module level.
        // We'll define a function outside generate, then call it with the group bits.
        // But function input is 8-bit, output 3-bit.
        // We'll define function prio8.
    end
endgenerate

// Function to compute 3-bit index of highest set bit in 8-bit input.
// Returns 0 if no bit set, but we only use when group_valid is true.
function [2:0] prio8;
    input [7:0] bits;
    begin
        if (bits[7]) prio8 = 3'd7;
        else if (bits[6]) prio8 = 3'd6;
        else if (bits[5]) prio8 = 3'd5;
        else if (bits[4]) prio8 = 3'd4;
        else if (bits[3]) prio8 = 3'd3;
        else if (bits[2]) prio8 = 3'd2;
        else if (bits[1]) prio8 = 3'd1;
        else prio8 = 3'd0;
    end
endfunction

// Assign group_idx using function
generate
    for (g = 0; g < 8; g = g + 1) begin : group_idx_assign
        assign group_idx[g] = prio8(req[g*8 +: 8]);
    end
endgenerate

// Now determine the highest priority group (i.e., the group with highest index that has group_valid=1)
// We need a 3-bit index of that group (0-7).
// We'll use a priority encoder on group_valid (8 bits) to get group_sel (3 bits).
wire [2:0] group_sel;

// Priority encoder for 8-bit group_valid, highest bit priority (bit7 highest)
// Similar to prio8 but output 3 bits.
function [2:0] prio8_valid;
    input [7:0] bits;
    begin
        if (bits[7]) prio8_valid = 3'd7;
        else if (bits[6]) prio8_valid = 3'd6;
        else if (bits[5]) prio8_valid = 3'd5;
        else if (bits[4]) prio8_valid = 3'd4;
        else if (bits[3]) prio8_valid = 3'd3;
        else if (bits[2]) prio8_valid = 3'd2;
        else if (bits[1]) prio8_valid = 3'd1;
        else prio8_valid = 3'd0;
    end
endfunction

assign group_sel = prio8_valid(group_valid);

// Overall valid
assign valid = |group_valid;

// Index = {group_sel, group_idx[group_sel]} but group_idx is a memory-like array; we need to select.
// Since group_idx is an unpacked array of 3-bit wires, we can use a mux.
// We'll generate a mux tree or use a case statement in a function.
// Simpler: use a 8-to-1 mux via ternary or generate.
wire [2:0] group_idx_selected;

generate
    // Use a chain of ternary: group_sel==0 ? group_idx[0] : group_sel==1 ? group_idx[1] : ...
    // But group_idx is an array of wires, we can index with variable? In Verilog-2005, you cannot use variable to index an unpacked array in continuous assignment? Actually you can if it's a memory? But here group_idx is declared as "wire [2:0] group_idx [7:0];" which is an unpacked array of wires. You can use a variable index to read from it in an expression? In Verilog-2001, yes, if it's a memory, you can use a variable index to read, but it's not synthesizable for arbitrary variable? Actually it is synthesizable as a mux. But to be safe, we'll generate a mux explicitly.
    // We'll create a 8-to-1 mux using a generate loop with nested ternary.
    // Alternative: use a case statement inside an always @(*) block, but that would be procedural and we want continuous assignment? It's fine, combinational always block is allowed.
    // However, the problem says "no initial blocks", but always @(*) is allowed for combinational logic.
    // We'll use a continuous assignment with a nested ternary built by generate? That may be messy.
    // Simpler: use a function that takes group_sel and returns group_idx[group_sel]? But function cannot access module-level wires? It can if passed as inputs.
    // We'll define a function that takes the 8 group_idx values and group_sel, and returns the selected one.
    // But that would require passing 8 inputs and 3-bit sel, which is fine.
    // We'll do:
endgenerate

// Function to select one of 8 3-bit values based on 3-bit sel.
function [2:0] select_group_idx;
    input [2:0] sel;
    input [2:0] idx0, idx1, idx2, idx3, idx4, idx5, idx6, idx7;
    begin
        case (sel)
            3'd0: select_group_idx = idx0;
            3'd1: select_group_idx = idx1;
            3'd2: select_group_idx = idx2;
            3'd3: select_group_idx = idx3;
            3'd4: select_group_idx = idx4;
            3'd5: select_group_idx = idx5;
            3'd6: select_group_idx = idx6;
            3'd7: select_group_idx = idx7;
            default: select_group_idx = 3'd0;
        endcase
    end
endfunction

assign group_idx_selected = select_group_idx(group_sel, group_idx[0], group_idx[1], group_idx[2], group_idx[3], group_idx[4], group_idx[5], group_idx[6], group_idx[7]);

// Final index = {group_sel, group_idx_selected}
assign index = {group_sel, group_idx_selected};

// Grant = 1 << index, but when req=0, index=0, so grant = 1 (since 1<<0=1).
// We can compute grant as a one-hot decode of index.
// Use a 6-to-64 decoder.
// Since index is 6 bits, we can generate a loop.
wire [63:0] grant_internal;

generate
    for (i = 0; i < 64; i = i + 1) begin : grant_gen
        assign grant_internal[i] = (index == i);
    end
endgenerate

assign grant = grant_internal;

endmodule
