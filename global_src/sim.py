import sys
import os
import os.path # for isfile('input/weight_initial.txt')
import time # for proper randomization
import numpy

import nest

# Reading parameters.
sys.path.append('.')
from parameters.parameters_network import network_parameters
from parameters.parameters_synapse import synapse_parameters
from parameters.parameters_neuron import neuron_parameters

nest.SetKernelStatus({
	'resolution': 0.1,
	'local_num_threads': 1,
	# a truly random number generator, not dependent on the time
	'rng_seeds': [int.from_bytes(os.urandom(4), sys.byteorder)] # expects a list with a seed for each thread
})
nest.sli_run('M_ERROR setverbosity') # setting quiet mode

# Reading input data.
input_masks = numpy.loadtxt('input/mask.txt')
number_of_inputs = len(input_masks[0]) * network_parameters['inputs_per_component']
number_of_excitatory_inputs = number_of_inputs - network_parameters['number_of_inhibitory_inputs']
input_rates = [[0.0] * number_of_inputs for input_mask in input_masks]
for vector_number in range(len(input_masks)):
	for component_number in range(number_of_inputs):
		input_rates[vector_number][component_number] = (
			network_parameters['low_input_rate'] +
			input_masks[vector_number][
				component_number // network_parameters['inputs_per_component']
			] * (
				network_parameters['high_input_rate'] - network_parameters['low_input_rate']
			)
		)

# Establishing the network.
neuron_id = nest.Create('iaf_psc_exp', params=neuron_parameters)

generators_ids = nest.Create('poisson_generator', number_of_inputs)
# Uncomment to read input spike trains from file
# instead of generating on the fly
# generators_ids = nest.Create('spike_generator', number_of_inputs)
# nest.SetStatus(
# 	generators_ids,
# 	[
# 		{'spike_times': numpy.loadtxt('input/input'
# 				+ str(input_number) + '.txt')
# 		}
# 		for input_number in range(inputs_ids)
# 	]
# )

inputs_ids = nest.Create('parrot_neuron', number_of_inputs)
nest.Connect(generators_ids, inputs_ids, 'one_to_one', syn_spec='static_synapse')
exc_inputs_ids = inputs_ids[0 : number_of_excitatory_inputs]
if number_of_excitatory_inputs < number_of_inputs:
	inh_inputs_ids = inputs_ids[number_of_excitatory_inputs
								: number_of_inputs]
nest.Connect(exc_inputs_ids, neuron_id, conn_spec = 'all_to_all', syn_spec=synapse_parameters)
synapses_ids = nest.GetConnections(exc_inputs_ids)
if number_of_excitatory_inputs < number_of_inputs:
	nest.Connect(
		inh_inputs_ids,
		neuron_id,
		conn_spec = 'all_to_all',
		syn_spec = {
			'model': 'static_synapse',
			'weight': -1.0
		}
	)

# Allow for the case this is the testing stage.
testing_is_now = False
if os.path.isfile('input/weight_initial.txt'):
	testing_is_now = True
	nest.SetStatus(
		synapses_ids,
		'weight',
		list(numpy.loadtxt('input/weight_initial.txt'))
	)

detector_id = nest.Create('spike_detector')
nest.Connect(neuron_id, detector_id, syn_spec = 'static_synapse')

# The simulation itself.
weights_outfile = open('weights.txt', 'w')
rate_outfile = open('out_rate.txt', 'w')
total_time_elapsed = 0
for epochs_elapsed in range(
	int(numpy.ceil(
		network_parameters['time_max']
		/ network_parameters['one_vector_longtitude']
		/ len(input_rates)
	))
):
	# Because of the for loop below,
	# time is rounded to full epochs even if it would be higher than time_max.
	for current_input_vector in input_rates:
		# We start with writing down the weights
		# so that the initial weights are also saved.
		if (
			int(total_time_elapsed)
			% int(network_parameters['weights_watching_step'])
		) == 0 and not testing_is_now:
			# This way, weights cannot be printed more often than
			# once per input vector. Address this later if relevant.
			# If smooth weight history is needed, as a temporary
			# workaround duplicate vectors in input/mask.txt
			# with little one_vector_longtitude.
			#
			# During testing, weights are not printed
			# as they exhibit no change.
			current_weights = nest.GetStatus(synapses_ids, keys = 'weight')
			for word in current_weights:
				print(word, end=' ', file=weights_outfile)
			print('', file=weights_outfile, flush=True)

		# The simulation itself.
		nest.SetStatus(generators_ids, [{'rate': r} for r in current_input_vector])
		nest.Simulate(network_parameters['one_vector_longtitude'])

		if testing_is_now:
			output_spikes = nest.GetStatus(
				detector_id, keys = 'events'
			)[0]['times']
			print(
				1000.0 * len(output_spikes)
					/ network_parameters['one_vector_longtitude'],
				file=rate_outfile,
				flush=True
			)
			# Empty the detector.
			nest.SetStatus(detector_id, {'n_events': 0})

		if sys.stdout.isatty():
			# Output is to a terminal,
			# so it makes sense to show progress.
			sys.stdout.write(
				'\r' + str(
					100.0
					* total_time_elapsed
					/ network_parameters['time_max']
				) + '% done                          '
			)

		total_time_elapsed += network_parameters['one_vector_longtitude']

	# Stop if the weights have converged to their boundary values.
	if (not testing_is_now) and (
		sum([w < 0.1 for w in current_weights])
		+ sum([w > 0.9 for w in current_weights])
		== number_of_inputs
	):
		print('Early stopping on weights convergence to 0 or 1.')
		break

weights_outfile.close()
rate_outfile.close()
