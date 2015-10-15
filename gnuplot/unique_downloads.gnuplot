set terminal postscript eps enhanced color font 'Helvetica,10'
set output 'output/unique_downloads.eps'
set boxwidth 0.75 absolute
set style fill solid 1.00 noborder
set key outside right top vertical Left reverse noenhanced autotitle columnhead nobox
set style histogram rowstacked title textcolor lt -1
set datafile missing '-'
set datafile separator ';'
set style data histograms
set xtics border in scale 0,0 nomirror rotate by -45  autojustify
set xtics  norangelimit
set xtics  ()
set xlabel "Weeks"
set ylabel "Unique Downloads"
set title "SNAP unique downloads" 
plot for [COL=2:5:1] 'output/unique_downloads.dat' using COL:xticlabels(1)
