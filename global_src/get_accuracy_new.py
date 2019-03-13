from subprocess import check_output
import numpy
import sklearn.metrics

number_of_classes = int(check_output(
	'echo neuron*-freqs_train.txt | wc -w',
	shell=True
))
# Read the frequencies in response to all the vectors.
freqs = {}
items_per_class = {
	train_or_test: [
		len(numpy.loadtxt(
			'../' # out of Testing
			+ train_or_test + '_data/'
			+ 'mask_class' + str(current_class) + '.txt'
		))
		for current_class in range(number_of_classes)
	]
	for train_or_test in ('train', 'test')
}
correct_classes = {
	train_or_test: numpy.concatenate([
		# because instances in the test set come ordered
		[class_] * items_per_class[train_or_test][class_]
		for class_ in range(number_of_classes)
	])
	for train_or_test in ('train', 'test')
}
for train_or_test in ('train', 'test'):
	freqs[train_or_test] = [
		numpy.loadtxt('neuron' + str(neu) + '-freqs_' + train_or_test + '.txt')
		for neu in range(number_of_classes)
	]

votes_for_classes = {
	# votes[train_or_test] should have the shape
	# (number of vectors, len(classes_order)):
	# votes[vector_number] == (
	# 	votes_for_class_1,
	# 	...,
	# 	votes_for_class_N
	# )
	train_or_test: numpy.array([
		[0] * number_of_classes
		for i in range(
			sum(items_per_class[train_or_test])
		)
	])
	for train_or_test in ('train', 'test')
}

# Get (number_of_classes)**2 mean frequencies: of each neuron, in
# response to each class (averaged over all the vectors of the
# class). We will further compare the frequency in response to
# each particular vector to the ranges of these mean frequencies.
mean_train = [
	[
		numpy.mean(
			freqs['train'][neu][
				# Select output in response to class class_
				correct_classes['train'] == class_
			]
		)
		for class_ in range(number_of_classes)
	]
	for neu in range(number_of_classes)
]

def get_y_pred(votes, classes_order=list(range(number_of_classes))):
	'''
	votes should have the shape
	(number of vectors, len(classes_order)):
	votes[vector_number] == (
		votes_for_class_1,
		...,
		votes_for_class_N
	)
	'''
	return numpy.array([
		classes_order[numpy.argmax(current_vector_votes)]
		for current_vector_votes in votes
	])

for train_or_test in ('train', 'test'):
	print('On the', train_or_test, 'set:')

	# Sort the neurons by how well they distinguish
	# their classes from not theirs.
	def diffs_square_sum(current_class):
		return sum([
			(mean_train[current_class][current_class]
				- mean_train[current_class][other_class])**2
			for other_class in range(number_of_classes)
		])

	n = len(correct_classes[train_or_test])
	for vector_number in range(n):
		for current_class in range(number_of_classes):
			votes_for_classes[train_or_test][vector_number][current_class] -= abs(
				freqs[train_or_test][current_class][vector_number] - mean_train[current_class][current_class]
			) #/ (diffs_square_sum(current_class) / 1e+6)

	y_true = correct_classes[train_or_test]
	y_pred = get_y_pred(votes_for_classes[train_or_test])

	print(sklearn.metrics.classification_report(
		y_true=y_true,
		y_pred=y_pred
	))
	print(
		sklearn.metrics.f1_score(
			y_true=y_true,
			y_pred=y_pred,
			average='macro'
		),
		file=open(train_or_test + '_accuracy.txt', 'w')
	)
