reset
set xlabel "Freq (cm^-1)"
set ylabel "Intensity"
set grid
set xrange [0:4000]
set yrange [0:255]
# **************************************************
unset multiplot
set term wxt 1 enhanced dashed size 500,300 font "Arial,8"
set multiplot layout 1,1
set title "boltzmann-spectrum.dat"
p "./boltzmann_spectrum.dat" u 1:2 w l notitle
unset multiplot
set term wxt 2 enhanced dashed size 500,300 font "Arial,8"
set multiplot layout 1,1
set title "averaged-spectrum.dat"
p "./averaged_spectrum.dat" u 1:2 w l notitle
