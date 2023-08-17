reset
# =======================================================================
set term wxt 1 enhanced dashed size 600,400 font "Arial,8"

set pm3d
set xyplane at 90
set hidden3d
#set dgrid3d 200,200 qnorm 2
set zrange [0:1000]
set xrange [-180:180]
set yrange [-180:180]
set xtics 40
set ytics 40
set palette defined (0 "blue", 4 "white",  6 "yellow", 8 "red")
#splot './dihedral_grid.dat'   with lines notitle
#pause -1

reset
# =======================================================================
set term wxt 2 enhanced dashed size 500,400 font "Arial,12"

set title "Glucose"
set view map
set xrange [-180:180]
set yrange [-180:180]
set zrange [0:16]
set xtics 60
set mxtics 6
set ytics 60
set mytics 6
set xlabel "{/Symbol f}(degree)"
set ylabel "{/Symbol y}(degree)"
set grid 
#set dgrid3d 100,100 qnorm 2
set contour base
set cbrange [0:1600]
#set cblabel "E_{rel} (kcal/mol)"  font "Arial,8"
set palette defined (0 "blue", 4 "white",  6 "yellow", 8 "red")

splot './dihedral_grid.dat' u 1:2:3   with pm3d notitle

reset
# =======================================================================
set term wxt 3 enhanced dashed size 500,400 font "Arial,12"

set xrange [-180:180]
set yrange [-180:180]
set zrange [0:14]

plot './dihedral.dat' u 2:3 w p


#set isosample  200,200
#set table 'test.dat'
#splot "./dihedral.dat" u 2:3:4
#unset table
#
#set contour base
#set cntrparam level incremental 0, 4, 8 
#unset surface
#set table 'cont.dat'
#set dgrid3d 100,100 qnorm 2
#splot "./dihedral.dat" u 2:3:4
#unset table
#
#reset
#set xrange [-180:180]
#set yrange [-180:180]
#set zrange [0:14]
#unset key
#set palette defined (0 "blue", 4 "white",  6 "yellow", 8 "red")
#p 'test.dat' with image, 'cont.dat' w l lt -1 lw 1.5
