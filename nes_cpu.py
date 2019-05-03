# -*- coding: utf-8 -*-
from typing import (
    Dict, List, Tuple
)

import opcodes_table
import utils


class NesCPU(object):
    def __init__(self):
        self._reg_values = None
        self._memory = None
        self._opcodes = None

        self._setup()

    def _setup(self):
        # at power-up
        self._reg_values: Dict[str, int] = {
            'PC': 0x34,
            'P': 0,
            'A': 0,
            'X': 0,
            'Y': 0,
            'S': 0xfd,
        }
        self._memory: List[int] = [0] * 64 * 1024

        self._opcodes: Dict[int, Tuple[str, str]] = opcodes_table.opcodes

    def reg_value(self, name: str):
        n = name.upper()
        return self._reg_values[n]

    def set_reg_value(self, name: str, value: int):
        n = name.upper()

        if n not in self._reg_values:
            raise ValueError('未知的寄存器：<{}>'.format(n))
        if n == 'PC':
            if value < 0 or value > 2 ** 16 - 1:
                raise ValueError('<{}>超过了<{}>寄存器的取值范围'.format(value, n))
        else:
            if value < 0 or value > 2 ** 8 - 1:
                raise ValueError('<{}>超过了<{}>寄存器的取值范围'.format(value, n))

        self._reg_values[n] = value

    def reset(self):
        s = self.reg_value('s')
        self.set_reg_value('s', s - 3)

    def mem_value(self, addr: int):
        return self._memory[addr]

    def set_mem_value(self, addr: int, value: int):
        if value < 0 or value > 2 ** 8 - 1:
            raise ValueError(f'<{value}>超过了字节的取值范围')
        self._memory[addr] = value

    def next_mem_value(self):
        pc = self.reg_value('pc')
        v = self.mem_value(pc)
        self.set_reg_value('pc', pc + 1)
        return v

    def address(self, mode: str):
        if mode == 'ABS':
            al = self.next_mem_value()
            ah = self.next_mem_value()
            a = utils.number_from_bytes([al, ah])
            return a
        elif mode == 'ZPG':
            a = self.next_mem_value()
            return a
        elif mode == 'ABX':
            al = self.next_mem_value()
            ah = self.next_mem_value()
            a = utils.number_from_bytes([al, ah])
            i = self.reg_value('x')
            return a + i
        elif mode == 'ABY':
            al = self.next_mem_value()
            ah = self.next_mem_value()
            a = utils.number_from_bytes([al, ah])
            i = self.reg_value('y')
            return a + i
        elif mode == 'ZPX':
            a = self.next_mem_value()
            i = self.reg_value('x')
            return a + i
        elif mode == 'ZPY':
            a = self.next_mem_value()
            i = self.reg_value('y')
            return a + i
        elif mode == 'IND':
            tal = self.next_mem_value()
            tah = self.next_mem_value()
            ta = utils.number_from_bytes([tal, tah])

            al = self.mem_value(ta)
            ah = self.mem_value(ta + 1)
            a = utils.number_from_bytes([al, ah])

            return a
        elif mode == 'INX':
            t = self.next_mem_value()
            i = self.reg_value('x')
            ta = t + i

            al = self.mem_value(ta)
            ah = self.mem_value(ta + 1)
            a = utils.number_from_bytes([al, ah])

            return a
        elif mode == 'INY':
            ta = self.next_mem_value()

            al = self.mem_value(ta)
            ah = self.mem_value(ta + 1)
            a = utils.number_from_bytes([al, ah])

            i = self.reg_value('y')
            return a + i
        elif mode == 'REL':
            diff = self.next_mem_value()
            diff = utils.number_from_bytes([diff], signed=True)
            pc = self.reg_value('pc')
            return pc + diff
        else:
            raise ValueError('错误的寻址模式：<{}>'.format(mode))
