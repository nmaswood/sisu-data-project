import sisu.spillable_hash as spillable
import sisu.utils as utils


def test_disk_hash(tmpdir):
    disk_hash = spillable._DiskHash()
    range_limit = 10

    # add
    for i in range(range_limit):
        disk_hash.add(i)

    # __contains__
    for i in range(range_limit):
        assert i in disk_hash

    assert range_limit not in disk_hash

    # flush
    path = f'{tmpdir}/out'
    disk_hash.flush(path, 2)
    nums = utils.read_nums(path)

    assert nums == set(range(range_limit))


def test_spillable_hash(tmpdir):
    capacity = 5
    spillable_hash = spillable.SpillableHash(capacity)
    range_ = 10

    # add
    for i in range(range_):
        spillable_hash.add(i)

    # __contains__
    for i in range(range_):
        assert i in spillable_hash
    assert 1234 not in spillable_hash

    # attributes
    assert spillable_hash.cardinality == range_
    assert len(spillable_hash._mem) == capacity
    assert spillable_hash._disk.cardinality == range_ - capacity

    # props
    assert spillable_hash._mem_full
    assert spillable_hash.available_memory == 0

    # flush
    output = f'{tmpdir}/out'
    block_size = 10
    spillable_hash.flush(output, block_size)
    nums_from_disk = utils.read_nums(output)

    assert set(nums_from_disk) == set(range(range_))
