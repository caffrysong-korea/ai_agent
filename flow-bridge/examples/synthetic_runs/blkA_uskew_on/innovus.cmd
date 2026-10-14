# cmd log (fictional) run=blkA_uskew_on host=hostX date=2026-10-02
source /proj/runs/blkA_uskew_on/design_cfg.tcl
init_design
setDesignMode -process 5
defIn /proj/runs/blkA_uskew_on/fp.def
setPlaceMode -place_global_cong_effort medium
place_opt_design
ccopt_design
setOptMode -usefulSkew true
optDesign -postCTS
routeDesign
optDesign -postRoute
