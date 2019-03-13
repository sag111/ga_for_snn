cd models/output

python <<END_TO_PYTHON
import sys
sys.path.append('../../src/')
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
					'parameter_' + parameter_name + '_vs_generation.txt',
					'w'
				)
			)
END_TO_PYTHON
pars=`
	for f in parameter_*_vs_generation.txt
	do
		par_name=${f#parameter_}
		par_name=${par_name%_vs_generation.txt}
		echo $par_name
	done
`

for train_or_test in 'train' 'test'
do
	echo '#' generation mean std min max > ${train_or_test}_accuracy_vs_generation.txt
	for current_dir in generation*_best_genome
	do
		generation=${current_dir%_best_genome}
		generation=${generation#generation}

		echo -ne $generation '\t'
		cat $current_dir/mean_${train_or_test}_accuracy.txt
	done | sort -n > ${train_or_test}_accuracy_vs_generation.txt

	{
		echo "# ${train_or_test}: best_generation mean std min max"
		src_path=${0%/*}
		python $src_path/get_highest_accuracy.py ${train_or_test}_accuracy_vs_generation.txt | tr -s '(,)' ' '
	} >&3
done 3>best_accuracy_ever.txt

# Get the generation with the best train accuracy.
if test -L best_genome
then
	# Delete the symbolic link if it exists.
	rm best_genome
fi
best_train_accuracy=`python $src_path/get_highest_accuracy.py train_accuracy_vs_generation.txt | tr -s '(,)' ' ' | tail -n 1`
best_generation=`echo $best_train_accuracy | cut --delimiter=' ' --fields=1`
ln --symbolic --force generation${best_generation}_best_genome best_genome

for par in $pars
do
	{
		echo '#' generation $par
		for current_dir in generation*_best_genome
		do
			generation=${current_dir%_best_genome}
			generation=${generation#generation}

			echo -ne $generation '\t'
			# Commented out until we completely switch to new,
			# dictionary-based parameter format.
			#cat $current_dir/parameters/parameters* | grep [\'\"]$par[\'\"]: | tr -s ' ,:' '\n' | tail -n 1
			cat $current_dir/parameters/parameters* | grep $par | tr -s ' ,=' '\n' | tail -n 1
		done | sort -n
	} > parameter_${par}_vs_generation.txt
done
