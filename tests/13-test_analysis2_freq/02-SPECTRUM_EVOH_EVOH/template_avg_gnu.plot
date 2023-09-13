reset
set xlabel "Freq (cm^-1)"
set ylabel "Normalized Intensity"
set grid
set xrange [400:4000]
set yrange [0:1]
# **************************************************
set term wxt 1 enhanced dashed size 500,300 font "Arial,8"
set multiplot layout 1,1
set title "boltzmann-spectrum.dat # spectra 185"
p "./boltzmann_spectrum.dat" u 1:2 w l notitle
unset multiplot
set term wxt 2 enhanced dashed size 500,300 font "Arial,8"
set multiplot layout 1,1
set title "averaged-spectrum.dat # spectra 185"
p "./averaged_spectrum.dat" u 1:2 w l notitle
unset multiplot
set term wxt 3 enhanced dashed size 500,300 font "Arial,8"
set multiplot layout 1,1
set title "similarity-avg-spectrum.dat # spectra 6"
p "./similarity_avg_spectrum.dat" u 1:2 w l notitle
