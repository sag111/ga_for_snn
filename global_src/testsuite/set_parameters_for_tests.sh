# This is the global configuration for all test runs.
# Specific test scripts may in addition make
# their own alterations to the code.

if ! test -d src
then
	echo src/ not found; $0 should be invoked from the project root directory. >&2
	exit 1
fi


# Disable cluster-specific environment bootstrapping.
sed -i "s/source .*/#source /" src/run_an_mpi_job.py

# Disable cross-validation.
sed -i "s/fold\*/fold0/" src/train_and_test.sh

# Set the number of generations to 1.
cat >> src/parameters/genetic_network_parameters.py <<-END_TO_CAT
	# Appended by the test script
	# for the debugging purpose.
	max_generations = 1
END_TO_CAT

# Set the number of genomes in a generation to 1.
sed -i "s/PopulationSize .*/PopulationSize 1/" src/parameters/neat_parameters.txt

# Decrease the simulation time.
cat >> src/parameters/traits.py <<-END_TO_CAT
	# Appended by the test script
	# for the debugging purpose.
	network_traits['time_max'] = {
		'details': {
			# Decrease the simulation time.
			'max': int(1e+4),
			'min': int(1e+4),
			'mut_power': int(1e+6),
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 0,
		'mutation_prob': 0,
		'type': 'int'
	}
	network_traits['one_vector_longtitude'] = {
		'details': {
			# Decrease the simulation time.
			'max': 1000,
			'min': 1000,
			'mut_power': 1000,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 0,
		'mutation_prob': 0,
		'type': 'int'
	}
	synapse_traits['lambda'] = {
		'details': {
			'max': 0.1,
			'min': 0.1,
			'mut_power': 0.001, # the highest possible amount of change during one mutation
			'mut_replace_prob': 0.25 # if mutated, the probability to be re-initialized to a random value, rather than changed by a random value proportional to mut_power
		},
		'importance_coeff': 0, # the trait value is multiplied by importance_coeff when calculating distance between genomes
		'mutation_prob': 0,
		'type': 'float'
	}

END_TO_CAT
