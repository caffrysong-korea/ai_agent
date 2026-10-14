# stage 01: init (fictional)
source $env(DESIGN_DIR)/design_cfg.tcl
init_design
setDesignMode -process 5
run_hook post_init
