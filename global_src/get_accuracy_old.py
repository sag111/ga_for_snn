from subprocess import check_output
import numpy
import sklearn.metrics

number_of_classes = int(check_output(
	'echo neuron*-freqs_train.txt | wc -w',
	shell=True
))
# Read the frequencies in response to all the vectors.
freqs = {}
correct_classes_train_and_test = {}
for train_or_test in ('train', 'test'):
	freqs[train_or_test] = [
		numpy.loadtxt('neuron' + str(neu) + '-freqs_' + train_or_test + '.txt')
		for neu in range(number_of_classes)
	]

	items_per_class = [
		len(numpy.loadtxt(
			'../'  # out of 'Testing'
			+ train_or_test + '_data/'
			+ 'mask_class' + str(current_class) + '.txt'
		))
		for current_class in range(number_of_classes)
	]
	correct_classes_train_and_test[train_or_test] = numpy.concatenate([
		# because instances in the test set come ordered
		[i] * items_per_class[i]
		for i in range(number_of_classes)
	])

# Get (number_of_classes)**2 mean frequencies: of each neuron, in
# response to each class (averaged over all the vectors of the
# class). We will further compare the frequency in response to
# each particular vector to the ranges of these mean frequencies.
mean_train = [
	[
		numpy.mean(
			freqs['train'][neu][
				# Select output in response to class class_
				correct_classes_train_and_test['train'] == class_
			]
		)
		for class_ in range(number_of_classes)
	]
	for neu in range(number_of_classes)
]

for train_or_test in ('train', 'test'):
	print('On the', train_or_test, 'set:')

	correct_classes = correct_classes_train_and_test[train_or_test]
	
	# Sort the neurons by how well they distinguish
	# their classes from not theirs.
	def diffs_square_sum(current_class):
		return sum([
			(mean_train[current_class][current_class]
				- mean_train[current_class][other_class])**2
			for other_class in range(number_of_classes)
		])

	neurons_credibility_order = sorted(
		list(range(number_of_classes)),
		key=diffs_square_sum,
		reverse=True
	)
	print('Order of neurons by credibility: ',
		neurons_credibility_order)


	def inside_this_class(current_class, item_number):
		"""
		Returns whether the output rate in response to item_number
		lies inside the range of the response of current_class neuron
		to the train test of current_class.

		By "inside" we mean not farther than half the distance
		to the closest other class.
		"""

		other_classes = list(range(number_of_classes))
		other_classes.pop(current_class)

		# boundary is set in the middle between current_class
		# and the closest of the other_classes
		boundary = min([
			abs(mean_train[current_class][current_class]
				- mean_train[current_class][other_class]
			) / 2
			for other_class in other_classes
		])

		return abs(freqs[train_or_test][current_class][item_number] - mean_train[current_class][current_class]) < boundary

	# Use first the best performing neurons
	# to identify their classes,
	# then assign the remaining items to the worst neuron's class.
	n = len(correct_classes)
	classes = [0] * n
	for i in range(n):
		classes[i] = neurons_credibility_order[-1]
		for neu in reversed(neurons_credibility_order):
			if inside_this_class(neu, i):
				classes[i] = neu

	print(sklearn.metrics.classification_report(
		y_true=correct_classes,
		y_pred=classes
	))
	print(
		sklearn.metrics.f1_score(
			y_true=correct_classes,
			y_pred=classes,
			average='macro'
		),
		file=open(train_or_test + '_accuracy.txt', 'w')
	)
