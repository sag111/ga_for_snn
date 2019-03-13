# coding: utf-8

import sys  # for argv
from subprocess import check_output
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
import sklearn.metrics


path_to_experiment_data = (
    sys.argv[1] if len(sys.argv) > 1
    else './'
)

src_path = sys.argv[0]
# Strip the filename to leave path only.
src_path = src_path[:src_path.rfind('/')]
src_path += '/../'  # out of 'visualization'
sys.path.append(src_path)  # for split_data.py
parameters_path = path_to_experiment_data  # to parameters/
sys.path.append(parameters_path)  # for parameters_network.py
from split_data import load_dataset
X_full, y_full = load_dataset()

accuracies_on_original_data = []
accuracies_on_encoded_data = []
accuracies_on_neurons_rates = []
feature_importances_on_original_data = []
feature_importances_on_encoded_data = []
feature_importances_on_neurons_rates = []
for fold in range(int(check_output(
    'echo ' + path_to_experiment_data + '/fold*/Testing | wc -w',
    shell=True
))):
    data_dir = '{path_to_experiment_data:s}/fold{fold:d}/{train_or_test:s}_data/'
    current_fold_indices = {
        train_or_test: np.loadtxt(
            (data_dir + 'indices.txt').format(
                path_to_experiment_data=path_to_experiment_data,
                fold=fold,
                train_or_test=train_or_test
            ),
            dtype=int
        )
        for train_or_test in ('train', 'test')
    }

    # Stage 1. The original data as it is.
    X_original, y_original = [
        {
            train_or_test: X_or_y_full.take(current_fold_indices[train_or_test], axis=0)
            for train_or_test in ('train', 'test')
        }
        for X_or_y_full in (X_full, y_full)
    ]

    # Stage 2. The rates the neurons receive, after preprocessing and/or multiplication.
    number_of_classes = len(set(y_full))  # Not hardcoding '3' here in case we move from Iris to Digits.
    vectors_per_class = {
        train_or_test: [
            np.loadtxt(
                (data_dir + 'mask_class{current_class:d}.txt').format(
                    path_to_experiment_data=path_to_experiment_data,
                    fold=fold,
                    train_or_test=train_or_test,
                    current_class=current_class
                )
            )
            for current_class in range(number_of_classes)
        ]
        for train_or_test in ('train', 'test')
    }
    X_encoded = {
        train_or_test: np.concatenate([
            vectors_per_class[train_or_test][current_class]
            for current_class in range(number_of_classes)
        ])
        for train_or_test in ('train', 'test')
    }
    y_encoded = {
        train_or_test: np.concatenate([
            [current_class] * len(vectors_per_class[train_or_test][current_class])
            for current_class in range(number_of_classes)
        ])
        for train_or_test in ('train', 'test')
    }

    # Stage 3. The neurons' output rates.
    neurons_rates_per_neuron = {
        train_or_test: [
            np.loadtxt(
                (
                    '{path_to_experiment_data:s}/fold{fold:d}/'
                    + 'Testing/neuron{neuron:d}-freqs_{train_or_test:s}.txt'
                ).format(
                    path_to_experiment_data=path_to_experiment_data,
                    fold=fold,
                    train_or_test=train_or_test,
                    neuron=neuron
                )
            )
            # The neuron number here actually corresponds
            # to the class the neuron was trained on.
            for neuron in range(number_of_classes)
        ]
        for train_or_test in ('train', 'test')
    }
    X_neurons_rates = {
        train_or_test: np.transpose([
            # Concatenate for each vector
            # all neurons' output in response to it.
            neurons_rates_per_neuron[train_or_test][neuron]
            for neuron in range(number_of_classes)
        ])
        for train_or_test in ('train', 'test')
    }

    for X, y, accuracies_array, feature_importances_array in (
        (X_original, y_original, accuracies_on_original_data, feature_importances_on_original_data),
        (X_encoded, y_encoded, accuracies_on_encoded_data, feature_importances_on_encoded_data),
        (X_neurons_rates, y_encoded, accuracies_on_neurons_rates, feature_importances_on_neurons_rates)
    ):
        classifier = GradientBoostingClassifier(
            loss='deviance',
            learning_rate=0.1,
            n_estimators=100,
            subsample=1.0,
            criterion='friedman_mse',
            min_samples_split=2,
            min_samples_leaf=1,
            min_weight_fraction_leaf=0.0,
            max_depth=3,
            #min_impurity_decrease=0.0,  # complains that it does not have such parameter
            min_impurity_split=None,
            init=None,
            random_state=None,
            max_features=None,
            verbose=0,
            max_leaf_nodes=None,
            warm_start=False,
            presort='auto'
        )

        classifier.fit(X['train'], y['train'])
        accuracies_array.append(
            sklearn.metrics.f1_score(
                y_true=y['test'],
                y_pred=classifier.predict(X['test']),
                average='macro'
            )
        )
        feature_importances_array.append(classifier.feature_importances_)

# For comparison, the accuracy the spiking network
# achieved with its own class-assigning algorithm.
spiking_network_accuracies = np.loadtxt(
   path_to_experiment_data + '/test_accuracies.txt'
)

for description, accuracies_array in (
    ('На исходных данных:', accuracies_on_original_data),
    ('После предобработки:', accuracies_on_encoded_data),
    ('На выходных частотах обученных нейронов:', accuracies_on_neurons_rates),
    ('Точность спайковой сети:', spiking_network_accuracies)
):
    print(
        description,
        '{mean:.1f}% +/- {std:.1f}%, min: {min:.1f}%, max: {max:.1f}%'.format(
            mean=100*np.mean(accuracies_array),
            std=100*np.std(accuracies_array),
            min=100*np.min(accuracies_array),
            max=100*np.max(accuracies_array)
        )
    )

for description, feature_importances_array in (
    ('На исходных данных:', feature_importances_on_original_data),
    ('После предобработки:', feature_importances_on_encoded_data),
    ('На выходных частотах обученных нейронов:', feature_importances_on_neurons_rates)
):
    feature_importances = [
        (
            np.mean(current_feature_importances),
            np.std(current_feature_importances)
        ) 
        for current_feature_importances in np.transpose(feature_importances_array)
    ]
    np.savetxt(
        (
            path_to_experiment_data
            + '/feature_importance-' + description[:-1]  # strip ':'
            + '.txt'
        ),
        feature_importances
    )
