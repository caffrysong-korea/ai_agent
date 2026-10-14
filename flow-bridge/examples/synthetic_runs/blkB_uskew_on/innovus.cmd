# cmd log (fictional) run=blkB_uskew_on host=hostX date=2026-10-04
source /proj/runs/blkB_uskew_on/design_cfg.tcl
init_design
setDesignMode -process 5
defIn /proj/runs/blkB_uskew_on/fp.def
setPlaceMode -place_global_cong_effort high
place_opt_design
ccopt_design
setOptMode -usefulSkew true
optDesign -postCTS
routeDesign
optDesign -postRoute
