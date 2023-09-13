reset
###############################################################################
#set term wxt 1 enhanced dashed size 500,400 font "Arial,8"
set term png 1 size 500,400 font "Arial,8"
#set multiplot layout 1,1

list=system("echo $(ls *spectrum.dat)")
print list
#plot for [i in list] i u 1:2 w l notitle
do for [i in list] {
 print i
 set output sprintf('%s.png', i)
 plot i using 1:2 w l notitle
}
#plot x
