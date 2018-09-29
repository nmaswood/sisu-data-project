# sisu-data-project

Intersection between two lists of files on disk.

## Setup

`conda create -n sisuenv anaconda python=3.6`

`source activate sisuenv`

`pip install -e .'[dev]'`

`python3 setup.py install`


## Testing

__This seeds the data dir for testing.__

`python sisu/util.py`

You can now run unit tests

`pytest sisu/tests`

`python3 sisu/main.py --file_1 sisu/tests/data/medium-large-same-0.lst --file_2 sisu/tests/data/medium-large-same-1.lst --mem_limit 25`

__if you uncomment the tests for `medium-large/large` files in `test_strategy` tests will take a very long time to run.__

## Running

`python3 sisu/main.py --file_one XYZ --file_two ABC --mem_limit 123`

## Notes

When `mem_limit` exceeds file size things slow down considerably. Probably as to be expected...

If I worked on this more, two things I would do:

* find a way to improve performance of `SpillableHash`. I think in retrospect this was the design decesion that adversely effected performance the most. I believe other implementations of hash join iterate over the data multiple times to get around having to spill values to disk and, without trying it, I think that may be a better way.
* Use gridsearch to find optimal values for allocating/tuning memory. i.e. (see
    `determine_memory` functions in `strategy.py`


## Problem

Given two files, each containing a list of integer-valued IDs, write a program that prints the total number of IDs that appear in both files. The program should use no more memory than a pre-specified budget.


* The implementation should take as command-line input the relative paths to the two files, along with a maximum memory limit, in megabytes.

* Your implementation should assume the input is stored in ASCII text, with one integer (with value ranging from 0 to 2^63) per line, and that each integer appears at most once in each file.

* Your implementation can assume that the memory budget will be no smaller than 1MB, and the input files will be no larger than 500MB, and should execute as efficiently as possible while respecting the memory budget.

* Your implementation should optimize for the cases where inputs may be larger than and smaller than the memory budget, and when the inputs are different sizes.

* If your implementation needs to write to disk, it can write to files in the `/tmp` directory, but it should also clean up after itself.


* Please submit both code and test cases, as well as a short summary of how you optimized your implementation.


* The goal of this task is to write very efficient, production-quality code, so please take the time to document the code, test it, optimize it, etc. as you would for real, performance-critical production code.
