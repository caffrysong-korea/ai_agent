# blkA constraints (fictional)
create_clock -name clk_core -period 0.500 [get_ports clk]
create_generated_clock -name clk_div2 -source [get_ports clk] -divide_by 2 [get_pins u_div/q]
set_clock_uncertainty 0.030 [all_clocks]
set_input_delay 0.100 -clock clk_core [all_inputs]
set_output_delay 0.100 -clock clk_core [all_outputs]
set_false_path -from [get_ports rst_n]
set_multicycle_path 2 -setup -from [get_pins u_slow/*]
