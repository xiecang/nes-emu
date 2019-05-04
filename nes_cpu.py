# -*- coding: utf-8 -*-
from typing import (
    Dict, List, Tuple, Optional
)

import opcodes_table
import utils
import nes_file as nf


class NesCPU(object):
    def __init__(self):
        self._reg_values = None
        self._memory = None
        self._opcodes = None
        self._p_masks = None

        self._setup()

    def _setup(self):
        # at power-up
        self._reg_values: Dict[str, int] = {
            'PC': 0,
            'P': 0x34,
            'A': 0,
            'X': 0,
            'Y': 0,
            'S': 0xfd,
        }
        self._memory: List[int] = [0] * 64 * 1024

        self._opcodes: Dict[int, Tuple[str, str]] = opcodes_table.opcodes

        self._p_masks: Dict[str, int] = {
            'N': 0b10000000,
            'V': 0b01000000,
            'D': 0b00001000,
            'I': 0b00000100,
            'Z': 0b00000010,
            'C': 0b00000001,
        }

    def load_nes(self, nes: nf.NesFile):
        self._memory[0x8000:0xc000] = nes.prg_rom
        self._memory[0xc000:] = nes.prg_rom

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
        if mode == 'IMP':
            return None
        elif mode == 'IMM':
            a = self.next_mem_value()
            return a
        elif mode == 'ABS':
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

    def flag(self, bit: str):
        b = bit.upper()
        m = self._p_masks[b]
        p = self.reg_value('p')
        f = p & m
        return f != 0

    def set_flag(self, bit: str, switch_on: bool):
        b = bit.upper()
        p = self.reg_value('p')
        m = self._p_masks[b]
        if switch_on:
            p |= m
        else:
            p &= ~m
        self.set_reg_value('p', p)

    def execute(self):
        args = self._prepare()
        self._execute(*args)

    def _prepare(self):
        c = self.next_mem_value()
        op, mode = self._opcodes[c]
        addr = self.address(mode)
        return op, addr, mode == 'IMM'

    def _execute(self, op: str, addr: Optional[int], immediate: bool):
        if immediate or addr is None:
            # 立即寻址 和 隐含寻址 情况
            mvalue = addr
        else:
            mvalue = self.mem_value(addr)

        utils.log(f'mvalue: {mvalue}')

        if op == 'JMP':
            self.set_reg_value('pc', addr)
        elif op == 'LDX':
            v = mvalue
            self.set_reg_value('x', v)
            self.set_flag('z', v == 0)
            self.set_flag('n', v & 0b01000000 != 0)
        elif op == 'STX':
            v = self.reg_value('x')
            self.set_mem_value(addr, v)
        else:
            raise ValueError('错误的 op： <{}>'.format(op))
