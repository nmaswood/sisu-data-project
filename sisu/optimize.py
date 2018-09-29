import os

import sisu.constants as c
import sisu.strategy as s
import sisu.utils as utils

DEFAULT_CONFIG = {
    # what constitutes a 'small file'?
    'small_file': 10 * c.MEGABYTE,
    # what constitutes a 'large file'?
    'large_file': 100 * c.MEGABYTE,
    # what is a signifacant ratio between the smaller file
    # and the memory limit?
    'file_to_mem': 2,
    # what is a signifacant ratio between the larger file
    # and the smaller file?
    'file_to_file': 5
}


@utils.reorder_by_file_size
def optimal_strategy(file1, file2, mem_limit, **config):
    """Given the inputs try to determine which strategy
    between merging and hashing is most efficient.

    For more details on why these values were chosen
    go to strategy.py and read the docs there.

    Parameters
    ----------
    file1 : str
        the path to the first file
    file2 : str
        the path to the second file
    mem_limit : float
        The memory limit in bytes

   config
        custom kwargs that can be different for each strategy

    Returns
    ------
    implementation of Strategy
    """

    if not config:
        config = DEFAULT_CONFIG

    file1_size = os.path.getsize(file1)
    file2_size = os.path.getsize(file2)

    file_to_mem_ratio = file1_size / mem_limit
    file_to_file_ratio = file2_size / file1_size

    # both files are relatively small and you have an acceptable amount of
    # memory relative to your smaller file

    if file1_size <= config['small_file'] and \
            file2_size <= config['small_file'] \
            and file_to_mem_ratio <= config['file_to_file']:
        return s.Hash

    # one file is much larger than the other and you have enough
    # memory for a hash table

    if file_to_file_ratio >= config['file_to_file'] and \
            file_to_mem_ratio <= config['file_to_mem']:
        return s.Hash

    return s.Merge
