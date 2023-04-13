reset
set xlabel "Freq (cm^-1)"
set ylabel "Intensity"
set grid
set xrange [0:4000]
set yrange [0:1163]
# **************************************************
unset multiplot
set term wxt 1 enhanced dashed size 1500,900 font "Arial,8"
set multiplot layout 3,3
set title "C12H26O3-pair-019-058-allign-FREQ-g16-spectrum.dat"
p "./C12H26O3_pair_019_058_allign_FREQ_g16_spectrum.dat" u 1:2 w l notitle
