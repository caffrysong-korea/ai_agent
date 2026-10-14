# synthetic customer flow (fictional) - entry script
set FLOW_ROOT [file dirname [info script]]
set HOOK_DIR  $FLOW_ROOT/hooks

proc run_hook {name} {
    global HOOK_DIR
    if {[file exists $HOOK_DIR/$name.tcl]} {
        source $HOOK_DIR/$name.tcl
    }
}

source $FLOW_ROOT/common/settings.tcl
source $FLOW_ROOT/stages/01_init.tcl
source $FLOW_ROOT/stages/02_floorplan.tcl
source $FLOW_ROOT/stages/03_place.tcl
source $FLOW_ROOT/stages/04_cts.tcl
source $FLOW_ROOT/stages/05_route.tcl
