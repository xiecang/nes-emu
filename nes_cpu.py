# -*- coding: utf-8 -*-
from typing import (
    Dict, List, Tuple, Optional
)

import pygame
import config
import opcodes_table
from utils import log, number_from_bytes
import nes_file as nf
from log_differ import LogDiffer
from nes_ppu import NesPPU


class NesCPU(object):
    def __init__(self):
        self.registers: Dict[str, int] = None
        self.ram: List[int] = None
        self.prg_rom: List[int] = None
        self.opcodes: Dict[int, Tuple[str, str]] = None
        self.p_masks: Dict[str, int] = None
        self.ppu = NesPPU()

        self.setup()

    def setup(self):
        # at power-up
        self.registers = {
            'PC': 0,
            'P': 0x34,
            'A': 0,
            'X': 0,
            'Y': 0,
            'S': 0xfd,
        }
        self.ram = [0] * 0x2000
        self.opcodes = opcodes_table.opcodes
        self.p_masks = {
            'N': 0b10000000,
            'V': 0b01000000,
            'B': 0b00010000,
            'D': 0b00001000,
            'I': 0b00000100,
            'Z': 0b00000010,
            'C': 0b00000001,
        }

    def load_nes(self, nes: nf.NesFile):
        self.prg_rom = nes.prg_rom
        self.ppu.load_nes(nes)

    def reg_value(self, name: str):
        n = name.upper()
        return self.registers[n]

    def set_reg_value(self, name: str, value: int):
        n = name.upper()

        if n not in self.registers:
            raise ValueError('未知的寄存器：<{}>'.format(n))
        if n == 'PC':
            if value < 0 or value > 2 ** 16 - 1:
                raise ValueError('<{}>超过了<{}>寄存器的取值范围'.format(value, n))
        else:
            if value < 0 or value > 2 ** 8 - 1:
                raise ValueError('<{}>超过了<{}>寄存器的取值范围'.format(value, n))

        self.registers[n] = value

    def mem_value(self, addr: int):
        if 0 <= addr <= 0x1fff:
            return self.ram[addr]
        elif 0x2000 <= addr <= 0x2007:
            return self.ppu.reg_value_for_cpu(addr)
        elif 0x2008 <= addr <= 0x3fff:
            # 主动忽略
            return 0
        elif 0x4000 <= addr <= 0x4013:
            # 主动忽略
            return 0
        elif addr == 0x4014:
            return self.ppu.reg_value_for_cpu(addr)
        elif 0x4015 <= addr <= 0x5fff:
            # 主动忽略
            return 0
        elif 0x8000 <= addr <= 0xbfff:
            addr -= 0x8000
            return self.prg_rom[addr]
        elif 0xc000 <= addr <= 0xffff:
            addr -= 0xc000
            return self.prg_rom[addr]
        else:
            raise ValueError('错误的读地址：<{}>'.format(addr))

    def set_mem_value(self, addr: int, value: int):
        # log('set_mem_value: ', hex(addr), hex(value))
        if value < 0 or value > 2 ** 8 - 1:
            raise ValueError('<{}>超过了字节的取值范围'.format(value))

        if 0 <= addr <= 0x1fff:
            self.ram[addr] = value
        elif 0x2000 <= addr <= 0x2007:
            self.ppu.set_reg_value_for_cpu(addr, value)
        elif 0x2008 <= addr <= 0x3fff:
            # 主动忽略
            pass
        elif 0x4000 <= addr <= 0x4013:
            # 主动忽略
            pass
        elif addr == 0x4014:
            self.ppu.set_reg_value_for_cpu(addr, value)
        elif 0x4015 <= addr <= 0x5fff:
            # 主动忽略
            pass
        else:
            raise ValueError('错误的写地址：<{}>'.format(addr))

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
            a = number_from_bytes([al, ah])
            return a
        elif mode == 'ZPG':
            a = self.next_mem_value()
            return a
        elif mode == 'ABX':
            al = self.next_mem_value()
            ah = self.next_mem_value()
            a = number_from_bytes([al, ah])
            i = self.reg_value('x')
            return (a + i) % 0x10000
        elif mode == 'ABY':
            al = self.next_mem_value()
            ah = self.next_mem_value()
            a = number_from_bytes([al, ah])
            i = self.reg_value('y')
            return (a + i) % 0x10000
        elif mode == 'ZPX':
            a = self.next_mem_value()
            i = self.reg_value('x')
            return (a + i) % 0x100
        elif mode == 'ZPY':
            a = self.next_mem_value()
            i = self.reg_value('y')
            return (a + i) % 0x100
        elif mode == 'IND':
            tal = self.next_mem_value()
            tah = self.next_mem_value()
            ta = number_from_bytes([tal, tah])
            # 模拟 6502 的 BUG
            ta2 = (ta & 0xFF00) | ((ta + 1) & 0x00FF)

            al = self.mem_value(ta)
            ah = self.mem_value(ta2)
            a = number_from_bytes([al, ah])

            return a
        elif mode == 'INX':
            t = self.next_mem_value()
            i = self.reg_value('x')
            ta = (t + i) % 0x100
            ta2 = (ta + 1) % 0x100

            al = self.mem_value(ta)
            ah = self.mem_value(ta2)
            a = number_from_bytes([al, ah])

            return a
        elif mode == 'INY':
            ta = self.next_mem_value()
            ta2 = (ta + 1) % 0x100

            al = self.mem_value(ta)
            ah = self.mem_value(ta2)
            a = number_from_bytes([al, ah])

            i = self.reg_value('y')
            return (a + i) % 0x10000
        elif mode == 'REL':
            diff = self.next_mem_value()
            diff = number_from_bytes([diff], signed=True)
            pc = self.reg_value('pc')
            return (pc + diff) % 0x10000
        else:
            raise ValueError('错误的寻址模式：<{}>'.format(mode))

    def flag(self, bit: str):
        b = bit.upper()
        m = self.p_masks[b]
        p = self.reg_value('p')
        f = p & m
        return f != 0

    def set_flag(self, bit: str, switch_on: bool):
        b = bit.upper()
        p = self.reg_value('p')
        m = self.p_masks[b]
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

    def draw(self, canvas: pygame.Surface):
        self.ppu.draw(canvas)

    def execute(self):
        # for debug
        info = {}
        if config.DEBUG:
            info.update(self.registers)

        op, addr, mode = self._prepare()

        if config.DEBUG:
            info['op'] = op
            info['address'] = addr if addr is not None else -1
            log(LogDiffer.log_line_from_info(info))

        self._execute(op, addr, mode)

    def _prepare(self):
        c = self.next_mem_value()
        op, mode = self.opcodes[c]
        addr = self.address(mode)
        return op, addr, mode

    def _value_from_address(self, addr: Optional[int], mode: str):
        if mode in ('IMM', 'IMP'):
            # 立即寻址 和 隐含寻址 情况
            return addr
        else:
            return self.mem_value(addr)

    def _execute(self, op: str, addr: Optional[int], mode: str):
        if op == 'JMP':
            self.set_reg_value('pc', addr)
        elif op == 'LDX':
            v = self._value_from_address(addr, mode)
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
            v = self._value_from_address(addr, mode)
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
            v = self._value_from_address(addr, mode)
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
            v = number_from_bytes([vl, vh])
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
            v = self._value_from_address(addr, mode)
            r = self.reg_value('a')
            v = r & v
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'CMP':
            v = self._value_from_address(addr, mode)
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
                m = self.p_masks[b]
                f = v & m != 0
                self.set_flag(b, f)
        elif op == 'BMI':
            f = self.flag('n')
            if f:
                self.set_reg_value('pc', addr)
        elif op == 'ORA':
            v = self._value_from_address(addr, mode)
            r = self.reg_value('a')
            v = r | v
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'CLV':
            self.set_flag('v', False)
        elif op == 'EOR':
            v = self._value_from_address(addr, mode)
            r = self.reg_value('a')
            v = r ^ v
            self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'ADC':
            mvalue = self._value_from_address(addr, mode)
            v = mvalue
            r = self.reg_value('a')
            c = int(self.flag('c'))
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
            v = number_from_bytes([mvalue], signed=True)
            r = number_from_bytes([r], signed=True)
            v = r + v + c
            self.set_flag('v', v > 128 or v < -127)
        elif op == 'LDY':
            v = self._value_from_address(addr, mode)
            self.set_reg_value('y', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'CPY':
            v = self._value_from_address(addr, mode)
            r = self.reg_value('y')
            v = r - v
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            self.set_flag('c', v >= 0)
        elif op == 'CPX':
            v = self._value_from_address(addr, mode)
            r = self.reg_value('x')
            v = r - v
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            self.set_flag('c', v >= 0)
        elif op == 'SBC':
            mvalue = self._value_from_address(addr, mode)
            v = mvalue
            r = self.reg_value('a')
            c = int(self.flag('c'))
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
            v = number_from_bytes([mvalue], signed=True)
            r = number_from_bytes([r], signed=True)
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
                m = self.p_masks[b]
                f = v & m != 0
                self.set_flag(b, f)
            vl = self.pop()
            vh = self.pop()
            v = number_from_bytes([vl, vh])
            # 这里不需要像 RTS 一样 +1
            pc = v
            self.set_reg_value('pc', pc)
        elif op == 'LSR':
            if addr is not None:
                old_v = self._value_from_address(addr, mode)
                v = old_v >> 1
                self.set_mem_value(addr, v)
            else:
                old_v = self.reg_value('a')
                v = old_v >> 1
                self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            self.set_flag('c', old_v & 0b00000001 != 0)
        elif op == 'ASL':
            if addr is not None:
                old_v = self._value_from_address(addr, mode)
                v = old_v << 1
                v %= 256
                self.set_mem_value(addr, v)
            else:
                old_v = self.reg_value('a')
                v = old_v << 1
                v %= 256
                self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            self.set_flag('c', old_v & 0b10000000 != 0)
        elif op == 'ROR':
            c = int(self.flag('c'))
            if addr is not None:
                old_v = self._value_from_address(addr, mode)
                v = (old_v >> 1) + (c * 128)
                self.set_mem_value(addr, v)
            else:
                old_v = self.reg_value('a')
                v = (old_v >> 1) + (c * 128)
                self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            self.set_flag('c', old_v & 0b00000001 != 0)
        elif op == 'ROL':
            c = int(self.flag('c'))
            if addr is not None:
                old_v = self._value_from_address(addr, mode)
                v = (old_v << 1) + c
                v %= 256
                self.set_mem_value(addr, v)
            else:
                old_v = self.reg_value('a')
                v = (old_v << 1) + c
                v %= 256
                self.set_reg_value('a', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
            self.set_flag('c', old_v & 0b10000000 != 0)
        elif op == 'STY':
            v = self.reg_value('y')
            self.set_mem_value(addr, v)
        elif op == 'INC':
            v = self._value_from_address(addr, mode)
            v += 1
            v %= 256
            self.set_mem_value(addr, v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'DEC':
            v = self._value_from_address(addr, mode)
            v -= 1
            v %= 256
            self.set_mem_value(addr, v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'LAX':
            v = self._value_from_address(addr, mode)
            self.set_reg_value('a', v)
            self.set_reg_value('x', v)
            self.set_flag('n', v & 0b10000000 != 0)
            self.set_flag('z', v == 0)
        elif op == 'SAX':
            v1 = self.reg_value('a')
            v2 = self.reg_value('x')
            v = v1 & v2
            self.set_mem_value(addr, v)
        elif op == 'DCP':
            self._execute('DEC', addr, mode)
            self._execute('CMP', addr, mode)
        elif op == 'ISB':
            self._execute('ISC', addr, mode)
        elif op == 'ISC':
            self._execute('INC', addr, mode)
            self._execute('SBC', addr, mode)
        elif op == 'SLO':
            self._execute('ASL', addr, mode)
            self._execute('ORA', addr, mode)
        elif op == 'RLA':
            self._execute('ROL', addr, mode)
            self._execute('AND', addr, mode)
        elif op == 'SRE':
            self._execute('LSR', addr, mode)
            self._execute('EOR', addr, mode)
        elif op == 'RRA':
            self._execute('ROR', addr, mode)
            self._execute('ADC', addr, mode)
        elif op == 'BRK':
            # pc 压栈
            # 这里不需要 pc - 1
            pc = self.reg_value('pc')
            v = pc
            self.push((v & 0xff00) >> 8)
            self.push(v & 0x00ff)

            # p 压栈
            # 在这条指令中，只有「被压入栈」的 P 的 B flag 被置为 True
            bv = self.reg_value('p')
            self.set_flag('b', True)
            v = self.reg_value('p')
            self.push(v)
            self.set_reg_value('p', bv)

            # 设置中断跳转
            vl = self.mem_value(0xfffe)
            vh = self.mem_value(0xffff)
            v = number_from_bytes([vl, vh])
            self.set_reg_value('pc', v)

            self.set_flag('i', True)
            self.set_flag('b', True)
        else:
            raise ValueError('错误的 op： <{}>'.format(op))

    def interrupt(self, name: str):
        name = name.upper()

        if name == 'NMI':
            if not self.ppu.can_nmi():
                return
            else:
                self.ppu.set_can_nmi(False)
            al_pos = 0xfffa
        elif name == 'RESET':
            al_pos = 0xfffc
            # TODO: 完成 reset 的其他处理
        else:
            raise ValueError('错误的 interrupt： <{}>'.format(name))

        # 将 pc 和 p 压栈
        pc = self.reg_value('pc')
        v = pc
        self.push((v & 0xff00) >> 8)
        self.push(v & 0x00ff)
        # 只有「被压入栈」的 P 的 B flag 被置为 True
        bv = self.reg_value('p')
        self.set_flag('b', True)
        v = self.reg_value('p')
        self.push(v)
        self.set_reg_value('p', bv)

        al = self.mem_value(al_pos)
        ah = self.mem_value(al_pos + 1)
        addr = utils.number_from_bytes([al, ah])
        self.set_reg_value('pc', addr)
