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
            'B': 0b00010000,
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
            return (a + i) % 256
        elif mode == 'ZPY':
            a = self.next_mem_value()
            i = self.reg_value('y')
            return (a + i) % 256
        elif mode == 'IND':
            tal = self.next_mem_value()
            tah = self.next_mem_value()
            ta = utils.number_from_bytes([tal, tah])
            # 模拟 6502 的 BUG
            ta2 = (ta & 0xFF00) | ((ta + 1) & 0x00FF)

            al = self.mem_value(ta)
            ah = self.mem_value(ta2)
            a = utils.number_from_bytes([al, ah])

            return a
        elif mode == 'INX':
            t = self.next_mem_value()
            i = self.reg_value('x')
            ta = (t + i) % 256
            ta2 = (ta + 1) % 256

            al = self.mem_value(ta)
            ah = self.mem_value(ta2)
            a = utils.number_from_bytes([al, ah])

            return a
        elif mode == 'INY':
            ta = self.next_mem_value()
            ta2 = (ta + 1) % 256

            al = self.mem_value(ta)
            ah = self.mem_value(ta2)
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

    def push(self, value: int):
        s = self.reg_value('s')
        addr = s + 0x0100
        self.set_mem_value(addr, value)
        self.set_reg_value('s', s - 1)

    def pop(self):
        s = self.reg_value('s')
        s += 1
        addr = s + 0x0100
        self.set_reg_value('s', s)
        v = self.mem_value(addr)
        return v

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
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'STX':
            v = self.reg_value('x')
            self.set_mem_value(addr, v)
        elif op == 'JSR':
            pc = self.reg_value('pc')
            v = pc - 1
            self.push((v & 0xff00) >> 8)
            self.push(v & 0x00ff)
            self.set_reg_value('pc', addr)
        elif op == 'NOP':
            # do nothing
            pass
        elif op == 'SEC':
            self.set_flag('c', True)
        elif op == 'BCS':
            f = self.flag('c')
            if f:
                self.set_reg_value('pc', addr)
        elif op == 'CLC':
            self.set_flag('c', False)
        elif op == 'BCC':
            f = self.flag('c')
            if not f:
                self.set_reg_value('pc', addr)
        elif op == 'LDA':
            v = mvalue
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'BEQ':
            f = self.flag('z')
            if f:
                self.set_reg_value('pc', addr)
        elif op == 'BNE':
            f = self.flag('z')
            if not f:
                self.set_reg_value('pc', addr)
        elif op == 'STA':
            v = self.reg_value('a')
            self.set_mem_value(addr, v)
        elif op == 'BIT':
            v = mvalue
            a = self.reg_value('a')
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('v', v & 0b01000000 != 0)
            self.set_flag('z', v & a == 0)
        elif op == 'BVS':
            f = self.flag('v')
            if f:
                self.set_reg_value('pc', addr)
        elif op == 'BVC':
            f = self.flag('v')
            if not f:
                self.set_reg_value('pc', addr)
        elif op == 'BPL':
            f = self.flag('n')
            if not f:
                self.set_reg_value('pc', addr)
        elif op == 'RTS':
            vl = self.pop()
            vh = self.pop()
            v = utils.number_from_bytes([vl, vh])
            pc = v + 1
            self.set_reg_value('pc', pc)
        elif op == 'SEI':
            self.set_flag('i', True)
        elif op == 'SED':
            self.set_flag('d', True)
        elif op == 'PHP':
            # 在这条指令中，只有「被压入栈」的 P 的 B flag 被置为 True
            bv = self.reg_value('p')

            self.set_flag('b', True)
            v = self.reg_value('p')
            self.push(v)

            self.set_reg_value('p', bv)
        elif op == 'PLA':
            v = self.pop()
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'AND':
            v = mvalue
            r = self.reg_value('a')
            v = r & v
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'CMP':
            v = mvalue
            r = self.reg_value('a')
            v = r - v
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            self.set_flag('c', v >= 0)
        elif op == 'CLD':
            self.set_flag('d', False)
        elif op == 'PHA':
            v = self.reg_value('a')
            self.push(v)
        elif op == 'PLP':
            v = self.pop()
            # 从栈里弹出的值，外面不会作用到 P 的 B flag 上
            for b in 'NVDIZC':
                m = self._p_masks[b]
                f = v & m != 0
                self.set_flag(b, f)
        elif op == 'BMI':
            f = self.flag('n')
            if f:
                self.set_reg_value('pc', addr)
        elif op == 'ORA':
            v = mvalue
            r = self.reg_value('a')
            v = r | v
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'CLV':
            self.set_flag('v', False)
        elif op == 'EOR':
            v = mvalue
            r = self.reg_value('a')
            v = r ^ v
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'ADC':
            v = mvalue
            r = self.reg_value('a')
            if self.flag('c'):
                c = 1
            else:
                c = 0
            v = r + v + c
            # C flag: set if overflow
            if v > 255:
                v -= 256
                self.set_flag('c', True)
            else:
                self.set_flag('c', False)
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            # 处理 v flag
            v = utils.number_from_bytes([mvalue], signed=True)
            r = utils.number_from_bytes([r], signed=True)
            v = r + v + c
            self.set_flag('v', v > 128 or v < -127)
        elif op == 'LDY':
            v = mvalue
            self.set_reg_value('y', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'CPY':
            v = mvalue
            r = self.reg_value('y')
            v = r - v
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            self.set_flag('c', v >= 0)
        elif op == 'CPX':
            v = mvalue
            r = self.reg_value('x')
            v = r - v
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            self.set_flag('c', v >= 0)
        elif op == 'SBC':
            v = mvalue
            r = self.reg_value('a')
            if self.flag('c'):
                c = 1
            else:
                c = 0
            v = r - v - (1 - c)
            # C flag: clear if overflow
            if v < 0:
                v += 256
                self.set_flag('c', False)
            else:
                self.set_flag('c', True)
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            # 处理 v flag
            v = utils.number_from_bytes([mvalue], signed=True)
            r = utils.number_from_bytes([r], signed=True)
            v = r - v - (1 - c)
            self.set_flag('v', v > 128 or v < -127)
        elif op == 'INY':
            v = self.reg_value('y')
            v += 1
            v %= 256
            self.set_reg_value('y', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'INX':
            v = self.reg_value('x')
            v += 1
            v %= 256
            self.set_reg_value('x', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'DEY':
            v = self.reg_value('y')
            v -= 1
            v %= 256
            self.set_reg_value('y', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'DEX':
            v = self.reg_value('x')
            v -= 1
            v %= 256
            self.set_reg_value('x', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'TAY':
            v = self.reg_value('a')
            self.set_reg_value('y', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'TAX':
            v = self.reg_value('a')
            self.set_reg_value('x', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'TYA':
            v = self.reg_value('y')
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'TXA':
            v = self.reg_value('x')
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'TSX':
            v = self.reg_value('s')
            self.set_reg_value('x', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'TXS':
            v = self.reg_value('x')
            self.set_reg_value('s', v)
        elif op == 'RTI':
            v = self.pop()
            # 从栈里弹出的值，外面不会作用到 P 的 B flag 上
            for b in 'NVDIZC':
                m = self._p_masks[b]
                f = v & m != 0
                self.set_flag(b, f)
            vl = self.pop()
            vh = self.pop()
            v = utils.number_from_bytes([vl, vh])
            # 这里不需要像 RTS 一样 +1
            pc = v
            self.set_reg_value('pc', pc)
        else:
            raise ValueError('错误的 op： <{}>'.format(op))
