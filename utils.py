# -*- coding: utf-8 -*-
from typing import List


def log(*args, **kwargs):
    print(*args, **kwargs)


def signed_number(byte_list: List[int]):
    """
    [1]         => 1
    [0, 1]      => 256
    [255]       => -1
    [0, 255]    => -256
    [255, 255]  => -1
    [256]       => 因为 256 > 255 所以 raise Exception
    """
    bs = bytes(byte_list)
    return int.from_bytes(bs, 'little', signed=True)
