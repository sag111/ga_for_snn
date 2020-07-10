from subprocess import check_output
import numpy as np


def load_rates(data_path='.'):
    """
    returns {'train'|'test': (number_of_neurons, number_of_vectors)}
    """
    filename_mask = '{data_path:s}/neuron*-freqs_{train_or_test:s}.txt'
    filenames = {
        train_or_test: check_output(
            'echo ' + filename_mask.format(
                data_path=data_path,
                train_or_test=train_or_test
            ),
            shell=True, text=True
        ).split()
        for train_or_test in ('train', 'test')
    }
    rates = {
        train_or_test: np.array([
            np.loadtxt(filename)
            for filename in filenames[train_or_test]
        ])
        for train_or_test in ('train', 'test')
    }
    return rates


def get_y_true(data_path='.'):
    """
    Just count the number of lines in
    data_path/mask_class*.txt,
    assuming that, during testing, all classes come sorted.
    """
    y_true = {
        train_or_test: []
        for train_or_test in ('train', 'test')
    }
    for train_or_test in ('train', 'test'):
        input_data_filename_prefix = (
            '{data_path:s}/'
            '{train_or_test:s}_data/'
            'mask_class'.format(
                data_path=data_path,
                train_or_test=train_or_test
            )
        )
        input_data_filename_suffix = '.txt'
        class_names = check_output(
            '''
                for f in {prefix:s}*{suffix:s}
                do
                    cl=${{f#{prefix:s}}}
                    cl=${{cl%{suffix:s}}}
                    echo $cl
                done | sort -n
            '''.format(
                prefix=input_data_filename_prefix,
                suffix=input_data_filename_suffix
            ),
            shell=True, text=True
        ).split()
        class_sizes = {
            class_name: int(check_output(
                'wc -l < {prefix:s}{cl:s}{suffix:s}'.format(
                    prefix=input_data_filename_prefix,
                    cl=class_name,
                    suffix=input_data_filename_suffix
                ),
                shell=True
            ))
            for class_name in class_names
        }
        y_true[train_or_test] = np.concatenate([
            # because instances in the test set come ordered
            [int(class_name)] * class_sizes[class_name]
            for class_name in class_names
        ])
    return y_true


def get_y_pred(rates, y_true):
    classes = set(y_true['train'])
    number_of_classes = len(classes)
    votes_for_classes = {
        # votes[train_or_test] should have the shape
        # (number of vectors, len(classes_order)):
        # votes[vector_number] == (
        #   votes_for_class_1,
        #   ...,
        #   votes_for_class_N
        # )
        train_or_test: np.array([
            [0] * number_of_classes
            for i in range(len(y_true[train_or_test]))
        ])
        for train_or_test in ('train', 'test')
    }

    # Get (number_of_classes)**2 mean frequencies: of each neuron, in
    # response to each class (averaged over all the vectors of the
    # class). We will further compare the frequency in response to
    # each particular vector to the ranges of these mean frequencies.
    mean_train = [
        [
            np.mean(
                rates['train'][neu][
                    # Select output in response to class class_
                    y_true['train'] == class_
                ]
            )
            for class_ in classes
        ]
        for neu in range(number_of_classes)
    ]

    y_pred = {}
    for train_or_test in ('train', 'test'):

        # Sort the neurons by how well they distinguish
        # their classes from not theirs.
        def diffs_square_sum(current_class):
            return sum([
                (mean_train[current_class][current_class]
                    - mean_train[current_class][other_class])**2
                for other_class in range(number_of_classes)
            ])

        for vector_number in range(len(y_true[train_or_test])):
            for current_class in classes:
                #normalizing_coefficient = np.std(rates[train_or_test][current_class][correct_classes[train_or_test] == current_class])
                #normalizing_coefficient = diffs_square_sum(current_class) / 1e+6
                normalizing_coefficient = 1
                if normalizing_coefficient == 0:
                    normalizing_coefficient = 1e-3
                votes_for_classes[train_or_test][vector_number][current_class] -= abs(
                    rates[train_or_test][current_class][vector_number] - mean_train[current_class][current_class]
                ) / normalizing_coefficient
        y_pred[train_or_test] = get_y_from_votes(
            votes_for_classes[train_or_test], list(classes)
        )
    return y_pred


def get_y_from_votes(votes, classes_order):
    '''
    votes should have the shape
    (number of vectors, len(classes_order)):
    votes[vector_number] == (
        votes_for_class_1,
        ...,
        votes_for_class_N
    )
    '''
    return np.array([
        classes_order[np.argmax(current_vector_votes)]
        for current_vector_votes in votes
    ])


if __name__ == '__main__':
    import sklearn.metrics

    rates_path = '.'
    input_data_path = '..'  # out of Testing/
    y_true_train_or_test = get_y_true(input_data_path)
    y_pred_train_or_test = get_y_pred(
        load_rates(rates_path),
        y_true_train_or_test
    )

    for train_or_test in ('train', 'test'):
        y_true = y_true_train_or_test[train_or_test]
        y_pred = y_pred_train_or_test[train_or_test]
        np.savetxt(train_or_test + '_y_pred.txt', y_pred, '%d')

        print(
            'On the', train_or_test, 'set:',
            sklearn.metrics.classification_report(
                y_true=y_true,
                y_pred=y_pred
            )
        )
        print(
            sklearn.metrics.f1_score(
                y_true=y_true,
                y_pred=y_pred,
                average='macro'
            ),
            file=open(train_or_test + '_accuracy.txt', 'w')
        )
