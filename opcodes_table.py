# -*- coding: utf-8 -*-
opcodes = {
    0x00: ('BRK', 'IMP'),
    0x01: ('ORA', 'INX'),
    0x02: ('KIL', 'IMP'),
    0x03: ('SLO', 'INX'),
    0x04: ('NOP', 'ZPG'),
    0x05: ('ORA', 'ZPG'),
    0x06: ('ASL', 'ZPG'),
    0x07: ('SLO', 'ZPG'),
    0x08: ('PHP', 'IMP'),
    0x09: ('ORA', 'IMM'),
    0x0A: ('ASL', 'IMP'),
    0x0B: ('ANC', 'IMM'),
    0x0C: ('NOP', 'ABS'),
    0x0D: ('ORA', 'ABS'),
    0x0E: ('ASL', 'ABS'),
    0x0F: ('SLO', 'ABS'),
    0x10: ('BPL', 'REL'),
    0x11: ('ORA', 'INY'),
    0x12: ('KIL', 'IMP'),
    0x13: ('SLO', 'INY'),
    0x14: ('NOP', 'ZPX'),
    0x15: ('ORA', 'ZPX'),
    0x16: ('ASL', 'ZPX'),
    0x17: ('SLO', 'ZPX'),
    0x18: ('CLC', 'IMP'),
    0x19: ('ORA', 'ABY'),
    0x1A: ('NOP', 'IMP'),
    0x1B: ('SLO', 'ABY'),
    0x1C: ('NOP', 'ABX'),
    0x1D: ('ORA', 'ABX'),
    0x1E: ('ASL', 'ABX'),
    0x1F: ('SLO', 'ABX'),
    0x20: ('JSR', 'ABS'),
    0x21: ('AND', 'INX'),
    0x22: ('KIL', 'IMP'),
    0x23: ('RLA', 'INX'),
    0x24: ('BIT', 'ZPG'),
    0x25: ('AND', 'ZPG'),
    0x26: ('ROL', 'ZPG'),
    0x27: ('RLA', 'ZPG'),
    0x28: ('PLP', 'IMP'),
    0x29: ('AND', 'IMM'),
    0x2A: ('ROL', 'IMP'),
    0x2B: ('ANC', 'IMM'),
    0x2C: ('BIT', 'ABS'),
    0x2D: ('AND', 'ABS'),
    0x2E: ('ROL', 'ABS'),
    0x2F: ('RLA', 'ABS'),
    0x30: ('BMI', 'REL'),
    0x31: ('AND', 'INY'),
    0x32: ('KIL', 'IMP'),
    0x33: ('RLA', 'INY'),
    0x34: ('NOP', 'ZPX'),
    0x35: ('AND', 'ZPX'),
    0x36: ('ROL', 'ZPX'),
    0x37: ('RLA', 'ZPX'),
    0x38: ('SEC', 'IMP'),
    0x39: ('AND', 'ABY'),
    0x3A: ('NOP', 'IMP'),
    0x3B: ('RLA', 'ABY'),
    0x3C: ('NOP', 'ABX'),
    0x3D: ('AND', 'ABX'),
    0x3E: ('ROL', 'ABX'),
    0x3F: ('RLA', 'ABX'),
    0x40: ('RTI', 'IMP'),
    0x41: ('EOR', 'INX'),
    0x42: ('KIL', 'IMP'),
    0x43: ('SRE', 'INX'),
    0x44: ('NOP', 'ZPG'),
    0x45: ('EOR', 'ZPG'),
    0x46: ('LSR', 'ZPG'),
    0x47: ('SRE', 'ZPG'),
    0x48: ('PHA', 'IMP'),
    0x49: ('EOR', 'IMM'),
    0x4A: ('LSR', 'IMP'),
    0x4B: ('ASR', 'IMM'),
    0x4C: ('JMP', 'ABS'),
    0x4D: ('EOR', 'ABS'),
    0x4E: ('LSR', 'ABS'),
    0x4F: ('SRE', 'ABS'),
    0x50: ('BVC', 'REL'),
    0x51: ('EOR', 'INY'),
    0x52: ('KIL', 'IMP'),
    0x53: ('SRE', 'INY'),
    0x54: ('NOP', 'ZPX'),
    0x55: ('EOR', 'ZPX'),
    0x56: ('LSR', 'ZPX'),
    0x57: ('SRE', 'ZPX'),
    0x58: ('CLI', 'IMP'),
    0x59: ('EOR', 'ABY'),
    0x5A: ('NOP', 'IMP'),
    0x5B: ('SRE', 'ABY'),
    0x5C: ('NOP', 'ABX'),
    0x5D: ('EOR', 'ABX'),
    0x5E: ('LSR', 'ABX'),
    0x5F: ('SRE', 'ABX'),
    0x60: ('RTS', 'IMP'),
    0x61: ('ADC', 'INX'),
    0x62: ('KIL', 'IMP'),
    0x63: ('RRA', 'INX'),
    0x64: ('NOP', 'ZPG'),
    0x65: ('ADC', 'ZPG'),
    0x66: ('ROR', 'ZPG'),
    0x67: ('RRA', 'ZPG'),
    0x68: ('PLA', 'IMP'),
    0x69: ('ADC', 'IMM'),
    0x6A: ('ROR', 'IMP'),
    0x6B: ('ARR', 'IMM'),
    0x6C: ('JMP', 'IND'),
    0x6D: ('ADC', 'ABS'),
    0x6E: ('ROR', 'ABS'),
    0x6F: ('RRA', 'ABS'),
    0x70: ('BVS', 'REL'),
    0x71: ('ADC', 'INY'),
    0x72: ('KIL', 'IMP'),
    0x73: ('RRA', 'INY'),
    0x74: ('NOP', 'ZPX'),
    0x75: ('ADC', 'ZPX'),
    0x76: ('ROR', 'ZPX'),
    0x77: ('RRA', 'ZPX'),
    0x78: ('SEI', 'IMP'),
    0x79: ('ADC', 'ABY'),
    0x7A: ('NOP', 'IMP'),
    0x7B: ('RRA', 'ABY'),
    0x7C: ('NOP', 'ABX'),
    0x7D: ('ADC', 'ABX'),
    0x7E: ('ROR', 'ABX'),
    0x7F: ('RRA', 'ABX'),
    0x80: ('NOP', 'IMM'),
    0x81: ('STA', 'INX'),
    0x82: ('NOP', 'IMM'),
    0x83: ('SAX', 'INX'),
    0x84: ('STY', 'ZPG'),
    0x85: ('STA', 'ZPG'),
    0x86: ('STX', 'ZPG'),
    0x87: ('SAX', 'ZPG'),
    0x88: ('DEY', 'IMP'),
    0x89: ('NOP', 'IMM'),
    0x8A: ('TXA', 'IMP'),
    0x8B: ('XAA', 'IMM'),
    0x8C: ('STY', 'ABS'),
    0x8D: ('STA', 'ABS'),
    0x8E: ('STX', 'ABS'),
    0x8F: ('SAX', 'ABS'),
    0x90: ('BCC', 'REL'),
    0x91: ('STA', 'INY'),
    0x92: ('KIL', 'IMP'),
    0x93: ('AHX', 'INY'),
    0x94: ('STY', 'ZPX'),
    0x95: ('STA', 'ZPX'),
    0x96: ('STX', 'ZPY'),
    0x97: ('SAX', 'ZPY'),
    0x98: ('TYA', 'IMP'),
    0x99: ('STA', 'ABY'),
    0x9A: ('TXS', 'IMP'),
    0x9B: ('TAS', 'ABY'),
    0x9C: ('SHY', 'ABX'),
    0x9D: ('STA', 'ABX'),
    0x9E: ('SHX', 'ABY'),
    0x9F: ('AHX', 'ABY'),
    0xA0: ('LDY', 'IMM'),
    0xA1: ('LDA', 'INX'),
    0xA2: ('LDX', 'IMM'),
    0xA3: ('LAX', 'INX'),
    0xA4: ('LDY', 'ZPG'),
    0xA5: ('LDA', 'ZPG'),
    0xA6: ('LDX', 'ZPG'),
    0xA7: ('LAX', 'ZPG'),
    0xA8: ('TAY', 'IMP'),
    0xA9: ('LDA', 'IMM'),
    0xAA: ('TAX', 'IMP'),
    0xAB: ('LAX', 'IMM'),
    0xAC: ('LDY', 'ABS'),
    0xAD: ('LDA', 'ABS'),
    0xAE: ('LDX', 'ABS'),
    0xAF: ('LAX', 'ABS'),
    0xB0: ('BCS', 'REL'),
    0xB1: ('LDA', 'INY'),
    0xB2: ('KIL', 'IMP'),
    0xB3: ('LAX', 'INY'),
    0xB4: ('LDY', 'ZPX'),
    0xB5: ('LDA', 'ZPX'),
    0xB6: ('LDX', 'ZPY'),
    0xB7: ('LAX', 'ZPY'),
    0xB8: ('CLV', 'IMP'),
    0xB9: ('LDA', 'ABY'),
    0xBA: ('TSX', 'IMP'),
    0xBB: ('LAS', 'ABY'),
    0xBC: ('LDY', 'ABX'),
    0xBD: ('LDA', 'ABX'),
    0xBE: ('LDX', 'ABY'),
    0xBF: ('LAX', 'ABY'),
    0xC0: ('CPY', 'IMM'),
    0xC1: ('CMP', 'INX'),
    0xC2: ('NOP', 'IMM'),
    0xC3: ('DCP', 'INX'),
    0xC4: ('CPY', 'ZPG'),
    0xC5: ('CMP', 'ZPG'),
    0xC6: ('DEC', 'ZPG'),
    0xC7: ('DCP', 'ZPG'),
    0xC8: ('INY', 'IMP'),
    0xC9: ('CMP', 'IMM'),
    0xCA: ('DEX', 'IMP'),
    0xCB: ('AXS', 'IMM'),
    0xCC: ('CPY', 'ABS'),
    0xCD: ('CMP', 'ABS'),
    0xCE: ('DEC', 'ABS'),
    0xCF: ('DCP', 'ABS'),
    0xD0: ('BNE', 'REL'),
    0xD1: ('CMP', 'INY'),
    0xD2: ('KIL', 'IMP'),
    0xD3: ('DCP', 'INY'),
    0xD4: ('NOP', 'ZPX'),
    0xD5: ('CMP', 'ZPX'),
    0xD6: ('DEC', 'ZPX'),
    0xD7: ('DCP', 'ZPX'),
    0xD8: ('CLD', 'IMP'),
    0xD9: ('CMP', 'ABY'),
    0xDA: ('NOP', 'IMP'),
    0xDB: ('DCP', 'ABY'),
    0xDC: ('NOP', 'ABX'),
    0xDD: ('CMP', 'ABX'),
    0xDE: ('DEC', 'ABX'),
    0xDF: ('DCP', 'ABX'),
    0xE0: ('CPX', 'IMM'),
    0xE1: ('SBC', 'INX'),
    0xE2: ('NOP', 'IMM'),
    0xE3: ('ISB', 'INX'),
    0xE4: ('CPX', 'ZPG'),
    0xE5: ('SBC', 'ZPG'),
    0xE6: ('INC', 'ZPG'),
    0xE7: ('ISB', 'ZPG'),
    0xE8: ('INX', 'IMP'),
    0xE9: ('SBC', 'IMM'),
    0xEA: ('NOP', 'IMP'),
    0xEB: ('SBC', 'IMM'),
    0xEC: ('CPX', 'ABS'),
    0xED: ('SBC', 'ABS'),
    0xEE: ('INC', 'ABS'),
    0xEF: ('ISB', 'ABS'),
    0xF0: ('BEQ', 'REL'),
    0xF1: ('SBC', 'INY'),
    0xF2: ('KIL', 'IMP'),
    0xF3: ('ISB', 'INY'),
    0xF4: ('NOP', 'ZPX'),
    0xF5: ('SBC', 'ZPX'),
    0xF6: ('INC', 'ZPX'),
    0xF7: ('ISB', 'ZPX'),
    0xF8: ('SED', 'IMP'),
    0xF9: ('SBC', 'ABY'),
    0xFA: ('NOP', 'IMP'),
    0xFB: ('ISB', 'ABY'),
    0xFC: ('NOP', 'ABX'),
    0xFD: ('SBC', 'ABX'),
    0xFE: ('INC', 'ABX'),
    0xFF: ('ISB', 'ABX'),
}
