from itertools import islice
import argparse
import os
import random as r
import time
from functools import wraps

import sisu.constants as c


def parse_args(args=None):
    """Parses command line args and validates the following conditions

        * Files exists
        * Files are smaller than 500 MB
        * Memlimit is greater than 1MB

    Parameters
    ----------
    prefix : list of str, optional
        A argument to parse. Reads from argv if None
    block_size: int , optional

    Yields
    ------
    dict
        Arg values as an object.
    """
    parser = argparse.ArgumentParser(description='Intersect Two Lists')

    parser.add_argument(
        '--file_1',
        required=True,
        help='The first file containing newline delimited ascii numbers.',
        type=str)

    parser.add_argument(
        '--file_2',
        required=True,
        help='The second file containing newline delimited ascii numbers.',
        type=str
    )

    parser.add_argument(
        '--mem_limit',
        required=True,
        help='The upper limit for RAM in MB',
        type=lambda x: float(x) * c.MEGABYTE)

    parsed_args = parser.parse_args(args)

    if parsed_args.mem_limit < c.MIN_MEMORY_BUDGET:
        raise argparse.ArgumentTypeError(
            f'A memory limit of {parsed_args.mem_limit} is too small.'
        )

    for f in {parsed_args.file_1, parsed_args.file_2}:
        if not os.path.isfile(f):
            raise argparse.ArgumentTypeError(f'The file {f} does not exist.')

        size = os.path.getsize(f)
        if size > c.MAX_FILE_SIZE:
            raise argparse.ArgumentTypeError(
                f'The specified file {f} is too large.'
            )

    return parsed_args


def write_fake_data(file_name, size, r_limit=None):
    """Generates fake data. Randomly samples from
    range and writes those ints to disk.

    Parameters
    ----------
    file_name: str
        Name of output file
    size: int
        Number of output rows

    Side Effect
    ------
    Writes a file to disk
    """

    if r_limit is None:
        r_limit = c.MAX_NUMBER - 1

    with open(file_name, 'w') as fp:

        range_ = range(c.MIN_NUMBER, r_limit)

        random_nums = r.sample(range_, size)

        as_str = ''.join([str(num) + '\n' for num in random_nums])
        fp.write(as_str)


def seed():
    """Generates seed data files for testing.
    This avoids having to version control large files.

    Will write about 4GB to disk.

    File size approxmiated with `du -h`

    Side Effect
    ------
    Writes several files to `sisu/tests/data`
    """

    print(
        'Beginning to seed the test dir.\n'
        'Please be patient!'
    )

    r.seed(0)
    fake_data_config = (
        # About 4.0K
        (
            'small-same',
            (100, 150),
            (100, 150),
        ),
        # About 4.0K

        (
            'medium-same',
            (1000, 1200),
            (1000, 1200),
        ),
        (
            'medium-large-same',
            (10000, 12000),
            (10000, 12000),
        ),

        # About 30MB
        (
            'large-same',
            (4200000, 4500000),
            (4200000, 4500000),
        ),
        # About 500MB
        (
            'huge-same',
            (58000000, 59000000),
            (58000000, 59000000),
        ),

        # For these values one input list is
        # about 10x smaller than the other

        # x < 4.0K
        (
            'small-diff',
            (1, 120),
            (100, 120),
        ),

        # x < 4.0K
        (
            'medium-diff',
            (100, 1200),
            (1000, 1200),
        ),
        (
            'medium-large-diff',
            (1000, 12000),
            (10000, 12000),
        ),

        # About 30MB
        (
            'large-diff',
            (420000, 4500000),
            (4200000, 4500000),
        ),

        # About 500MB
        (
            'huge-diff',
            (5800000, 59000000),
            (58000000, 59000000),
        ),
    )

    prefix = 'sisu/tests/data'

    for (name, file1_config, file2_config) in fake_data_config:

        start = time.time()

        for idx, (file_size, file_rlimit) in enumerate(
                (file1_config, file2_config)):

            write_fake_data(f'{prefix}/{name}-{idx}.lst', file_size,
                            file_rlimit)

        file1_nums = read_nums(f'{prefix}/{name}-0.lst')
        file2_nums = read_nums(f'{prefix}/{name}-1.lst')

        output_string = ''.join([
            f'{num}\n' for num in file1_nums.intersection(file2_nums)
        ])
        with open(f'{prefix}/{name}-intersection.lst', 'w') as outfile:
            outfile.write(output_string)

        end = time.time()
        print(f'Finished {name} in {end - start} seconds')


def read_nums(path):
    """Simple helper function that grabs an entire file
    in memory and parses ints from it

    Parameters
    ----------
    path : str

    Returns
    ------
    set of int
    """

    with open(path, 'r') as infile:
        nums = infile.readlines()
    return {int(num.strip()) for num in nums}


def read_file_by_block(file_, block_size):
    """Reads `block_size`lines of a file  at a time
    Parameters
    ----------
    file_ : str
        The name of a file to fetch from
    block_size: int , optional
        Number of ints to fetch at a time from a list


    Yields
    ------
    list of str
        Numbers from the file by list (lazily).
    """

    with open(file_, 'r') as f:

        while True:
            chunk = islice(f, block_size)
            stripped = (int(num[:-1]) for num in chunk)
            nums = list(stripped)
            if not nums:
                break
            yield nums


def require_int(function):
    @wraps(function)
    def wrapper(*args):
        """Ensures the input argument is an int

        # NOTE This implementation assumes alot.
        It assumes you are wrapping an instance method
        that takes one param that you'd like to be an int.

        Parameters
        ----------
        arg : Any

        Returns
        ------
        function
        """
        if type(args[1]) != int:
            raise ValueError('Argument must be of type int')

        retval = function(*args)
        return retval

    return wrapper


def reorder_by_file_size(function):
    @wraps(function)
    def wrapper(file1, file2, mem_limit, **kwargs):
        """Given a strategy reorders the arguments s.t. the smaller file
        is always passed in first.

        Parameters
        ----------
        file1 : str
        file2 : str
        mem : float

        Returns
        ------
        function
        """

        file1_size = os.path.getsize(file1)
        file2_size = os.path.getsize(file2)

        if file1_size <= file2_size:
            return function(file1, file2, mem_limit, **kwargs)

        return function(file2, file1, mem_limit, **kwargs)
    return wrapper


def mb_to_bytes(mb):
    """Converts # in mb to # in bytes

    Parameters
    ----------
    mb : float

    Returns
    ------
    int
    """

    return int(mb * c.MEGABYTE)


def bytes_to_ints(bytes_):
    """Converts # in bytes to # of ints in python

    Parameters
    ----------
    bytes_ : int U float

    Returns
    ------
    int
    """
    return int(bytes_ // c.SIZE_INT)


if __name__ == '__main__':
    seed()
