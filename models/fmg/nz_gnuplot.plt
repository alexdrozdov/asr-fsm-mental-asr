set grid
set polar
set size ratio -1
unset key
set title "Границы ближней зоны"

set terminal latex
set output "nz_gnuplot.tex"

plot 'nz_gnuplot_data.dat' w l ls 1