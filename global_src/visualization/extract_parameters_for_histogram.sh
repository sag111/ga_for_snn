if test $# = 1
then
	acceptable_accuracy=$1
else
	echo Usage: $0 acceptable_accuracy >&2
	acceptable_accuracy=0.85
fi

collect_parameters () {
	outdir=$1/
	dirs_to_collect_from=$2

	if test -d $outdir
	then
		rm -r $outdir
	fi
	mkdir $outdir

	python <<END_TO_PYTHON
import sys
sys.path.append('./src/')
from parameters import traits
import numpy as np
for current_traits in (
	traits.network_traits, 
	traits.neuron_traits, 
	traits.synapse_traits
):
	for parameter_name in current_traits:
		if (current_traits[parameter_name]['mutation_prob'] > 0
		and current_traits[parameter_name]['details']['max'] != current_traits[parameter_name]['details']['min']):
			print(
				'#', 'generation', parameter_name,
				'\n#',
				'min:', current_traits[parameter_name]['details']['min'],
				'max:', current_traits[parameter_name]['details']['max'],
				file=open(
					'$outdir/'
					'parameter_' + parameter_name + '-good_values_for_histogram.txt',
					'w'
				),
				sep='\t'
			)
END_TO_PYTHON
	pars=`
		for f in $outdir/parameter_*-good_values_for_histogram.txt
		do
			par_name=${f#$outdir/parameter_}
			par_name=${par_name%-good_values_for_histogram.txt}
			echo $par_name
		done
	`

	for current_dir in $dirs_to_collect_from
	do
		if ! test -f $current_dir/mean_test_accuracy.txt
		then
			continue
		fi

		if python <<-END_TO_PYTHON
				acc = float(
					open('$current_dir/mean_train_accuracy.txt').readline().split()[0]
				)
				exit(0) if acc > $acceptable_accuracy else exit(1)
			END_TO_PYTHON
		then
			good_or_bad_group=good
		else
			good_or_bad_group=bad
		fi

		# Extract the mean accuracy to a separate file, so that
		# this file contains the accuracies in the same order in which
		# the parameters will be stored below.
		tr -s ' \t' '\n' < $current_dir/mean_test_accuracy.txt | head -n 1 >> $outdir/${good_or_bad_group}_accuracy_for_histogram.txt

		for par in $pars
		do
			outfile=$outdir/parameter_${par}-${good_or_bad_group}_values_for_histogram.txt

			# Commented out until we completely switch to new,
			# dictionary-based parameter format.
			#cat $current_dir/parameters/parameters* | grep [\'\"]$par[\'\"]: | tr -s ' ,:' '\n' | tail -n 1 >> $outfile
			cat $current_dir/parameters/parameters* | grep $par | tr -s ' ,=' '\n' | tail -n 1 >> $outfile
		done

		for good_or_bad_group in good bad
		do
			python > $outdir/parameter_${par}-${good_or_bad_group}_histogram.txt <<END_TO_PYTHON
import numpy as np
values = np.loadtxt(
	'$outdir/'
	'parameter_${par}-${good_or_bad_group}_values_for_histogram.txt'
)
if len(values) == 0:
	# The file is empty.
	exit()
hist, bins = np.histogram(values)

# To get a normed histogram
l = len(values)

# For gnuplot to fully draw the first bin
print(min(values) - bins[0]/100, 0)

for i in range(len(hist)):
	print(bins[i], hist[i] / l)

# For gnuplot to fully draw the last bin
print(max(values), 0)
END_TO_PYTHON
		done
	done
}  # end of function definition

collect_parameters "models/output/histograms_of_parameters-all_generations" "models/output/generation*_best_genome/"
collect_parameters "models/output/histograms_of_parameters-last_generation" "models/genome*/"
collect_parameters "models/output/histograms_of_parameters-best_genome" "models/output/best_genome/"
