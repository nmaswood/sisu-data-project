import subprocess
import sisu.strategy as strategy
import sisu.constants as c
import sisu.utils as utils


def _file_len(fname):
    """Calls `wc -l` on a file and returns the result. Called on `intersection`
    files to get the number of intersections for a particular test case.

    Parameters
    ----------
    fname : str

    Returns
    ------
    int
    """
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    value = result.strip().split(b' ', 1)[0]
    return int(value)


def _strategy_test_helper(dir_, strat, test_file_name, mem_limit, **config):
    """Given a strat, its params and test suite file name it performs the strategy
    and sees if it returns the correct result.

    Parameters
    ----------
    dir_
        dir name which contains testing data
    strat
        A class which implements Strategy method
    test_file_name
        name of testing example e.g. small-same
    mem_limit
        limit in bytes
    **config
        strat kwargs
    """

    types = ('0', '1', 'intersection')
    base_name = str(dir_ / test_file_name)

    (
        file1_name,
        file2_name,
        intersection_name
    ) = [f'{base_name}-{type_}.lst' for type_ in types]

    res = strat.intersect(file1_name, file2_name, mem_limit, **config)

    assert res.cardinality == _file_len(intersection_name)


def test_naive_intersect(datadir):

    mem_limit = 0
    _strategy_test_helper(datadir, strategy.Naive, 'small-same', mem_limit)
    _strategy_test_helper(datadir, strategy.Naive, 'small-diff', mem_limit)

    _strategy_test_helper(datadir, strategy.Naive, 'medium-same', mem_limit)
    _strategy_test_helper(datadir, strategy.Naive, 'medium-diff', mem_limit)


def test_merge_external_sort(datadir):

    unsorted_file = str(datadir / 'medium-same-1.lst')

    arbitrary_size = 3 * c.MEGABYTE

    f = strategy.Merge.external_sort(unsorted_file, arbitrary_size)

    nums = sorted(utils.read_nums(unsorted_file))
    with open(f.name, 'r') as infile:
        ints = [
            int(num.strip()) for num in infile.readlines()
        ]

    assert ints == nums


def test_hash_intersect(datadir):
    mem_limit = c.MEGABYTE

    _strategy_test_helper(datadir, strategy.Hash, 'small-diff', mem_limit)
    _strategy_test_helper(datadir, strategy.Hash, 'small-same', mem_limit)

    mem_limit = 2 * c.MEGABYTE

    _strategy_test_helper(datadir, strategy.Hash, 'medium-same', mem_limit)
    _strategy_test_helper(datadir, strategy.Hash, 'medium-diff', mem_limit)

    mem_limit = c.MEGABYTE

    # _strategy_test_helper(datadir, strategy.Hash, 'medium-large-same',
    # mem_limit)

    # _strategy_test_helper(datadir, strategy.Hash, 'medium-large-diff',
    # mem_limit)


def test_merge_strategy(datadir):
    mem_limit = c.MEGABYTE

    _strategy_test_helper(datadir, strategy.Merge, 'small-diff', mem_limit)
    _strategy_test_helper(datadir, strategy.Merge, 'small-same', mem_limit)

    _strategy_test_helper(datadir, strategy.Merge, 'medium-same', mem_limit)
    _strategy_test_helper(datadir, strategy.Merge, 'medium-diff', mem_limit)

    # _strategy_test_helper(datadir, strategy.Hash, 'medium-large-same',
    # mem_limit)
    # _strategy_test_helper(datadir, strategy.Hash, 'medium-large-diff',
    # mem_limit)
