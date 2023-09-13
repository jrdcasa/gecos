reset
f1="/home/jramos/Programacion/GITHUB_REPO_DIR/gecos2/tests/13-test_analysis2_freq/01-ENERGY_EVOH_ETH/gecos_energy_analysis.dat"

# ============== COMMON FORMATS ====================
set style line 1 lt 1 ps 1.0 lc rgb "black"  pt 6 lw 2.0
set style line 2 lt 1 ps 1.0 lc rgb "black"  pt 4 lw 2.0
set style line 3 lt 1 ps 1.0 lc rgb "black"  pt 6 lw 2.0

# ============== 2D PLOT =====================
set term wxt 1 enhanced dashed size 900,800 font "Arial,12"
set multiplot layout 3,2

set title "Relative energy of conformers"
set xlabel "Conformer ID"
set ylabel "Rel. Energy (kcal/mol)
set xtics 20.0
set xrange[-1:205]
set format y "%.1f"
set grid
p f1 u 1:4 ls 1 notitle
unset xrange

set title "Relative energy vs RMSD"
set xlabel "Rel. Energy (kcal/mol)
set ylabel "RMSD (Angstroms)"
set format x "%.1f"
set format y "%.1f"
set xtics auto
p f1 u 4:6 ls 2 notitle

set title "Relative energy vs Number H bonds"
set xlabel "Rel. Energy (kcal/mol)"
set ylabel "# H-bonds"
set format x "%.1f"
unset format y
set ytics 1
set xtics auto
set yrange [-1:1]
p f1 u 4:11 ls 3 notitle
unset yrange

set title "Relative energy vs Intermolecular Contacts"
set xlabel "Rel. Energy (kcal/mol)"
set ylabel "# Intermolecular Contacts"
set format x "%.1f"
unset format y
set ytics 1
set xtics auto
set yrange [-1:4]
p f1 u 4:12 ls 3 notitle
unset yrange

set title "Relative energy vs Intramolecular Contacts"
set xlabel "Rel. Energy (kcal/mol)"
set ylabel "# Intramolecular Contacts"
set format x "%.1f"
set format y "%.0f"
unset format y
set ytics 1
set xtics auto
set yrange [1:6]
p f1 u 4:13 ls 3 notitle
unset yrange

set title "Number H bonds vs RMDS (with energy)"
set xlabel "RMSD (Angstroms)"
set ylabel "# H-bonds"
set format x "%.1f"
set format y "%.0f"
set xtics auto
set yrange [-1:1]
set grid
set palette rgb 33,13,10
plot f1 u 6:11:4 palette pt 7 notitle
unset yrange

unset multiplot

# ============== 3D-POINT PLOT ===============
set term wxt 2 enhanced dashed size 500,400 font "Arial,12"
set multiplot layout 1,1

unset view
set zlabel "Rel. Energy (kcal/mol)
set xlabel "RMSD (Angstroms)"
set ylabel "# H-bonds"
set xtics auto
set ytics auto
set ztics auto
splot f1 u 6:11:4 ls 1 notitle w p
unset multiplot
