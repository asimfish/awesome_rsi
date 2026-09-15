module design(input wire [63:0] req, output wire valid, output reg [5:0] index, output wire [63:0] grant);
integer i;
always @* begin index=0; for(i=0;i<64;i=i+1) if(req[i]) index=i; end
assign valid=|req;
assign grant=valid ? (64'b1 << index) : 64'b0;
endmodule