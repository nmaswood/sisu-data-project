import time

import sisu.optimize as optimize
import sisu.utils as utils


def main():
    """Parse arguments, determine the optimal strategy
    and then call that strategy with the given params.

    Print the cardinality of the result hash to get a final
    result
    """
    args = utils.parse_args()
    strategy = optimize.optimal_strategy(args.file_1, args.file_2,
                                         args.mem_limit)

    start = time.time()
    print('Beginning operation')
    res = strategy.intersect(args.file_1, args.file_2, args.mem_limit)
    end = time.time()
    print(res.cardinality)
    print(f'Operation completed in {end - start} seconds')


if __name__ == '__main__':
    main()
