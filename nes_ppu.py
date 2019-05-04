# -*- coding: utf-8 -*-
from typing import Dict, List
import nes_file as nf


class NesPPU(object):
    def __init__(self):
        self.registers: Dict[str, int] = None
        self.memory: List[int] = None
        # 用于判断 PPUSCROLL、PPUADDR 的寄存是该写「高位」还是「低位」
        self.reg_flag: Dict[str, bool] = None
        # 将 cpu 读写的 port 映射到 ppu 寄存器上
        self.reg_mapper_for_cpu: Dict[int, str] = None
        self.buffer = 0

        self.setup()

    def setup(self):
        self.registers = {
            'PPUCTRL': 0,
            'PPUMASK': 0,
            'PPUSTATUS': 0b10100000,
            'OAMADDR': 0,
            'OAMDATA': 0,
            'PPUSCROLL': 0,
            'PPUADDR': 0,
            'PPUDATA': 0,
            'OAMDMA': 0,
        }
        self.reg_mapper_for_cpu = {
            0x2000: 'PPUCTRL',
            0x2001: 'PPUMASK',
            0x2002: 'PPUSTATUS',
            0x2003: 'OAMADDR',
            0x2004: 'OAMDATA',
            0x2005: 'PPUSCROLL',
            0x2006: 'PPUADDR',
            0x2007: 'PPUDATA',
            0x4014: 'OAMDMA',
        }
        self.memory = [0] * 0x4000
        self.reg_flag = {
            'PPUSCROLL': True,
            'PPUADDR': True,
        }

    def load_nes(self, nes: nf.NesFile):
        self.memory[:0x2000] = nes.chr_rom

    def reg_value(self, name: str):
        n = name.upper()
        return self.registers[n]

    def set_reg_value(self, name: str, value: int):
        n = name.upper()

        if n not in self.registers:
            raise ValueError('未知的寄存器：<{}>'.format(n))
        if n in ('PPUADDR', 'PPUSCROLL'):
            if value < 0 or value > 2 ** 16 - 1:
                raise ValueError('<{}>超过了<{}>寄存器的取值范围'.format(value, n))
        else:
            if value < 0 or value > 2 ** 8 - 1:
                raise ValueError('<{}>超过了<{}>寄存器的取值范围'.format(value, n))

        self.registers[n] = value

    def mem_value(self, addr: int):
        # 镜像
        if 0x3000 <= addr <= 0x3eff:
            addr -= 0x1000
        elif 0x3f20 <= addr <= 0x3fff:
            addr -= 0x0020
        elif addr in (0x3F10, 0x3F14, 0x3F18, 0x3F1C):
            addr -= 0x0010

        return self.memory[addr]

    def set_mem_value(self, addr: int, value: int):
        # 镜像
        if 0x3000 <= addr <= 0x3eff:
            addr -= 0x1000
        elif 0x3f20 <= addr <= 0x3fff:
            addr -= 0x0020
        elif addr in (0x3F10, 0x3F14, 0x3F18, 0x3F1C):
            addr -= 0x0010

        self.memory[addr] = value

    def reg_value_for_cpu(self, addr: int):
        name = self.reg_mapper_for_cpu[addr]
        # if name not in ('PPUSTATUS', 'OAMDATA', 'PPUDATA'):
        #     raise ValueError('CPU 不能读取<{}>寄存器'.format(name))

        if name == 'PPUDATA':
            a = self.reg_value('ppuaddr')

            if 0x3F00 <= a <= 0x3FFF:
                v = self.mem_value(a)
                self.buffer = v
            else:
                # NOTE: 这里是直接返回「当前」缓冲区的值，然后再更新缓冲区
                v = self.buffer
                self.buffer = self.mem_value(a)

            self.set_reg_value('ppuaddr', a + 1)
            return v
        else:
            return self.reg_value(name)

    def set_reg_value_for_cpu(self, addr: int, value: int):
        name = self.reg_mapper_for_cpu[addr]
        # if name not in ('PPUCTRL', 'PPUMASK', 'OAMADDR', 'OAMDATA', 'PPUSCROLL', 'PPUADDR', 'PPUDATA', 'OAMDMA'):
        #     raise ValueError('CPU 不能写入<{}>寄存器'.format(name))

        if name == 'PPUDATA':
            a = self.reg_value('ppuaddr')
            self.set_mem_value(a, value)
            self.set_reg_value('ppuaddr', a + 1)
        elif name in self.reg_flag:
            old_v = self.reg_value(name)
            f = self.reg_flag[name]
            self.reg_flag[name] = not f
            if f:
                self.set_reg_value(name, (old_v & 0x00ff) | (value << 8))
            else:
                self.set_reg_value(name, (old_v & 0xff00) | value)
        else:
            self.set_reg_value(name, value)
