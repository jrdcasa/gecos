reset
set xlabel "Freq (cm^-1)"
set ylabel "Intensity"
set grid
set xrange [599:4000]
set yrange [0:1]
# **************************************************

set term wxt 1 enhanced dashed size 1500,600 font "Arial,8"
set multiplot layout 2,3
set title "Original"
p "./Spectra/EVOH-EVA_exp.dat" u 1:2 w l notitle lc rgb "black"

set title "Normalize minmax"
p "./01_tmp_EVOH-EVA_exp_normalize_minmax.dat" u 1:2 w l notitle lc rgb "black" 

set title "Peak Smoothing SG"
p "./05-tmp_peaksmoothing_SG.dat" u 1:2 w l lc rgb "blue" title "Smoothed"

set title "Final Spectrum"
p "./EVOH-EVA_exp_corrected.dat" u 1:2 w l lc rgb "blue" notitle 

unset multiplot

set term wxt 2 enhanced dashed size 600,400 font "Arial,8"
set multiplot layout 1,1

unset yrange
p\
    "./Spectra/EVOH-EVA_exp.dat" u 1:2 w l lc rgb "black" title "Original",\
    "./EVOH-EVA_exp_corrected.dat" u 1:2 w l lc rgb "blue" title "Corrected"

