# common settings (fictional)
proc apply_design_overrides {stage} {
    global env
    set f $env(DESIGN_DIR)/overrides_$stage.tcl
    if {[file exists $f]} {
        source $f
    }
}

set opt_modes {
    -fixHoldAllowSetupTnsDegrade false
    -usefulSkew true
}
foreach {opt val} $opt_modes {
    setOptMode $opt $val
}
setNanoRouteMode -routeWithTimingDriven true
