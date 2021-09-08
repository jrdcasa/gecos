proc newRep { sel type color rep imol} {
    mol selection $sel
    mol representation $type
    mol addrep $imol
    mol showrep $imol $rep on
    mol modcolor $rep $imol $color
}

set dir "/home/jramos/PycharmProjects/GeCos/examples/03-IsoP_localhost_rdkit_pm3/03-IsoP_g16_conformers"

display projection orthographic
axes location off
color Display Background white
display depthcue off

set listFiles {}
lappend listFiles [list $dir/03-IsoP_151_gaussian_allign.mol2]
lappend listFiles [list $dir/03-IsoP_166_gaussian_allign.mol2]
lappend listFiles [list $dir/03-IsoP_295_gaussian_allign.mol2]
lappend listFiles [list $dir/03-IsoP_356_gaussian_allign.mol2]
lappend listFiles [list $dir/03-IsoP_419_gaussian_allign.mol2]
lappend listFiles [list $dir/03-IsoP_189_gaussian_allign.mol2]
lappend listFiles [list $dir/03-IsoP_238_gaussian_allign.mol2]


foreach ifile $listFiles {
    mol addfile $ifile type mol2
    set imol [molinfo top]
}
set imol_ref [molinfo top]
mol rename $imol_ref "OptimizedConformers"
mol delrep 0 $imol_ref
set rep1 0
newRep "all" "CPK" "Name" $rep1 $imol_ref
animate goto start

