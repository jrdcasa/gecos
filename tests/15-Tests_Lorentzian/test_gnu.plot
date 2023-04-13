reset
set xlabel "Freq (cm^-1)"
set ylabel "Intensity"
set grid
set xrange [0:4000]
#set yrange [0:336]
# **************************************************
unset multiplot
set term wxt 1 enhanced dashed size 1500,900 font "Arial,8"
set multiplot layout 2,3
set title "C12H26O3_pair_019_058_allign_FREQ_g16_spectrum_lorentz01.dat"
p "./C12H26O3_pair_019_058_allign_FREQ_g16_spectrum_lorentz01.dat" u 1:($2) w l notitle
set title "GaussSum3.0.2"
p "./IRSpectrum.txt" u 1:2 w l notitle
set title "gview"
set ylabel "{/Symbol e}(M^{-1}cm^{-1})"
p "./C12H26O3_pair_019_058_allign_FREQ_g16_ir.txt" u 1:2 w l notitle
set title "C12H26O3_pair_019_058_allign_FREQ_g16_spectrum.dat"
p "./C12H26O3_pair_019_058_allign_FREQ_g16_spectrum.dat" u 1:($2) w l notitle
unset multiplot


set term wxt 2 enhanced dashed size 1500,450 font "Arial,8"
set multiplot layout 1,2
set title "All"
set key top left  
p "./C12H26O3_pair_019_058_allign_FREQ_g16_spectrum_lorentz01.dat" u 1:2 w l title "GEcos Lorentz1",\
  "./IRSpectrum.txt" u 1:2 w p title "GaussSum",\

p  "./C12H26O3_pair_019_058_allign_FREQ_g16_ir.txt" u 1:2 w l title "GaussView",\
  "./C12H26O3_pair_019_058_allign_FREQ_g16_spectrum.dat" u 1:2 w p title "GEcos Lorentz2"

unset multiplot

set term wxt 3 enhanced dashed size 1500,900 font "Arial,8"
set multiplot layout 2,2
set title "All"

# Retrieve statistical properties
stats 'IRSpectrum.txt' using 2
#show variables all
ymax=STATS_max
print ymax

# Retrieve statistical properties
stats 'C12H26O3_pair_019_058_allign_FREQ_g16_ir.txt' using 2
#show variables all
ymaxx=STATS_max
print ymaxx


set key top left  
p "./C12H26O3_pair_019_058_allign_FREQ_g16_spectrum_lorentz01.dat" u 1:($3) w l title "GEcos Lorentz1",\
  "./IRSpectrum.txt" u 1:($2/ymax) w p title "GaussSum",\

p  "./C12H26O3_pair_019_058_allign_FREQ_g16_ir.txt" u 1:($2/ymaxx) w l title "GaussView",\
  "./C12H26O3_pair_019_058_allign_FREQ_g16_spectrum.dat" u 1:3 w p title "GEcos Lorentz2"

p "./C12H26O3_pair_019_058_allign_FREQ_g16_spectrum_lorentz01.dat" u 1:($3) w p title "GEcos Lorentz1",\
  "./IRSpectrum.txt" u 1:($2/ymax) w p title "GaussSum",\
   "./C12H26O3_pair_019_058_allign_FREQ_g16_ir.txt" u 1:($2/ymaxx) w l title "GaussView",\
  "./C12H26O3_pair_019_058_allign_FREQ_g16_spectrum.dat" u 1:3 w l title "GEcos Lorentz2"
unset multiplot
