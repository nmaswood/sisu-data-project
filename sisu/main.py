import sisu.utils as utils
import sisu.optimize as optimize

from pdb import set_trace


def main():
    args = utils.parse_args()
    strategy = optimize.optimal_strategy(args.file_1, args.file_2,
                                         args.mem_limit)

    res = strategy.intersect(args.file_1, args.file_2, args.mem_limit)
    print(res.cardinality)


if __name__ == '__main__':
    main()
