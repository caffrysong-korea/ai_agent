# REF cts stage (fictional)
ccopt_design
if {$DTCO_USKEW} {
    setOptMode -usefulSkew true
}
optDesign -postCTS
