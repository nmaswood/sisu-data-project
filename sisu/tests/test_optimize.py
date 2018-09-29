import os

import unittest.mock as mock
import sisu.constants as c
import sisu.optimize as optimize
import sisu.strategy as s


def test_optimal_strategy():
    config = optimize.DEFAULT_CONFIG

    file_sizes = {
        'small_file': config['small_file'] * (9/10),
        'medium_file': (config['small_file'] + config['large_file']) / 2,
        'big_file': config['large_file'] * 2 * 100
    }

    with mock.patch.object(os.path, 'getsize') as getsize:
        getsize.side_effect = lambda x: file_sizes[x]
        strat = optimize.optimal_strategy(
            'small_file', 'small_file',
            1.75 * file_sizes['small_file']
        )

        assert strat is s.Hash

        strat = optimize.optimal_strategy(
            'small_file', 'medium_file',
            1.75 * file_sizes['small_file']
        )

        assert strat is s.Hash

        strat = optimize.optimal_strategy(
            'big_file', 'big_file',
            1.75 * file_sizes['small_file']
        )

        assert strat is s.Merge
