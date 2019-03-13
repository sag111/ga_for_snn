from sys import argv
import numpy

accs = numpy.loadtxt(argv[1]) #'models/output/accuracy_vs_generation.txt'
# create a structured array
dtype = [
	('generation', int),
	('f1-mean', float),
	('f1-std', float),
	('f1-lowest', float),
	('f1-highest', float),
]
accs = numpy.array([tuple(line) for line in accs], dtype=dtype)

accs = numpy.sort(
	accs,
	order=['f1-mean', 'f1-highest', 'f1-lowest'],
	axis=0)

print('# generation mean std lowest highest')
print(accs[-1])
