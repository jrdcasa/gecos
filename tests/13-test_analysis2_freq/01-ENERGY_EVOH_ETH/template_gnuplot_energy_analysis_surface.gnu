reset
f1="./gecos_energy_analysis.dat"

# ============== COMMON FORMATS ====================
set style line 1 lt 1 ps 1.0 lc rgb "black"  pt 6 lw 2.0
set style line 2 lt 1 ps 1.0 lc rgb "black"  pt 4 lw 2.0
set style line 3 lt 1 ps 1.0 lc rgb "black"  pt 2 lw 2.0


# ============== 3D-POINT SURFACE ===============
set term wxt 5 enhanced dashed size 700,600 font "Arial,12"
set multiplot layout 1,1

set xlabel "RMSD (Angstroms)"
set ylabel "Rel. Energy (kcal/mol)
set zlabel "# H-bonds"

#set yrange[-.2:1.2]

set dgrid3d 50 50 50
set pm3d map
set surface
set view map
set contour
set key outside
set cntrparam linear  # Smooth out the lines
set cntrparam levels incremental 0, .5, 12 # Plot the selected contours
set palette rgb 33,13,10
set cbrange [0:1]  # Set the color range of contour values.
set style line 1 lc rgb '#4169E1' pt 7 ps 2

splot f1 u 6:4:11 ls 1 notitle w pm3d

unset multiplot
