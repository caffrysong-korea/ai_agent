# stage 03: place (fictional)
run_hook pre_place
setPlaceMode -place_global_cong_effort $PLACE_CONG_EFFORT
place_opt_design
run_hook post_place
