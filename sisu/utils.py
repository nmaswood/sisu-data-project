import argparse
import os
import random as r
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
        help='The upper limit for RAM',
        type=float, default=1.0)

    parsed_args = parser.parse_args(args)

    for f in {parsed_args.file_1, parsed_args.file_2}:
        if not os.path.isfile(f):
            raise argparse.ArgumentError(f'The file {f} does not exist.')

        size = os.path.getsize("/path/isa_005.mp3")
        if size >= c.MAX_FILE_SIZE:
            raise argparse.ArgumentError(
                f'The specified file {f} is too large.'
            )

    if parsed_args.mem_limit < c.MIN_MEMORY_BUDGET:
        raise argparse.ArgumentError(
            f'A memory limit of {parsed_args.mem_limit} is too small.'
        )

    return parsed_args


def write_fake_data(file_name, size, batch_size):
    """Generates fake data. Randomly samples from
    range and writes those ints to disk.

    Parameters
    ----------
    file_name: str
        Name of output file
    size: int
        Number of output rows
    batch_size: int
        Number of writes to occur.

    Side Effect
    ------
    Writes a file to disk
    """

    with open(file_name, 'w') as fp:

        range_ = range(c.MIN_NUMBER, c.MAX_NUMBER - 1)

        for _ in range(0, size, batch_size):

            k_random_nums = r.sample(range_, batch_size)

            as_str = '\n'.join([str(num) for num in k_random_nums])

            fp.write(as_str)


if __name__ == '__main__':
    write_fake_data('small1.lst', 100, 100)
