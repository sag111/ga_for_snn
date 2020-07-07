import sys  # for path
from os import chdir, mkdir
import numpy as np

import sklearn
import sklearn.model_selection
import sklearn.datasets

# We will need the number of inputs.
sys.path.append('.')
from parameters.parameters_network import network_parameters

def load_mnist(**kwargs):
    X, y = sklearn.datasets.fetch_openml('mnist_784', **kwargs)
    y = y.astype(int)
    return X, y

def load_dataset():
    if network_parameters['dataset'] == 'Optdigits':
        import csv
        X_and_y_train, X_and_y_test = [
            np.array([
                line for line in csv.reader(open(
                    '/s/ls4/users/aserenko/'
                    'Genetic/Optdigits/original_data/'
                    'optdigits.' + tra_or_tes
                ))
            ]).astype(int)
            for tra_or_tes in ('tra', 'tes')
        ]
        (X_train, y_train), (X_test, y_test) = [
            [
                X_and_y[:,:-1],
                X_and_y[:,-1]
            ]
            for X_and_y in (X_and_y_train, X_and_y_test)
        ]
        return {
            'train': (X_train, y_train),
            'test': (X_test, y_test)
        }

    dataset_loaders = {
        'Iris': sklearn.datasets.load_iris,
        'Digits': sklearn.datasets.load_digits,
        'Wisconsin': sklearn.datasets.load_breast_cancer,
        'MNIST': load_mnist
    }
    load_the_chosen_dataset = dataset_loaders[network_parameters['dataset']]
    X, y = load_the_chosen_dataset(return_X_y=True)
    # Flatten the images.
    X = X.reshape(
        (X.shape[0], -1)
    )

    if network_parameters['dataset'] == 'MNIST':
        # MNIST has a precomposed testing set.
        # So, we train on a random subset (but
        # not overlapping the testing set),
        # and test on all the 10 000 last instances.
        X_train = X[:-10000]
        y_train = y[:-10000]
        X_test = X[-10000:]
        y_test = y[-10000:]
        return {
            'train': (X_train, y_train),
            'test': (X_test, y_test)
        }
    return X, y

def encode_with_gaussian_receptive_fields(X):

    def get_gaussian(x, sigma_squared, mu):
        cutoff_gaussian = 0.09
        result = (
            # So that the maximum value, if x == mu, is 1
            np.e ** (- (x - mu) ** 2 / (2 * sigma_squared))
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
        np.concatenate([
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
    return np.array(result)


if __name__ == "__main__":
    data = load_dataset()
    if type(data) is tuple:
        X, y = data
        testing_set_is_precomposed = False
    if type(data) is dict:
        X, y = data['train']
        X_test_precomposed, y_test_precomposed = data['test']
        testing_set_is_precomposed = True

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
        X_train = X[train_indices]
        y_train = y[train_indices]
        if not testing_set_is_precomposed:
            X_test = X[test_indices]
            y_test = y[test_indices]
        else:
            # Copy to work around multiple normalization.
            X_test = X_test_precomposed.copy()
            y_test = y_test_precomposed
            # we still need bookkeeping of
            # which neuron gets which indices
            test_indices = np.array(range(len(y_test)))

        def normalize(X):
            for norm_type in network_parameters['normalize'].split('+'):
                if norm_type == 'L2':
                    X = sklearn.preprocessing.normalize(X, norm = 'l2', axis = 1)
                if norm_type == 'L1':
                    X = sklearn.preprocessing.normalize(X, norm = 'l1', axis = 1)
                if norm_type == 'complement':
                    X = np.concatenate(
                        [
                            X,
                            # append a complement to x
                            X.max() - X
                        ],
                        axis=1
                    )
                if norm_type == 'minmaxscale':
                    X = sklearn.preprocessing.minmax_scale(X, copy=False)
            return X
        X_train, X_test = [
            normalize(X_train_or_test)
            for X_train_or_test in (X_train, X_test)
        ]

        if network_parameters['gaussian_encoding'] == True:
            X_train, X_test = map(
                encode_with_gaussian_receptive_fields,
                (X_train, X_test)
            )

        mkdir('fold' + str(fold))
        chdir('fold' + str(fold))

        mkdir('train_data')
        mkdir('test_data')

        np.savetxt('train_data/indices.txt', train_indices, '%d')
        if not testing_set_is_precomposed:
            np.savetxt('test_data/indices.txt', test_indices, '%d')

        for current_class in set(y):
            current_X_train = X_train[y_train == current_class]
            current_X_test = X_test[y_test == current_class]

            np.savetxt(
                'train_data/mask_class' + str(current_class) + '.txt',
                current_X_train,
                '%.3f'
            )
            np.savetxt(
                'train_data/indices_class' + str(current_class) + '.txt',
                train_indices[y_train == current_class],
                '%d'
            )

            np.savetxt(
                'test_data/mask_class' + str(current_class) + '.txt',
                current_X_test,
                '%.3f'
            )
            np.savetxt(
                'test_data/indices_class' + str(current_class) + '.txt',
                test_indices[y_test == current_class],
                '%d'
            )

        chdir('..') # out of fold*
