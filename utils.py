# -*- coding: utf-8 -*-
from typing import List


def log(*args, **kwargs):
    print(*args, **kwargs)


def number_from_bytes(byte_list: List[int], *, signed=False):
    """
    [1]                      => 1
    [0, 1]                   => 256
    [255]                    => 255
    [255], signed=True       => -1
    [255, 255], signed=True  => -1
    [256]                    => 因为 256 > 255 所以 raise Exception
    """
    bs = bytes(byte_list)
    return int.from_bytes(bs, 'little', signed=signed)
