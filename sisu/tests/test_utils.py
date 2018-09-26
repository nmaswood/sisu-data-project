import argparse
import os
import random as r

import unittest.mock as mock
import pytest

import sisu.utils as utils


def _tokenize_and_flatten(arg_string):
    return sum([x.split(' ', 1) for x in arg_string], [])


def test_parse_args():
    expected = {
        'mem_limit': 12345678.0,
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


@pytest.fixture
def small_same_one():
    return (
        13,
        6,
        12,
        14,
        0,
        4,
        8,
        7,
        3,
        2,
    )


def test_write_fake_data(ten_random_one, tmpdir):
    r.seed(0)

    path = os.path.join(tmpdir, 'fake.lst')
    utils.write_fake_data(path, 10)

    with open(path, 'r') as infile:
        actual = tuple(
            int(num.strip()) for num in infile.readlines()
        )
    assert actual == ten_random_one


def test_read_file_by_block(small_same_one, datadir):
    path = os.path.join(str(datadir), 'small-same-1.lst')
    lines = utils.read_file_by_block(path, 2)
    as_list = list(lines)
    flat = sum(as_list, [])

    assert len(as_list) == 10 // 2
    assert tuple(map(int, flat)) == small_same_one


def test_require_int():

    @utils.require_int
    def func(self, should_be_int):
        pass

    with pytest.raises(ValueError) as excinfo:
        func({}, 'hi')
        assert str(excinfo.value).endswith('must be of type int.')

    func({}, 1)
