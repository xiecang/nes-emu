# -*- coding: utf-8 -*-

import nes_cpu as nc
import test_nes_file as nft
import log_differ as ld
from utils import number_from_bytes


def test_register():
    cpu = nc.NesCPU()
    test_cases = [
        ('PC', 'PC', 256),
        ('PC', 'pc', 256),
        ('pc', 'pc', 256),
        ('p', 'p', 1),
        ('a', 'a', 2),
        ('x', 'x', 3),
        ('y', 'y', 4),
        ('s', 's', 4),
    ]
    for case in test_cases:
        sname = case[0]
        gname = case[1]
        value = case[2]

        cpu.set_reg_value(sname, value)
        result = cpu.reg_value(gname)
        expected = value

        assert expected == result, (case, result)


def test_load_nes():
    nes = nft.prepared_nes()
    cpu = nc.NesCPU()
    cpu.load_nes(nes)

    expected = nes.prg_rom
    result = cpu.prg_rom
    assert expected == result, result


def address_for_log_info(addr):
    if addr is None:
        return -1
    else:
        return addr


def test_by_log_differ():
    differ = ld.LogDiffer.from_json('misc/nestest_log.json')
    nes = nft.prepared_nes()
    cpu = nc.NesCPU()
    cpu.load_nes(nes)
    # nestest.nes 所需的特殊初始化
    cpu.set_reg_value('pc', 0xc000)
    cpu.set_reg_value('p', 0x24)

    while True:
        info = dict(
            PC=cpu.reg_value('PC'),
            A=cpu.reg_value('A'),
            X=cpu.reg_value('X'),
            Y=cpu.reg_value('Y'),
            P=cpu.reg_value('P'),
            S=cpu.reg_value('S'),
        )

        op, addr, mode = cpu._prepare()

        info['op'] = op
        info['address'] = address_for_log_info(addr)

        try:
            differ.diff(info)
        except ld.AllTestsPassed:
            break

        cpu._execute(op, addr, mode)


def test_flag1():
    cpu = nc.NesCPU()
    cpu.set_reg_value('p', 0)
    test_cases = [
        ('N', False),
        ('V', False),
        ('D', False),
        ('I', False),
        ('Z', False),
        ('C', False),
    ]
    for case in test_cases:
        b = case[0]
        expected = case[1]
        result = cpu.flag(b)
        assert expected == result, (case, result)


def test_flag2():
    cpu = nc.NesCPU()
    cpu.set_reg_value('p', 0b10001010)
    test_cases = [
        ('N', True),
        ('V', False),
        ('D', True),
        ('I', False),
        ('Z', True),
        ('C', False),
    ]
    for case in test_cases:
        b = case[0]
        expected = case[1]
        result = cpu.flag(b)
        assert expected == result, (case, result)


def test_set_flag():
    cpu = nc.NesCPU()
    cpu.set_reg_value('p', 0)

    cpu.set_flag('N', True)
    expected = True
    result = cpu.flag('N')
    assert expected == result, result

    cpu.set_flag('N', False)
    expected = False
    result = cpu.flag('N')
    assert expected == result, result


def test_push_pop1():
    cpu = nc.NesCPU()
    cpu.push(1)
    expected = 1
    result = cpu.pop()
    assert expected == result, result


def test_push_pop2():
    cpu = nc.NesCPU()
    cpu.push(1)
    cpu.push(2)
    cpu.push(3)
    cpu.push(4)
    expected = [4, 3, 2, 1]
    result = [cpu.pop() for _ in range(4)]
    assert expected == result, result


def test_push():
    """ addr = s + 0x0100 """
    cpu = nc.NesCPU()
    s = cpu.reg_value('s')
    cpu.push(1)

    expected = 1
    addr = s + 0x0100
    result = cpu.mem_value(addr)
    assert expected == result, result


def test_ppu():
    nes = nft.prepared_nes()
    cpu = nc.NesCPU()
    cpu.load_nes(nes)

    rl = cpu.mem_value(0xfffc)
    rh = cpu.mem_value(0xfffd)
    reset = number_from_bytes([rl, rh])
    cpu.set_reg_value('pc', reset)

    for _ in range(20000):
        cpu.execute()

    expected = [
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 45, 45, 32, 82, 117, 110, 32, 97, 108, 108, 32, 116, 101, 115, 116, 115, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45, 32, 66, 114, 97, 110, 99, 104, 32, 116, 101, 115, 116, 115,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45, 32, 70, 108, 97, 103, 32, 116,
        101, 115, 116, 115, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45, 32,
        73, 109, 109, 101, 100, 105, 97, 116, 101, 32, 116, 101, 115, 116, 115, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 45, 45, 32, 73, 109, 112, 108, 105, 101, 100, 32, 116, 101, 115, 116, 115, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45, 32, 83, 116, 97, 99, 107, 32, 116, 101, 115,
        116, 115, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45, 32, 65, 99, 99,
        117, 109, 117, 108, 97, 116, 111, 114, 32, 116, 101, 115, 116, 115, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 45, 45, 32, 40, 73, 110, 100, 105, 114, 101, 99, 116, 44, 88, 41, 32, 116, 101, 115, 116, 115, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45, 32, 90, 101, 114, 111, 112, 97, 103, 101, 32, 116, 101, 115,
        116, 115, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45, 32, 65, 98, 115, 111, 108, 117,
        116, 101, 32, 116, 101, 115, 116, 115, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45,
        32, 40, 73, 110, 100, 105, 114, 101, 99, 116, 41, 44, 89, 32, 116, 101, 115, 116, 115, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 45, 45, 32, 65, 98, 115, 111, 108, 117, 116, 101, 44, 89, 32, 116, 101, 115, 116,
        115, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45, 32, 90, 101, 114, 111, 112, 97, 103, 101,
        44, 88, 32, 116, 101, 115, 116, 115, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 45, 32, 65,
        98, 115, 111, 108, 117, 116, 101, 44, 88, 32, 116, 101, 115, 116, 115, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 85, 112, 47, 68, 111, 119, 110, 58, 32, 115, 101,
        108, 101, 99, 116, 32, 116, 101, 115, 116, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 83, 116,
        97, 114, 116, 58, 32, 114, 117, 110, 32, 116, 101, 115, 116, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 83, 101, 108, 101, 99, 116, 58, 32, 73, 110, 118, 97, 108, 105, 100, 32, 111, 112, 115, 33,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32,
        32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    ]
    result = cpu.ppu.memory[0x2000:0x2400]
    assert expected == result, result
