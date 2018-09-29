import argparse
import os
import random as r

import pytest
import unittest.mock as mock

import sisu.constants as constants
import sisu.utils as utils


def _tokenize_and_flatten(arg_string):
    """Given an arg string splits each unit in
    (arg_name, arg_value) tuples and then flattens the result.

    '--foobar baz', '--bazbar foobaz' ->
    ['--foobar', 'baz', '--bazbar', 'foobaz']
    """
    return sum([x.split(' ', 1) for x in arg_string], [])


def test_parse_args():
    expected = {
        'mem_limit': 12345678.0 * constants.MEGABYTE,
        'file_1': 'hello',
        'file_2': 'world',
    }

    arg_string = (
        "--mem_limit 12345678",
        "--file_1 hello",
        "--file_2 world",
    )

    args = _tokenize_and_flatten(arg_string)

    with mock.patch.object(os.path, 'isfile') as isfile, \
            mock.patch.object(os.path, 'getsize') as getsize:
        isfile.return_value = True
        getsize.return_value = 10000000
        parsed_args = utils.parse_args(args)

    actual = {
        key: getattr(parsed_args, key)
        for key in expected
    }

    assert actual == expected

    expected = {
        'mem_limit': -1,
        'file_1': 'hello',
        'file_2': 'world',
    }

    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        parsed_args = utils.parse_args(args)
        assert str(excinfo.value).endswith('is too small.')

    with mock.patch.object(os.path, 'isfile') as isfile:
        isfile.return_value = False
        with pytest.raises(argparse.ArgumentTypeError) as excinfo:
            parsed_args = utils.parse_args(args)
            assert str(excinfo.value).endswith('does not exist.')

    with mock.patch.object(os.path, 'isfile') as isfile, \
            mock.patch.object(os.path, 'getsize') as getsize:
        isfile.return_value = True
        getsize.return_value = int(1e100)
        with pytest.raises(argparse.ArgumentTypeError) as excinfo:
            parsed_args = utils.parse_args(args)
            assert str(excinfo.value).endswith('too large.')


@pytest.fixture
def ten_random_one():
    # created with utils.seed
    # seed of 0
    return (
        3553260803050964941,
        8211050864078048428,
        373402508605428821,
        8904841857247764026,
        4481891911369680482,
        8469216845598671736,
        7654042048833979961,
        8926379391851030281,
        3302422582397125124,
        8224117987793733247,
    )


def test_write_fake_data(ten_random_one, tmpdir):
    r.seed(0)

    path = os.path.join(tmpdir, 'fake.lst')
    utils.write_fake_data(path, 10)
    actual = utils.read_nums(path)

    assert actual == set(ten_random_one)


def test_read_file_by_block(datadir):
    path = os.path.join(str(datadir), 'small-same-0.lst')
    lines = utils.read_file_by_block(path, 2)
    as_list = list(lines)
    flat = sum(as_list, [])

    assert len(as_list) == 100 // 2
    assert set(map(int, flat)) == utils.read_nums(path)


def test_require_int():

    @utils.require_int
    def func(self, should_be_int):
        pass

    with pytest.raises(ValueError) as excinfo:
        func({}, 'hi')
        assert str(excinfo.value).endswith('must be of type int.')


def test_reorder_by_file_size():

    mock_func = mock.MagicMock()

    @utils.reorder_by_file_size
    def func(file1, file2, mem_limit):
        mock_func.foo(file1, file2, mem_limit)

    mem_limit = 123

    file_d = {
        'file1': 100,
        'file2': 1000,
    }

    with mock.patch.object(os.path, 'getsize') as getsize:
        getsize.side_effect = lambda x: file_d[x]
        func('file1', 'file2', mem_limit)
        mock_func.foo.assert_called_with('file1', 'file2', mem_limit)
        func('file2', 'file1', mem_limit)
        mock_func.foo.assert_called_with('file1', 'file2', mem_limit)


def test_read_nums(tmpdir, ten_random_one):

    r.seed(0)

    path = os.path.join(tmpdir, 'fake.lst')
    utils.write_fake_data(path, 10)
    nums = utils.read_nums(path)

    assert set(ten_random_one) == nums


def test_mb_to_bytes():
    assert utils.mb_to_bytes(1.0) == constants.MEGABYTE
    assert utils.mb_to_bytes(2.0) == constants.MEGABYTE * 2
    assert utils.mb_to_bytes(2.34) == int(constants.MEGABYTE * 2.34)


def test_bytes_to_ints():
    assert utils.bytes_to_ints(1000) == 1000 // constants.SIZE_INT
    assert utils.bytes_to_ints(1234) == 1234 // constants.SIZE_INT
    assert utils.bytes_to_ints(9999) == 9999 // constants.SIZE_INT
