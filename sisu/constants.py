import sys

MIN_NUMBER = 0
MAX_NUMBER = 1 << 63

BYTE = 1

MEGABYTE = BYTE << 20
MIN_MEMORY_BUDGET = MEGABYTE
MAX_FILE_SIZE = 500 * MEGABYTE

SIZE_INT = sys.getsizeof(int())

# when we read a an element from the list
# it is not stored as an int but rather as a array of
# ascii chars. Therefore we account for the largest
# possible size of a line by taking the size of the
# biggest possible number
LARGEST_ELEMENT_SIZE = sys.getsizeof(str(MAX_NUMBER))
