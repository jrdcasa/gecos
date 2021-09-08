proc newRep { sel type color rep imol} {
    mol selection $sel
    mol representation $type
    mol addrep $imol
    mol showrep $imol $rep on
    mol modcolor $rep $imol $color
}

display projection orthographic
axes location off
color Display Background white
display depthcue off

set listFiles { IsoP_rdkit_151_gaussian_allign.mol2 IsoP_rdkit_166_gaussian_allign.mol2 IsoP_rdkit_295_gaussian_allign.mol2 IsoP_rdkit_356_gaussian_allign.mol2 IsoP_rdkit_419_gaussian_allign.mol2 IsoP_rdkit_189_gaussian_allign.mol2 IsoP_rdkit_238_gaussian_allign.mol2}

foreach ifile $listFiles {
    mol addfile $ifile type mol2
    set imol [molinfo top]
}
set imol_ref [molinfo top]
mol rename $imol_ref "OptimizedConformers"
mol delrep 0 $imol_ref
set rep1 0
newRep "all" "CPK" "ColorID 4" $rep1 $imol_ref

