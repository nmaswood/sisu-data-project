from itertools import islice


def read_file_by_block(file_, block_size):
    """Reads `block_size` at a time
    Parameters
    ----------
    prefix : file_
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
            stripped = (num[:-1] for num in chunk)
            nums = list(stripped)
            if not nums:
                break
            yield nums
