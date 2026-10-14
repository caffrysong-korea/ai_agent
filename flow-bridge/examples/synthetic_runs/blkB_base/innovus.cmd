# cmd log (fictional) run=blkB_base host=hostX date=2026-10-03
source /proj/runs/blkB_base/design_cfg.tcl
init_design
setDesignMode -process 5
defIn /proj/runs/blkB_base/fp.def
setPlaceMode -place_global_cong_effort medium
place_opt_design
ccopt_design
optDesign -postCTS
routeDesign
optDesign -postRoute
