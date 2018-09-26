import os
import argparse

import unittest.mock as mock

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

    # tokenize and flatten
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

    # with pytest.raises(ValueError) as excinfo:
        # budget_range(1, 0, 100)
    # assert str(excinfo.value).startswith('Minimum budget')

