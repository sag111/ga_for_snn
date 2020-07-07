set term png size 800, 800
set output 'accuracy_vs_generation.png'

set xlabel 'Поколение'
set ylabel 'F1-score, %'

set xtics 1
set xrange [-0.5:]

plot 'train_accuracy_vs_generation.txt' using 1:($2-$3):4:5:($2+$3) with candlesticks title 'Train' whiskerbars, \
	  'test_accuracy_vs_generation.txt' using 1:($2-$3):4:5:($2+$3) with candlesticks title 'Test' whiskerbars
