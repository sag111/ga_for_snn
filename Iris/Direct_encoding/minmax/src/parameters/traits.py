"""
The parameters to be adjusted by MultiNEAT,
in the format MultiNEAT expects:

parameter_name = {
	'details': {
		'max'
		'min'
		'mut_power'  # the highest possible amount of change during one mutation
		'mut_replace_prob'  #  if mutated, the probability to be re-initialized to a random value, rather than changed by a random value proportional to mut_power
	},
	'importance_coeff'  # the trait value is multiplied by importance_coeff when calculating distance between genomes
	'mutation_prob': 0
	'type'
}

"""

# Network parameters
# ------------------
#	time_max: 10000000 # [ms]
#	one_vector_longtitude: 2000 # [ms] one input vector presenting duration
#	high_input_rate: 50 # [Hz], frequency coding an input vector component of 1
#	low_input_rate: 0 # [Hz], frequency coding an input vector component of 0
#	weights_watching_step: 1000 # [ms]
#	number_of_inputs: 100
#	number_of_excitatory_inputs: 100
#	weight_initial_mean: 0.3
#	weight_initial_sigma: 0.01
#	dataset: {'Iris', 'Digits', 'Wisconsin', 'MNIST'}
#	normalize: 'L2', 'L1', 'minmaxscale', None
#	gaussian_encoding: True

network_traits = {
	'time_max': {
		'details': {
			'max': int(3e+6),
			'min': int(3e+6),
			'mut_power': int(1e+6),
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'int'
	},

	'one_vector_longtitude': {
		'details': {
			'max': 1000,
			'min': 1000,
			'mut_power': 1000,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'int'
	},

	'high_input_rate': {
		'details': {
			'max': 500.0,
			'min': 50.0,
			'mut_power': 20.0,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0.1,
		'type': 'float'
	},

	'low_input_rate': {
		'details': {
			'max': 20.0,
			'min': 0.0,
			'mut_power': 1.0,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0.1,
		'type': 'float'
	},

	'weights_watching_step': {
		'details': {
			'max': 1000,
			'min': 1000,
			'mut_power': 500,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'int'
	},

	'receptive_fields_per_component': {
		'details': {
			'max': 16,
			'min': 16,
			'mut_power': 5,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'int'
	},

	'inputs_per_component': {
		'details': {
			'max': 25,
			'min': 10,
			'mut_power': 1,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0.1,
		'type': 'int'
	},

	'number_of_inhibitory_inputs': {
		'details': {
			'max': 0,
			'min': 0,
			'mut_power': 5,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'int'
	},

	'dataset': {
		'details': {
			'set': ['"Iris"'],
			'probs': [1.0], # if mutated, the new value is chosen by a roulette according to these probs
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'str'
	},

	'normalize': {
		'details': {
			'set': ["'minmaxscale'"],
			'probs': [1.0], # if mutated, the new value is chosen by a roulette according to these probs
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 10.0,
		'mutation_prob': 0,
		'type': 'str'
	},

	'gaussian_encoding': {
		'details': {
			'set': ["False"],
			'probs': [1.0], # if mutated, the new value is chosen by a roulette according to these probs
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 10.0,
		'mutation_prob': 0,
		'type': 'str'
	},
}


# Neuron parameters
# -----------------
#	V_m: -70.0 # [mV], initial membrane potential
#	E_L: -70.0 # [mV], leak reversal
#	C_m: 2.0 # [pF]
#	t_ref: 3.0 # [ms]
#	tau_m: 10.0 # [ms]
#	V_th: -54.0
#	tau_syn_ex: 5.0
#	tau_syn_in: 5.0
#	I_e: 0.0 # external stimulation current
#	tau_minus: 20.0 # [ms], an STDP parameter. In NEST belongs to the neuron for technical reasons.

neuron_traits = {

	# The initial membrane potential V_m is always
	# equal to E_L, not to be mutable, so skipped there.

	'E_L': {
		'details': {
			'max': -70.0,
			'min': -70.0,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},
	
	'C_m': {
		'details': {
			'max': 3.0,
			'min': 1.0,
			'mut_power': 0.1,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0.1,
		'type': 'float'
	},

	't_ref': {
		'details': {
			'max': 3.0,
			'min': 3.0,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},

	'tau_m': {
		'details': {
			'max': 10.0,
			'min': 10.0,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},

	'V_th': {
		'details': {
			'max': -54.0,
			'min': -54.0,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},

	'tau_syn_ex': {
		'details': {
			'max': 5.0,
			'min': 5.0,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},

	'tau_syn_in': {
		'details': {
			'max': 5.0,
			'min': 5.0,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},

	'I_e': {
		'details': {
			'max': 0.0,
			'min': 0.0,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},

	'tau_minus': {
		'details': {
			'max': 100.0,
			'min': 1.0,
			'mut_power': 1.0,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0.1,
		'type': 'float'
	},

}


# Synapse parameters
# ------------------
# 	Wmax
# 	lambda
# 	alpha
# 	mu_plus
# 	mu_minus
# 	tau_plus
# 	model

synapse_traits = {
	
	# Wmax is always 1, not supposed to be mutable
	'Wmax': {
		'details': {
			'max': 1,
			'min': 1,
			'mut_power': 0,
			'mut_replace_prob': 0
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},
	
	'lambda': {
		'details': {
			'max': 0.001,
			'min': 0.001,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},

	'alpha': {
		'details': {
			'max': 2.0,
			'min': 0.3,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0.1,
		'type': 'float'
	},

	'mu_plus': {
		'details': {
			'max': 0.0,
			'min': 0.0,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},

	'mu_minus': {
		'details': {
			'max': 0.0,
			'min': 0.0,
			'mut_power': 0.001,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'float'
	},

	'tau_plus': {
		'details': {
			'max': 100.0,
			'min': 1.0,
			'mut_power': 1.0,
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0.1,
		'type': 'float'
	},

	'model': {
		'details': {
			'set': ['"stdp_nn_restr_synapse"'],
			'probs': [1.0], # if mutated, the new value is chosen by a roulette according to these probs
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'str'
	},

	'weight': {
		'details': {
			'set': ['''{
				'distribution': 'uniform',
				'low': 0.0,
				'high': 1.0
			}'''],
			'probs': [1.0],
			'mut_replace_prob': 0.25
		},
		'importance_coeff': 1.0,
		'mutation_prob': 0,
		'type': 'str'
	}
}

def write_parameters_file(outfile, trait_values, title):
	print(title, '=', '{', file=outfile)
	for trait_name, trait_value in trait_values.items():
		print(
			"\t'" + trait_name + "':",
			str(trait_value) + ',',
			file=outfile
		)
	print('}', file=outfile)
