import logging
import errno
import sys
import pytest
import os
from device import STACK_SIZE, open_device, read_nums, write_nums, change_size


def test_delete_by_singles(dev):
    dev = open_device

    for i in range(STACK_SIZE):
        assert write_nums(dev, [i + 1]) == 1

    for i in range(STACK_SIZE):
        ret = read_nums(dev, 1)
        assert len(ret) == 1
        assert ret[0] == STACK_SIZE - i


def test_delete_by_multiples(open_device):
    fix = open_device
    to_add = [i + 1 for i in range(STACK_SIZE)]

    assert write_nums(fix, to_add) == len(to_add)
    assert read_nums(fix, STACK_SIZE) == list(reversed(to_add))


def test_partial_write_read(open_device):
    fix = open_device

    add_size = STACK_SIZE * 3
    to_add = [i + 1 for i in range(add_size)]

    assert write_nums(fix, to_add) == STACK_SIZE
    assert read_nums(fix, add_size) == list(reversed(to_add[0:STACK_SIZE]))


def test_write_non_algined_byte(open_device):
    fix = open_device

    input = b'\xDE\xAD\xDE'
    output = b'\xDE\xAD\xDE\x00'

    assert os.write(fix, bytelist) == len(input)
    assert read_nums(fix, 1) == [int.from_bytes(
        output, byteorder=sys.byteorder)]


def test_overflow(open_device):
    fix = open_device

    assert write_nums(fix, [0 for i in range(STACK_SIZE)]) == STACK_SIZE

    with pytest.raises(OSError) as e_info:
        write_nums(fix, [1337])

    assert e_info.value.errno == errno.ENOBUFS

    assert len(read_nums(fix, STACK_SIZE)) == STACK_SIZE


def test_underflow(open_device):
    fix = open_device

    with pytest.raises(OSError) as e_info:
        read_nums(fix, 1)

    assert e_info.value.errno == errno.ENOSPC


def test_basic_resize(open_device):
    fix = open_device
    new_size = 2

    assert change_size(fix, new_size) == 0

    assert write_nums(fix, [i for i in range(
        new_size + 1)]) == new_size
    assert read_nums(fix, new_size) == list(
        reversed([i for i in range(new_size)]))

    assert change_size(fix, STACK_SIZE) == 0


def test_resize_to_smaller_than_actual(open_device):
    fix = open_device
    new_size = 7

    assert write_nums(fix, [i for i in range(STACK_SIZE)]) == STACK_SIZE

    assert change_size(fix, new_size) == 0
    assert len(read_nums(fix, STACK_SIZE)) == new_size

    assert change_size(fix, STACK_SIZE) == 0


def test_read_after_resize(open_device):
    fix = open_device
    new_size = 8

    assert write_nums(fix, [i for i in range(new_size)]) == new_size
    assert change_size(fix, new_size - 1) == 0

    assert read_nums(fix, new_size) == list(
        reversed([i for i in range(new_size - 1)]))

    assert change_size(fix, STACK_SIZE) == 0
