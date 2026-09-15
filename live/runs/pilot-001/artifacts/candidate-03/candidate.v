module design(input wire [63:0] req, output wire valid, output wire [5:0] index, output wire [63:0] grant);
    // 分组：16组，每组4位
    wire [3:0] group_valid;   // 每组是否有有效位
    wire [1:0] group_index [0:15]; // 每组内最高置位位的2位索引
    genvar i, j;
    generate
        for (i = 0; i < 16; i = i + 1) begin : group_loop
            // 组内优先级编码：4位输入，输出2位索引
            assign group_valid[i] = |req[i*4 +: 4];
            assign group_index[i] = req[i*4+3] ? 2'd3 :
                                    req[i*4+2] ? 2'd2 :
                                    req[i*4+1] ? 2'd1 : 2'd0;
        end
    endgenerate

    // 第一级仲裁：将16组分为4块，每块4组
    wire [3:0] block_valid;   // 每块是否有有效组
    wire [1:0] block_group_index [0:3]; // 块内最高优先级组的2位索引
    generate
        for (i = 0; i < 4; i = i + 1) begin : block_loop
            // 块内4组：i*4, i*4+1, i*4+2, i*4+3
            assign block_valid[i] = group_valid[i*4] | group_valid[i*4+1] | group_valid[i*4+2] | group_valid[i*4+3];
            // 优先级从高到低：i*4+3, i*4+2, i*4+1, i*4
            assign block_group_index[i] = group_valid[i*4+3] ? 2'd3 :
                                          group_valid[i*4+2] ? 2'd2 :
                                          group_valid[i*4+1] ? 2'd1 : 2'd0;
        end
    endgenerate

    // 第二级仲裁：从4块中选出最高优先级块
    wire [1:0] block_index; // 最高优先级块的2位索引
    assign block_index = block_valid[3] ? 2'd3 :
                         block_valid[2] ? 2'd2 :
                         block_valid[1] ? 2'd1 : 2'd0;

    // 最终索引：块索引（高2位） + 块内组索引（中2位） + 组内索引（低2位）
    wire [5:0] index_wire;
    assign index_wire = {block_index, block_group_index[block_index], group_index[block_index*4 + block_group_index[block_index]]};

    // 有效信号：任一块有效
    assign valid = block_valid[0] | block_valid[1] | block_valid[2] | block_valid[3];

    // 输出索引
    assign index = index_wire;

    // 生成独热码grant：利用索引译码
    // 使用generate循环对64位进行译码
    wire [63:0] grant_wire;
    generate
        for (i = 0; i < 64; i = i + 1) begin : grant_loop
            assign grant_wire[i] = (index_wire == i);
        end
    endgenerate
    // 当req=0时，grant应为1（最低位），但index_wire为0，所以grant[0]=1，符合要求
    assign grant = grant_wire;
endmodule