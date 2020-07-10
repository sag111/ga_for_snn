import sys
from subprocess import check_output
import numpy as np
import sklearn.metrics

from get_accuracy import load_rates, get_y_true, get_y_pred


tries = check_output(
    '''
        filename_to_check=/fold0/Testing/neuron0-freqs_test.txt
        for d in try*$filename_to_check
        do
            echo ${d%$filename_to_check}/
        done | sort -n --key=1.4  # ignore the "try" symbols when sorting
    ''',
    shell=True, text=True
).split()
max_number_of_tries = len(tries)
fold_dirs = check_output(
    'cd {example_try:s} ; echo fold*/'.format(
        example_try=tries[0]
    ),
    shell=True, text=True
).split()
number_of_folds = len(fold_dirs)
rates_per_fold_per_try = [
    # Order: (tries, folds, train|test, neuron, vector)
    [
        load_rates(try_dir + fold_dir + '/Testing')
        for fold_dir in fold_dirs
    ]
    for try_dir in tries
]
y_true_per_fold = [
    get_y_true(tries[0] + fold_dir)
    for fold_dir in fold_dirs
]

if len(sys.argv) > 1 and 'sort=' in sys.argv[1]:
    sort_type = sys.argv[1][len('sort='):]
else:
    sort_type = None
if sort_type == 'best_first' or sort_type == 'worst_first':
    rates_per_fold_per_try.sort(
        key=lambda rates_per_fold: np.mean([
            sklearn.metrics.f1_score(
                y_true=y_true_per_fold[fold_number]['train'],
                y_pred=get_y_pred(rates, y_true_per_fold[fold_number])['train'],
                average='macro'
            )
            for fold_number, rates in enumerate(rates_per_fold)
        ]),
        reverse=(True if sort_type == 'best_first' else False)
    )
if sort_type == 'random':
    np.random.shuffle(rates_per_fold_per_try)

for try_dir, rates_per_fold in zip(tries, rates_per_fold_per_try):
    print(
        try_dir,
        np.mean([
            sklearn.metrics.f1_score(
                y_true=y_true_per_fold[fold_number]['train'],
                y_pred=get_y_pred(rates, y_true_per_fold[fold_number])['train'],
                average='macro'
            )
            for fold_number, rates in enumerate(rates_per_fold)
        ]),
        np.std([
            sklearn.metrics.f1_score(
                y_true=y_true_per_fold[fold_number]['train'],
                y_pred=get_y_pred(rates, y_true_per_fold[fold_number])['train'],
                average='macro'
            )
            for fold_number, rates in enumerate(rates_per_fold)
        ])
    )

(
    accuracy_vs_number_of_tries_outfile,
    discrete_vote_accuracy_vs_number_of_tries_outfile
) = [
    {
        train_or_test: open(
            '{prefix:s}mean_{train_or_test:s}_accuracy'
            '_vs_number_of_tries{sort_type:s}.txt'.format(
                prefix=accuracy_calculation_method,
                train_or_test=train_or_test,
                sort_type=('-sort_'+sort_type if sort_type != None else '')
            ),
            'w'
        )
        for train_or_test in ('train', 'test')
    }
    for accuracy_calculation_method in ('', 'discrete_vote_')
]

all_rates_per_fold_per_try = rates_per_fold_per_try
for number_of_tries in range(1, max_number_of_tries+1):
    if sys.stderr.isatty():
        sys.stderr.write(
            '\r{progress:f}%% done'.format(
                progress=100.0*(number_of_tries-1)/(max_number_of_tries+1)
            )
        )
    rates_per_fold_per_try = all_rates_per_fold_per_try[:number_of_tries]

    # Method 1: sum the output rates over all tries
    # and pass the summed rates to the decoding algorithm.
    summed_rates_per_fold = [
        {
            train_or_test: sum([
                rates_per_fold[fold_number][train_or_test]
                for rates_per_fold in rates_per_fold_per_try
            ])
            for train_or_test in ('train', 'test')
        }
        for fold_number in range(number_of_folds)
    ]
    rate_vote_accuracies = {
        train_or_test: [
            sklearn.metrics.f1_score(
                y_true=y_true[train_or_test],
                y_pred=get_y_pred(rates, y_true)[train_or_test],
                average='macro'
            )
            for y_true, rates in zip(y_true_per_fold, summed_rates_per_fold)
        ]
        for train_or_test in ('train', 'test')
    }

    # Method 2: decode all tries' outputs into class labels
    # and average the labels.
    discrete_vote_accuracies = {
        train_or_test:
        [
            sklearn.metrics.f1_score(
                y_true=y_true[train_or_test],
                y_pred=np.median(
                    [
                        get_y_pred(
                            rates_per_fold[fold_number],
                            y_true
                        )[train_or_test]
                        for rates_per_fold in rates_per_fold_per_try
                    ],
                    axis=0
                ).astype(int),
                average='macro'
            )
            for fold_number, y_true in enumerate(y_true_per_fold)
        ]
        for train_or_test in ('train', 'test')
    }

    for train_or_test in ('train', 'test'):
        for train_or_test_accuracies, train_or_test_outfile in (
            (rate_vote_accuracies, accuracy_vs_number_of_tries_outfile),
            (discrete_vote_accuracies, discrete_vote_accuracy_vs_number_of_tries_outfile)
        ):
            print(
                number_of_tries,
                np.mean(train_or_test_accuracies[train_or_test]),
                np.std(train_or_test_accuracies[train_or_test]),
                np.min(train_or_test_accuracies[train_or_test]),
                np.max(train_or_test_accuracies[train_or_test]),
                file=train_or_test_outfile[train_or_test]
            )
