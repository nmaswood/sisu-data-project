import os
import tempfile
from itertools import islice
from glob import iglob

from pybloom_live import ScalableBloomFilter
import sisu.utils as u
import sisu.constants as c


class _DiskHash():
    """A _DiskHash is a simple data structure that uses a
    direcotry as a simple a hash map. Each write adds a file
    to a directory, where the name of the file corresponds
    to the name of the element.
    """

    def __init__(self):
        """
        Attributes
        ---------
        cardinality : int
            The amount of elements in the hash
        dir : TemporaryDirectory
            Output dir for values in the hash
        """
        self.cardinality = 0
        self.dir = tempfile.TemporaryDirectory()

    @u.require_int
    def __contains__(self, element):
        """Returns true if element present in map
        Performs 1 random seek.

        Parameters
        ----------
        element : int
            Integer to check existence of

        Returns
        ------
        bool
        """

        path = f'{self.dir.name}/{element}'
        return os.path.isfile(path)

    @u.require_int
    def add(self, element):
        """Adds element to set by writing a file to disk
        with the element as the name of the file.

        NOTE: This function assumes that the caller
        has already checked if the element is present in
        the set

        Parameters
        ----------
        element : int
            Integer to check existence of

        Returns
        ------
        element : int
        """
        path = f'{self.dir.name}/{element}'
        with open(path, 'a'):
            pass
        self.cardinality += 1
        return element

    def flush(self, output, block_size):
        """Writes all elements in set to `output` path
        `block_size` elements at a time.

        Parameters
        ----------
        output : str
            Path to write to
        block_size : int
            Number of elements to write at a single time.

        Side Effect
        ------
        Writes a file
        """
        files = iglob(f'{self.dir.name}/*')

        def _process(x):
            return os.path.split(x)[-1] + '\n'

        with open(output, 'a') as outfile:
            while True:
                chunk = islice(files, block_size)
                new_lines = [_process(file_) for file_ in chunk]
                if not new_lines:
                    break
                new_lines = ''.join(new_lines)
                outfile.write(new_lines)


class SpillableHash():
    """A SpillableHash is set data structure which keeps elements
    until memory until it reaches its set capacity wherein it spills
    to a disk map backed by a scalable bloomfilter.
    """

    def __init__(self, capacity):
        """
        Attributes
        ---------
        cardinality : int
            The amount of elements in the hash
        capacity : int
            The amount of ints the hash can fit in memory
        dir : TemporaryDirectory
            Output dir for values in the hash
        _mem : set of int
            In memory set of items
        _bloom : ScalableBloomFilter
            Bloom filter which is used when mem capacity is reached
        _disk:  _DiskHash
            On disk hash where values spill
        """
        self.cardinality = 0
        self.capacity = capacity
        self._mem = set()
        # figure out memory profile of bloom filter
        self._bloom = ScalableBloomFilter(
            mode=ScalableBloomFilter.SMALL_SET_GROWTH
        )
        self._disk = _DiskHash()

    @property
    def _mem_full(self):
        """Has in memory capacity been reached?

        Returns
        ------
        bool
        """
        return self.cardinality >= self.capacity

    @property
    def available_memory(self):
        """Returns the amount memory in bytes that was given to the hash
        map but not used.

        Returns
        ------
        int (in bytes)

        """
        if self._mem_full:
            return 0

        return (self.capacity - self.cardinality) * c.SIZE_INT

    @u.require_int
    def __contains__(self, number):
        """Is this number is any of the sets?
        Parameters
        ----------
        element : int
            Integer to check existence of

        Returns
        ------
        element : int
        """

        if number in self._mem:
            return True
        elif not self._mem_full:
            return False

        if number not in self._bloom:
            return False

        return number in self._disk

    @u.require_int
    def add(self, element):
        """Adds element to set by adding it to memory or disk.

        Parameters
        ----------
        element : int
            Integer to check existence of

        Returns
        ------
        element : int
        """

        if element in self._mem:
            return element

        if not self._mem_full:
            self.cardinality += 1
            self._mem.add(element)
            return element

        # we are making the assumption that
        # `each integer appears at most once in each file.`
        # can never write same int twice
        # otherwise uncoment the following line

        # if element not in self._bloom or element not in self._disk:

        self._bloom.add(element)
        self._disk.add(element)
        self.cardinality += 1

        return element

    def flush(self, output, block_size):
        """Writes all elements in set to `output` path
        `block_size` elements at a time.

        Parameters
        ----------
        output : str
            Path to write to
        block_size : int
            Number of elements to write at a single time.

        Side Effect
        ------
        Writes a file
        """
        acc = []

        with open(output, 'a') as outfile:
            for idx, num in enumerate(self._mem):

                as_str = f'{num}\n'
                acc.append(as_str)
                if idx % block_size == 0:
                    outfile.write(''.join(acc))
                    acc = []
            if acc:
                outfile.write(''.join(acc))
                acc = []

        self._disk.flush(output, block_size)
