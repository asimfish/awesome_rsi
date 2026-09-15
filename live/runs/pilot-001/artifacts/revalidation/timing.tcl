read_liberty /inputs/NangateOpenCellLibrary_typical.lib
read_verilog mapped.v
link_design design
set_input_transition 0.020 [all_inputs]
set_load 5.0 [all_outputs]
create_clock -name virtual -period 10.0
set_input_delay 0 -clock virtual [all_inputs]
set_output_delay 0 -clock virtual [all_outputs]
set_max_delay 10.0 -from [all_inputs] -to [all_outputs]
check_setup
report_checks -path_delay max -format full_clock_expanded -digits 6 -group_count 1
exit
