reset
set xlabel "Freq (cm^-1)"
set ylabel "Normalized Intensity"
set grid
set xrange [0:4000]
set yrange [0:1]
# **************************************************
unset multiplot
set term wxt 1 enhanced dashed size 1500,900 font "Arial,8"
set multiplot layout 3,3
set title "C12H26O3-pair-004-088-allign-FREQ-g16-spectrum.dat"
p "./C12H26O3_pair_004_088_allign_FREQ_g16_spectrum.dat" u 1:2 w l notitle
set title "C12H26O3-pair-001-018-allign-FREQ-g16-spectrum.dat"
p "./C12H26O3_pair_001_018_allign_FREQ_g16_spectrum.dat" u 1:2 w l notitle
set title "C12H26O3-pair-003-098-allign-FREQ-g16-spectrum.dat"
p "./C12H26O3_pair_003_098_allign_FREQ_g16_spectrum.dat" u 1:2 w l notitle
set title "C12H26O3-pair-037-041-allign-FREQ-g16-spectrum.dat"
p "./C12H26O3_pair_037_041_allign_FREQ_g16_spectrum.dat" u 1:2 w l notitle
