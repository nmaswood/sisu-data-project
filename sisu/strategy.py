from abc import ABCMeta, abstractmethod

from sisu.spillable_hash import SpillableHash
import sisu.utils as utils


class Strategy(metaclass=ABCMeta):
    """A strategy is an interface which expects a method called intersect to
    be implemented.

    The function takes two file paths specified as strings and a memory limit.
    Each file path is a  \n delimited file of ints in the range [0, 2^63]

    Given those three inputs a Strategy returns a SpillableHash which contains
    the result set.
    """
    @abstractmethod
    def intersect(file1, file2, mem_limit):
        """Returns a SpillableHash containing the intersecting values

        Parameters
        ----------
        file1 : str
        file2: str
        mem_limit: float

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
    def intersect(file1, file2, _):
        with open(file1, 'r') as f1, open(file2, 'r') as f2:

            file1_ids = {int(num.strip()) for num in f1.readlines()}
            file2_ids = {int(num.strip()) for num in f2.readlines()}

        hash_map = SpillableHash(float('inf'))
        for num in file1_ids.intersection(file2_ids):
            hash_map.add(num)
        return hash_map


class Hash(Strategy):
    @staticmethod
    def intersect(file1, file2, mem_limit):
        """The Hash strategy builds a hash table over the smaller file.
        It then walks through the numbers in the larger file and records
        ids present from second file that in the first.
        """

        file1_hash = SpillableHash(mem_limit)
        for block in utils.read_file_by_block(file1):
            for number in block:
                file1_hash.add(number)

        result_hash = SpillableHash(mem_limit)

        for block in utils.read_file_by_block(file2):
            for number in block:
                if number in file1_hash:
                    file1_hash.add(number)

        return result_hash


class Merge(Strategy):
    @staticmethod
    def sort(file1, file2, mem_limit):
        pass

    @staticmethod
    def intersect(file1, file2, mem_limit):
        pass
