from subprocess import check_output
import numpy

acc_on_train = numpy.loadtxt('train_accuracy.txt')
if acc_on_train > 0.3:
	print(1.e+6 * acc_on_train)
	exit()


number_of_classes = int(check_output(
	'echo neuron*-freqs_train.txt | wc -w',
	shell=True
))
# Read the frequencies in response to all the vectors.
freqs = {}
for train_or_test in ('train', 'test'):
	freqs[train_or_test] = [
		numpy.loadtxt('neuron' + str(neu) + '-freqs_' + train_or_test + '.txt')
		for neu in range(number_of_classes)
	]

# Fitness is calculated on the response to the train set.
train_or_test = 'train'
# Look how many vectors 0-th neuron received.
# Though the classes may be uneven, during testing all neurons
# must have received equal number of instances.
total_set_length = len(freqs[train_or_test][0])

items_per_class = [
	len(numpy.loadtxt(
		'../'  # out of 'Testing'
		+ train_or_test + '_data/'
		+ 'mask_class' + str(current_class) + '.txt'
	))
	for current_class in range(number_of_classes)
]

correct_classes = numpy.concatenate([
	# Instances in the test set come ordered
	[i] * items_per_class[i]
	for i in range(number_of_classes)
])

fitness = sum([
	sum([
		abs(
			freqs['train'][
				correct_classes[item]
			][item]
			- freqs['train'][other_neuron][item]
		)
		for other_neuron in range(number_of_classes)
	])
	for item in range(total_set_length)
])

print(fitness)
