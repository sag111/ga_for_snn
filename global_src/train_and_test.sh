# 1. Prepare the dataset: normalize, split into folds.
# 2. Train
# 3. Test
# 4. Calculate accuracy
#
# Prerequisites: parameters/, supposedly created
# by the genetic algorithm, must exist
# in the current directory.
#
# Output: mean_fitness.txt, accuracies.txt


# Setting SRC_PATH to where this script resides,
# as here all the other ones probably reside.
my_name=${0##*/}
SRC_PATH=${0%/$my_name}
# Replace the relative path with the absolute.
pushd $SRC_PATH
SRC_PATH="`pwd`"
popd


# Prepare the dataset: normalize, split into folds.
# This creates folders fold0/, ..., fold5/,
# with train_data/ and test_data/ in each folder.
if ! test -d fold0/train_data
then
	python $SRC_PATH/split_data.py
else
	echo Encoded data already exists.
fi

neurons=`
	for f in fold0/train_data/mask_class*.txt
	do
		neu=${f#fold0/train_data/mask_class}
		neu=${neu%\.txt}
		echo $neu
	done | tr -s '[:alpha:]/_.' ' '
`

for fold in fold*
do
(
	cd $fold/

	# 2. Training
	# -----------

	if test -d Training
	then
		echo Training not needed for $fold, directory already exists.
	else
		mkdir Training
		cd Training

		for neu in $neurons
		do
		(
			if test -d Neuron$neu
			then
				rm -r Neuron$neu
			fi
			mkdir Neuron$neu
			cd Neuron$neu

			# this fold' data is
			# out of Neuron$neu, then out of Training/Testing, in fold*
			data_path=../..

			# this genome' parameters/ are
			# out of Neuron$neu, then out of Training/Testing, then out of fold*
			cp -R $data_path/../parameters ./parameters

			mkdir input
			cp $data_path/train_data/mask_class$neu.txt input/mask.txt

			python $SRC_PATH/sim.py

			cd .. # out of Neuron$neu
		) &
		done
		wait # for python $SRC_PATH/sim.py
		
		cd .. # out of Training
	fi

	# 3. Testing
	# ----------

	if test -d Testing
	then
		echo Testing not needed for $fold, directory already exists.
	else
		mkdir Testing
		cd Testing

		for neu in $neurons
		do
		(
			if test -d Neuron$neu
			then
				rm -r Neuron$neu
			fi
			mkdir Neuron$neu
			cd Neuron$neu

			# this fold' data is
			# out of Neuron$neu, then out of Training/Testing, in fold*
			data_path=../..

			# this genome' parameters/ are
			# out of Neuron$neu, then out of Training/Testing, then out of fold*
			cp -R $data_path/../parameters ./parameters

			# Alter a few network parameters for testing.
			cat >> parameters/parameters_synapse.py <<-'END_TO_CAT'
				#
				# Turn off STDP for the testing stage.
				synapse_parameters['lambda'] = 0
			END_TO_CAT
			cat >> parameters/parameters_network.py <<-'END_TO_CAT'
				#
				# Override a few parameters for the testing stage.
				# ------------------------------------------------
				# Must be enough to estimate the mean output rate
				# in response to a vector.
				network_parameters['one_vector_longtitude'] = 2000 # [ms]
				network_parameters['weights_watching_step'] = network_parameters['one_vector_longtitude'] # [ms]
			END_TO_CAT

			mkdir input
			# Pick the weights obtained during training.
			trained_weights_file=$data_path/Training/Neuron$neu/weights.txt
			if ! test -f $trained_weights_file
			then
				echo -n $trained_weights_file not found, testing aborted. >&2
				exit 1
			fi
			tail -n 2 $trained_weights_file | head -n 1 > input/weight_initial.txt
			

			# Testing on the training set, and then on the testing set.
			for train_or_test in 'train' 'test'
			do
				cat $data_path/${train_or_test}_data/mask_class*.txt > input/mask.txt

				# Set the correct simulation duration.
				whole_set_size=`wc -l < input/mask.txt`
				cat >> parameters/parameters_network.py <<-END_TO_CAT
					# Only one cycle of data presenting should take place.
					network_parameters['time_max'] = $whole_set_size * network_parameters['one_vector_longtitude'] # [ms]
				END_TO_CAT

				python $SRC_PATH/sim.py

				mv out_rate.txt ../neuron$neu-freqs_${train_or_test}.txt
			done

			cd .. # out of Neuron$neu
		) &
		done
		wait # until the testing completes
		cd .. # out of Testing

		# Now we may, if short of space, do
		# rm -r Neuron* ../Training/Neuron*
	fi


	# 4. Calculating accuracy
	# ---------------------

	cd Testing
	python $SRC_PATH/get_accuracy.py > classification_report.txt
	python $SRC_PATH/get_fitness.py > ../fitness.txt

	cd .. # out of Testing
	mv Testing/*_accuracy.txt Testing/classification_report.txt .
	cd .. # out of fold
) &
done

wait

cat fold*/fitness.txt > fitnesses.txt
for train_or_test in 'train' 'test'
do
	cat fold*/${train_or_test}_accuracy.txt > ${train_or_test}_accuracies.txt
	python > mean_${train_or_test}_accuracy.txt <<-END_TO_PYTHON
		import numpy
		accuracies = numpy.loadtxt('${train_or_test}_accuracies.txt')
		print(
			numpy.mean(accuracies),
			numpy.std(accuracies),
			numpy.min(accuracies),
			numpy.max(accuracies)
		)
	END_TO_PYTHON
done
python > mean_fitness.txt <<-END_TO_PYTHON
	import numpy
	fold_fitnesses = numpy.loadtxt('fitnesses.txt')
	print(numpy.mean(fold_fitnesses))
END_TO_PYTHON
