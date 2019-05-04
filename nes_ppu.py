# -*- coding: utf-8 -*-
from typing import Dict, List, Tuple

import pygame as pygame

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
        self.colors: List[Tuple[int, int, int, int]] = None

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

        self.colors = [
            (0x7F, 0x7F, 0x7F, 0xFF), (0x20, 0x00, 0xB0, 0xFF), (0x28, 0x00, 0xB8, 0xFF), (0x60, 0x10, 0xA0, 0xFF),
            (0x98, 0x20, 0x78, 0xFF), (0xB0, 0x10, 0x30, 0xFF), (0xA0, 0x30, 0x00, 0xFF), (0x78, 0x40, 0x00, 0xFF),
            (0x48, 0x58, 0x00, 0xFF), (0x38, 0x68, 0x00, 0xFF), (0x38, 0x6C, 0x00, 0xFF), (0x30, 0x60, 0x40, 0xFF),
            (0x30, 0x50, 0x80, 0xFF), (0x00, 0x00, 0x00, 0xFF), (0x00, 0x00, 0x00, 0xFF), (0x00, 0x00, 0x00, 0xFF),

            (0xBC, 0xBC, 0xBC, 0xFF), (0x40, 0x60, 0xF8, 0xFF), (0x40, 0x40, 0xFF, 0xFF), (0x90, 0x40, 0xF0, 0xFF),
            (0xD8, 0x40, 0xC0, 0xFF), (0xD8, 0x40, 0x60, 0xFF), (0xE0, 0x50, 0x00, 0xFF), (0xC0, 0x70, 0x00, 0xFF),
            (0x88, 0x88, 0x00, 0xFF), (0x50, 0xA0, 0x00, 0xFF), (0x48, 0xA8, 0x10, 0xFF), (0x48, 0xA0, 0x68, 0xFF),
            (0x40, 0x90, 0xC0, 0xFF), (0x00, 0x00, 0x00, 0xFF), (0x00, 0x00, 0x00, 0xFF), (0x00, 0x00, 0x00, 0xFF),

            (0xFF, 0xFF, 0xFF, 0xFF), (0x60, 0xA0, 0xFF, 0xFF), (0x50, 0x80, 0xFF, 0xFF), (0xA0, 0x70, 0xFF, 0xFF),
            (0xF0, 0x60, 0xFF, 0xFF), (0xFF, 0x60, 0xB0, 0xFF), (0xFF, 0x78, 0x30, 0xFF), (0xFF, 0xA0, 0x00, 0xFF),
            (0xE8, 0xD0, 0x20, 0xFF), (0x98, 0xE8, 0x00, 0xFF), (0x70, 0xF0, 0x40, 0xFF), (0x70, 0xE0, 0x90, 0xFF),
            (0x60, 0xD0, 0xE0, 0xFF), (0x60, 0x60, 0x60, 0xFF), (0x00, 0x00, 0x00, 0xFF), (0x00, 0x00, 0x00, 0xFF),

            (0xFF, 0xFF, 0xFF, 0xFF), (0x90, 0xD0, 0xFF, 0xFF), (0xA0, 0xB8, 0xFF, 0xFF), (0xC0, 0xB0, 0xFF, 0xFF),
            (0xE0, 0xB0, 0xFF, 0xFF), (0xFF, 0xB8, 0xE8, 0xFF), (0xFF, 0xC8, 0xB8, 0xFF), (0xFF, 0xD8, 0xA0, 0xFF),
            (0xFF, 0xF0, 0x90, 0xFF), (0xC8, 0xF0, 0x80, 0xFF), (0xA0, 0xF0, 0xA0, 0xFF), (0xA0, 0xFF, 0xC8, 0xFF),
            (0xA0, 0xFF, 0xF0, 0xFF), (0xA0, 0xA0, 0xA0, 0xFF), (0x00, 0x00, 0x00, 0xFF), (0x00, 0x00, 0x00, 0xFF),
        ]

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

    def color_from_xy(self, x: int, y: int):
        # 获取所在名称
        begin_of_name_table = 0x2000
        name_per_line = 32
        size_of_name = 8
        name_id = (x // size_of_name) + (y // size_of_name) * name_per_line
        pattern_id = self.mem_value(begin_of_name_table + name_id)
        # 查找对应图样表
        begin_of_pattern_table = 0
        width_of_pattern = 16
        height_of_pattern = 16
        bytes_per_pattern = width_of_pattern
        begin_of_p0 = begin_of_pattern_table + pattern_id * bytes_per_pattern
        begin_of_p1 = begin_of_p0 + bytes_per_pattern // 2
        # Y 坐标为平面内偏移
        offset = y % (height_of_pattern // 2)
        p0 = self.mem_value(begin_of_p0 + offset)
        p1 = self.mem_value(begin_of_p1 + offset)
        # X 坐标为字节内偏移
        shift = x % 8
        mask = 0x100 >> shift
        # 计算低二位
        low = (0b00000001 if (p0 & mask) != 0 else 0) | (0b00000010 if (p1 & mask) != 0 else 0)
        # 计算所在属性表
        aid = (x >> 5) + (y >> 5) * 8
        attr = self.mem_value(begin_of_name_table + aid + (32 * 30))
        # 获取属性表内位偏移
        aoffset = ((x & 0x10) >> 3) | ((y & 0x10) >> 2)
        # 计算高两位
        high = (attr & (3 << aoffset)) >> aoffset << 2
        # 合并作为调色盘索引
        index_of_palette = high | low
        # 从调色盘获取颜色编号
        begin_of_palette = 0x3f00
        index_of_color = self.mem_value(begin_of_palette + index_of_palette)
        return self.colors[index_of_color]

    def draw(self, canvas: pygame.Surface):
        width, height = canvas.get_width(), canvas.get_height()

        for y in range(height):
            for x in range(width):
                pos = x, y
                color = self.color_from_xy(x, y)
                canvas.set_at(pos, color)
