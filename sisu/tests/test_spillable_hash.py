import sisu.spillable_hash as spillable
import sisu.utils as utils


def test_disk_hash(tmpdir):
    disk_hash = spillable._DiskHash()
    range_limit = 10

    for i in range(range_limit):
        disk_hash.add(i)

    for i in range(range_limit):
        assert i in disk_hash

    assert range_limit not in disk_hash

    path = f'{tmpdir}/out'
    disk_hash.flush(path, 2)
    with open(path, 'r') as infile:
        nums = infile.readlines()
    nums = {int(num.strip()) for num in nums}

    assert nums == set(range(range_limit))


def test_spillable_hash(tmpdir):
    capacity = 5
    spillable_hash = spillable.SpillableHash(capacity)
    range_ = 10

    for i in range(range_):
        spillable_hash.add(i)

    assert spillable_hash.cardinality == range_
    assert len(spillable_hash._mem) == capacity
    assert spillable_hash._disk.cardinality == range_ - capacity

    output = f'{tmpdir}/out'
    block_size = 10
    spillable_hash.flush(output, block_size)
    nums_from_disk = sum(
        list(utils.read_file_by_block(output, block_size)), []
    )

    assert set(nums_from_disk) == set(range(range_))
