import os
import fcntl
import sys
import logging
from ioctl_opt import IOC, IOC_READ, IOC_WRITE
from pytest import fixture

STACK_SIZE = 10


@fixture
def open_device(logger):
    logger.set_level(logging.INFO)
    dev = os.open("/dev/stack", os.O_RDWR)
    yield dev
    os.close(dev)


def read(device, cnt: int) -> list[int]:
    res = os.read(device, cnt * 4)
    ret = []
    for i in range(0, int(len(res) / 4)):
        print(res[i*4: (i+1) * 4])
        ret.append(int.from_bytes(
            res[i * 4: (i+1) * 4], byteorder=sys.byteorder))

    return ret


def write(device, nums: list[int]):
    bytelist = bytes()
    for num in nums:
        byted = num.to_bytes(4, byteorder=sys.byteorder)
        bytelist += byted

    return os.write(device, bytelist) / 4


def change_size(device, new_size):
    cmd = IOC(IOC_WRITE, ord('a'), 0x01, 8)
    ret = fcntl.ioctl(device, cmd, new_size)
    return ret
