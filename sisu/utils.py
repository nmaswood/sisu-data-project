import union.constants as c

import random as r


def write_fake_data(file_name, size, batch_size):

    with open(file_name, 'w') as fp:

        range_ = range(c.MIN_NUMBER, c.MAX_NUMBER)

        for _ in range(0, size, batch_size):

            k_random_nums = r.sample(range_, batch_size)

            as_str = '\n'.join([str(num) for num in k_random_nums])

            fp.write(as_str)
