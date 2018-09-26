from abc import ABCMeta, abstractmethod


class Strategy(metaclass=ABCMeta):
    """
    A strategy is a class that implements a method called intersect.
    The function takes two file paths specified as strings and a memory limit.
    Each file path leads to a \n delimited file of ints in the range

    [0, 2^63]
    """
    @abstractmethod
    def intersect(file1, file2, mem_limit):
        raise NotImplementedError('Implement this method.')


class Naive(Strategy):
    """
    The naive strategy is a dummy testing solution that ignores the mem_limit
    parameter. This solution is intended as a base line benchmark.
    """
    @staticmethod
    def intersect(file1, file2, _):
        with open(file1, 'r') as f1, open(file2, 'r') as f2:

            file1_ids = set(f1.readlines())
            file2_ids = set(f2.readlines())

        return file1_ids.intersect(file2_ids)


class Block(Strategy):
    @staticmethod
    def intersect(file1, file2, mem_limit):
        pass


class Merge(Strategy):
    @staticmethod
    def intersect(file1, file2, mem_limit):
        pass


class Hash(Strategy):
    @staticmethod
    def intersect(file1, file2, mem_limit):
        pass
