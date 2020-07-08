import sys
from os import system, chdir, getcwd

from concurrent.futures import ProcessPoolExecutor as ChosenParallelExecutor
#from mpi4py.futures import MPIPoolExecutor as ChosenParallelExecutor
import MultiNEAT as neat

src_path = sys.argv[0]
# Strip the filename to leave path only.
src_path = src_path[:src_path.rfind('/')]
parameters_path = getcwd() + '/../src/'  # out of 'models/'

# Read MultiNEAT parameters.
neat_params = neat.Parameters()
# Strip off the comment lines starting with //
system(
	"grep -v '//' < "
	+ parameters_path + '/parameters/neat_parameters.txt | grep . >'
	+ parameters_path + '/parameters/neat_parameters.filtered.txt'
)
neat_params.Load(parameters_path + '/parameters/neat_parameters.filtered.txt')
system('rm ' + parameters_path + '/parameters/neat_parameters.filtered.txt')

# Read the SNN parameters to be searched by MultiNEAT
# from traits.py.
sys.path.append(parameters_path)
from parameters import traits
for trait_name, trait_value in traits.network_traits.items():
	neat_params.SetGenomeTraitParameters(trait_name, trait_value)
for trait_name, trait_value in traits.neuron_traits.items():
	# change to SetNeuronTraitParameters to let the neuron parameters mutate individually for each neuron
	neat_params.SetGenomeTraitParameters(trait_name, trait_value)
for trait_name, trait_value in traits.synapse_traits.items():
	# change to SetLinkTraitParameters to let the synapse parameters mutate individually for each synapse
	neat_params.SetGenomeTraitParameters(trait_name, trait_value)

# Read the parameters of network created inside MultiNEAT.
from parameters import genetic_network_parameters

genome = neat.Genome(
	0, # Some genome ID, I don't know what it means.
	genetic_network_parameters.inputs_number,
	2, # ignored for seed_type == 0, specifies number of hidden units if seed_type == 1
	genetic_network_parameters.outputs_number,
	False, #fs_neat. If == 1, a minimalistic perceptron is created: each output is connected to a random input and the bias.
	neat.ActivationFunction.UNSIGNED_SIGMOID, # output neurons activation function
	neat.ActivationFunction.UNSIGNED_SIGMOID, # hidden neurons activation function
	0, # seedtype
	neat_params, # global parameters object returned by neat.Parameters()
	0 # number of hidden layers
)

population = neat.Population(
	genome,
	neat_params,
	True, # whether to randomize the population
	0.5, # how much to randomize
	0 # the RNG seed
)

def evaluate(genome, specimen_number, executor):
	current_trait_values = genome.GetGenomeTraits()
	network_trait_values = {trait_name: trait_value
		for trait_name, trait_value in current_trait_values.items()
			if trait_name in traits.network_traits
	}
	neuron_trait_values = {trait_name: trait_value
		for trait_name, trait_value in current_trait_values.items()
			if trait_name in traits.neuron_traits
	}
	synapse_trait_values = {trait_name: trait_value
		for trait_name, trait_value in current_trait_values.items()
			if trait_name in traits.synapse_traits
	}

#	workdir = getcwd()
	system('''
		if test -d genome{number:d} ;
		then
			rm -r genome{number:d} ;
		fi ;
		mkdir genome{number:d}
	'''.format(number=specimen_number)
	)
	chdir(
		'genome{number:d}'.format(number=specimen_number)
	)
	system('mkdir parameters')
	traits.write_parameters_file(
		open('parameters/parameters_network.py', 'w'),
		network_trait_values,
		'network_parameters'
	)
	traits.write_parameters_file(
		open('parameters/parameters_neuron.py', 'w'),
		neuron_trait_values,
		'neuron_parameters'
	)
	traits.write_parameters_file(
		open('parameters/parameters_synapse.py', 'w'),
		synapse_trait_values,
		'synapse_parameters'
	)

#	executor.submit(simulate,
#			workdir + '/genome' + str(specimen_number)
#	)
	chdir('..') # out of genome*

#def simulate(directory_name):
#	system(
#		'cd ' + directory_name + ' ; '
#		'sh ../../src/train_and_test.sh > out.txt 2>err.txt'
#	)

system("""
	if ! test -d output/
	then
		mkdir output
	fi
""")
outfile = open('output/fitness.txt', 'w')

for generation_number in range(genetic_network_parameters.max_generations):

	genome_list = neat.GetGenomeList(population)

	with ChosenParallelExecutor(max_workers=1) as executor:
		for specimen_number, genome in enumerate(genome_list):
			# cannot use map() because it does not actually compute evaluate(),
			# just returns an iterator object instead
			evaluate(genome, specimen_number, executor)
	system(
		'mpirun -np '
		+ str(len(genome_list))
		+ ' python ' + src_path + '/run_an_mpi_job.py'
	)
	fitnesses_list = [
		float(open('genome' + str(specimen_number) + '/mean_fitness.txt').readline())
		for specimen_number in range(len(genome_list))
	]
	fitnesses_list = list(fitnesses_list) # because map() returns an iterator
	
	neat.ZipFitness(genome_list, fitnesses_list)
	
	if generation_number % genetic_network_parameters.result_watching_step == 0:
		best_genome = population.GetBestGenome()
		best_genome.Save('output/best_genome.txt')
		with open('output/best_genome.txt', 'a') as genomefile:
			genomefile.write(
				'\n' + str(best_genome.GetNeuronTraits())
				+ '\n' + str(best_genome.GetGenomeTraits())
			)
			genomefile.close()

		# We need to call argmax on fitnesses to get the index of the
		# best genome, rather than just picking genome0. Indeed, the
		# genomes will be sorted by fitness at population.Epoch()
		# call, but this call will at the same time do mutations, so
		# we'll only be able to get the best fitness, but not the
		# best parameters.
		best_specimen_number = max(
			list(range(len(genome_list))),
			key=lambda i: fitnesses_list[i]
		)
		system('cp -R -T '
		# -T is to remove output/generation* if it already exists
			+ 'genome' + str(best_specimen_number)
			+ ' output/generation' + str(generation_number) + '_best_genome'
		)

	outfile.write(
		str(generation_number)
		+ '\t' + str(max(fitnesses_list))
		+ '\n'
	)
	outfile.flush()
	sys.stderr.write(
		'\rGeneration ' + str(generation_number)
		+ ': fitness = ' + str(population.GetBestGenome().GetFitness())
	)

	# advance to the next generation
	population.Epoch()
