from abc import ABCMeta, abstractmethod
import os
import subprocess
import tempfile

from sisu.spillable_hash import SpillableHash
import sisu.utils as utils
import sisu.constants as c

from pdb import set_trace


class Strategy(metaclass=ABCMeta):
    """A strategy is an interface which expects a method called intersect to
    be implemented.

    The function takes two file paths specified as strings and a memory limit.
    Each file path is a  \n delimited file of ints in the range [0, 2^63]

    A config object is also passed in which holds certain memory tuning related
    values

    Given those four inputs a Strategy returns a SpillableHash which contains
    the result set.
    """
    @abstractmethod
    def intersect(file1, file2, mem_limit, **config):
        """Returns a SpillableHash containing the intersecting values

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
        SpillableHash
        """

        raise NotImplementedError('Implement this method.')


class Naive(Strategy):
    """The naive strategy is a dummy testing solution that ignores the mem_limit
    parameter. This solution is intended as a base line benchmark.
    """
    @staticmethod
    def intersect(file1, file2, _, **__):
        with open(file1, 'r') as f1, open(file2, 'r') as f2:

            file1_ids = {int(num.strip()) for num in f1.readlines()}
            file2_ids = {int(num.strip()) for num in f2.readlines()}

        hash_map = SpillableHash(float('inf'))
        for num in file1_ids.intersection(file2_ids):
            hash_map.add(num)
        return hash_map


class Hash(Strategy):

    DEFAULT_CONFIG = {

        # ideally we would like the memory capacity of
        # build hash to equal the amount of ints in file1
        # ...however we do not know how many ints are in
        # the file. That being said, better to overestimate
        # the size than to underestimate
        # and end up with many more disk seeks
        # err on the side of caution and make the size
        # of the build hash bigger than you may expect
        'file_size_scale_up': 4,
        'build_hash_memory_threshold': 6/10,

        # of the memory remaining after allocating our
        # build hash what amount of memory should be left
        # for our probe_hash?
        # We can make this smaller than our build has because
        # it is upper bounded by the number of values in file1

        'result_hash': 6/10,
    }

    @staticmethod
    def determine_memory(file1, file2, mem_limit, **config):
        """Given two files, a memory list and configuration settings
        determines how much memeory to allocate to the two SpillableHashes
        and for the blocksize in the `intersect` method
        """
        if not config:
            config = Hash.DEFAULT_CONFIG

        file1_size = os.path.getsize(file1)

        build_hash_memory = min(
            file1_size * config['file_size_scale_up'],
            mem_limit * config['build_hash_memory_threshold']
        )

        remaining_memory = mem_limit - build_hash_memory
        result_hash_memory = remaining_memory * config['result_hash']
        block_size_memory = remaining_memory - result_hash_memory

        return (
            int(build_hash_memory),
            int(result_hash_memory),
            int(block_size_memory)
        )

    @staticmethod
    @utils.reorder_by_file_size
    def intersect(file1, file2, mem_limit, **config):
        """The Hash strategy builds a hash table over the smaller file.
        It then walks through the numbers in the larger file and records
        ids present from second file that are in the first.
        """
        (
            build_hash_memory,
            result_hash_memory,
            block_size_memory
        ) = Hash.determine_memory(file1, file2, mem_limit, **config)

        build_hash_int_capacity = max(build_hash_memory // c.SIZE_INT, 1)
        build_hash = SpillableHash(build_hash_int_capacity)

        block_size = block_size_memory // c.LARGEST_ELEMENT_SIZE

        for block in utils.read_file_by_block(file1, block_size):
            for number in block:
                build_hash.add(number)

        result_hash_int_capacity = result_hash_memory // c.SIZE_INT

        # give back any unused capacity from the build hash map
        unused_capacity = build_hash.available_memory // c.SIZE_INT
        result_hash_int_capacity += unused_capacity
        build_hash.capacity -= unused_capacity

        result_hash = SpillableHash(result_hash_int_capacity)

        for block in utils.read_file_by_block(file2, block_size):
            for number in block:
                if number in build_hash:
                    result_hash.add(number)

        return result_hash


class Merge(Strategy):

    DEFAULT_CONFIG = {
        # we do not know how many ints are in the smaller of the two lists
        # let's do a rough estimate based on its file size of the smaller file
        # if we overshoot oh well.
        'result_hash_factor': 3,
        'result_hash_threshold': 1/2
    }

    @staticmethod
    def external_sort(file_, bytes_block_size):
        """ Leverage unix `sort` to external sort the file to an output
        `bytes_block_size` bytes at a time.
        """

        f = tempfile.NamedTemporaryFile()

        cmd = [
            'sort', '-n', '-o', f.name, '-S', f'{bytes_block_size}b',
            '-u', file_
        ]

        p = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        result, err = p.communicate()
        if p.returncode != 0:
            raise IOError(err)

        return f

    @staticmethod
    def determine_memory(file1, file2, mem_limit, **config):
        """Given two files, a memory list and configuration settings
        determines how much memeory to allocate to the SpillableHashes
        result set and for the `block_size` read for each file
        """
        if not config:
            config = Merge.DEFAULT_CONFIG

        init_read_memory = mem_limit
        file1_size = os.path.getsize(file1)

        result_hash_memory = min(
            mem_limit * config['result_hash_threshold'],
            file1_size * config['result_hash_factor']
        )

        rest_memory = mem_limit - result_hash_memory
        file1_block_memory = file2_block_memory = rest_memory // 2

        return (
            int(init_read_memory),
            int(result_hash_memory),
            int(file1_block_memory),
            int(file2_block_memory),
        )

    @staticmethod
    @utils.reorder_by_file_size
    def intersect(file1, file2, mem_limit, **config):

        (
            init_read_memory,
            result_hash_memory,
            file1_block_memory,
            file2_block_memory,
        ) = Merge.determine_memory(file1, file2, mem_limit, **config)

        tempfile1 = Merge.external_sort(file1, init_read_memory)
        tempfile2 = Merge.external_sort(file2, init_read_memory)

        result_hash_int_capacity = result_hash_memory // c.SIZE_INT

        result_hash = SpillableHash(result_hash_int_capacity)

        block1_size = file1_block_memory // c.LARGEST_ELEMENT_SIZE
        block2_size = file2_block_memory // c.LARGEST_ELEMENT_SIZE

        file1_generator = utils.read_file_by_block(tempfile1.name, block1_size)
        file2_generator = utils.read_file_by_block(tempfile2.name, block2_size)

        block1_pointer = 0
        block2_pointer = 0

        block1 = next(file1_generator)
        block2 = next(file2_generator)

        while True:

            if block1_pointer == len(block1):
                block1_pointer = 0
                try:
                    block1 = next(file1_generator)
                except StopIteration:
                    break

            if block2_pointer == len(block2):
                block2_pointer = 0
                try:
                    block2 = next(file2_generator)
                except StopIteration:
                    break

            block1_value = block1[block1_pointer]
            block2_value = block2[block2_pointer]

            if block1_value == block2_value:
                result_hash.add(block1_value)
                block1_pointer += 1
                block2_pointer += 1
            elif block1_value < block2_value:
                block1_pointer += 1
            else:
                block2_pointer += 1

        return result_hash
