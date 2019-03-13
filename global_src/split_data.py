import sys  # for path
from os import chdir, mkdir
import numpy

import sklearn
import sklearn.model_selection
import sklearn.datasets

# We will need the number of inputs.
sys.path.append('.')
from parameters.parameters_network import network_parameters

def load_dataset():
    if network_parameters['dataset'] == 'Iris':
        dataset_bunch = sklearn.datasets.load_iris()
    if network_parameters['dataset'] == 'Digits':
        dataset_bunch = sklearn.datasets.load_digits()
    if network_parameters['dataset'] == 'Wisconsin':
        dataset_bunch = sklearn.datasets.load_breast_cancer()
    if network_parameters['dataset'] == 'MNIST':
        dataset_bunch = sklearn.datasets.fetch_openml('mnist_784')

    X = dataset_bunch['data']
    y = dataset_bunch['target']

    # Flatten the images.
    X = X.reshape(
        (X.shape[0], -1)
    )

    return X, y

def encode_with_gaussian_receptive_fields(X):

    def get_gaussian(x, sigma_squared, mu):
        cutoff_gaussian = 0.09
        result = (
            # So that the maximum value, if x == mu, is 1
            numpy.e ** (- (x - mu) ** 2 / (2 * sigma_squared))
        )
        if result < cutoff_gaussian:
            result = 0
        return result

    max_x = X.max()
    min_x = X.min()
    n_fields = network_parameters['receptive_fields_per_component']
    mu_step = (max_x - min_x) / (n_fields - 1)
    # as in [Yu et al. 2014]
    sigma_squared = (
        2/3 * (max_x - min_x) / (n_fields - 2)
    )**2

    result = [
        numpy.concatenate([
            [
                get_gaussian(
                    x=x_component,
                    sigma_squared=sigma_squared,
                    mu=min_x + mu_step*field_number
                )
                for field_number in range(n_fields)
            ]
            for x_component in x
        ])
        for x in X
    ]
    return numpy.array(result)


if __name__ == "__main__":
    X, y = load_dataset()

    # This normalization is performed by row, not by column,
    # so it may safely be done before train-test-splitting.
    if 'L2' in network_parameters['normalize']:
        X = sklearn.preprocessing.normalize(X, norm = 'l2', axis = 1)
    if 'L1' in network_parameters['normalize']:
        X = sklearn.preprocessing.normalize(X, norm = 'l1', axis = 1)
    if 'complement' in network_parameters['normalize']:
        X = numpy.array([
            numpy.concatenate([
                x,
                # append a complement to x
                (x - X.max()) * (-1)
            ])
            for x in X
        ])

    splits = sklearn.model_selection.StratifiedKFold(
        n_splits=5,
        shuffle=True,
        random_state=None
    ).split(X, y)
    # splits = sklearn.model_selection.StratifiedShuffleSplit(
    #     n_splits=5,
    #     test_size = 0.2,
    #     random_state=None
    # ).split(X, y)
    for fold, current_split in enumerate(splits):
        train_indices, test_indices = current_split
        train_X = X[train_indices]
        train_y = y[train_indices]
        test_X = X[test_indices]
        test_y = y[test_indices]

        if 'minmaxscale' in network_parameters['normalize']:
            train_X, test_X = [
                sklearn.preprocessing.minmax_scale(train_or_test_X, copy=False)
                for train_or_test_X in (train_X, test_X)
            ]
        if network_parameters['gaussian_encoding'] == True:
            train_X, test_X = map(
                encode_with_gaussian_receptive_fields,
                (train_X, test_X)
            )

        mkdir('fold' + str(fold))
        chdir('fold' + str(fold))

        mkdir('train_data')
        mkdir('test_data')

        numpy.savetxt('train_data/indices.txt', train_indices, '%d')
        numpy.savetxt('test_data/indices.txt', test_indices, '%d')

        for current_class in set(y):
            current_train_X = train_X[train_y == current_class]
            current_test_X = test_X[test_y == current_class]

            # Trim the data to decrease simulation time.
            max_train_size = 30
            max_test_size = 10
            #current_train_X = current_train_X[:max_train_size]
            #current_test_X = current_test_X[:max_test_size]

            numpy.savetxt(
                'train_data/mask_class' + str(current_class) + '.txt',
                current_train_X,
                '%.3f'
            )
            numpy.savetxt(
                'test_data/mask_class' + str(current_class) + '.txt',
                current_test_X,
                '%.3f'
            )

        chdir('..') # out of fold*
