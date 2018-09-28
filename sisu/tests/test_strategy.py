import subprocess
import sisu.strategy as strategy


def file_len(fname):
    p = subprocess.Popen(['wc', '-l', fname], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])


def _strategy_test_helper(dir_, strat, test_file_name, mem_limit):

    types = ('1', '2', 'intersection')
    base_name = str(dir_ / test_file_name)

    (
        file1_name,
        file2_name,
        intersection_name
    ) = [f'{base_name}-{type_}.lst' for type_ in types]

    res = strat.intersect(file1_name, file2_name, mem_limit)

    file_len_ = file_len(intersection_name)

    assert res.cardinality == file_len_


def test_naive(datadir):
    nil = 0
    _strategy_test_helper(datadir, strategy.Naive, 'small-diff', nil)
    _strategy_test_helper(datadir, strategy.Naive, 'large-diff', nil)
    _strategy_test_helper(datadir, strategy.Naive, 'small-same', nil)
    _strategy_test_helper(datadir, strategy.Naive, 'large-same', nil)


def test_hash(datadir):
    nil = 0
    _strategy_test_helper(datadir, strategy.Naive, 'small-diff', nil)
    _strategy_test_helper(datadir, strategy.Naive, 'large-diff', nil)
    _strategy_test_helper(datadir, strategy.Naive, 'small-same', nil)
    _strategy_test_helper(datadir, strategy.Naive, 'large-same', nil)


def test_merge():
    pass
