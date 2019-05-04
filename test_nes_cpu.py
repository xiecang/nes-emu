# -*- coding: utf-8 -*-

import nes_cpu as nc
import test_nes_file as nft
import log_differ as ld


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
    nes = nft.prepare_nes()
    cpu = nc.NesCPU()
    cpu.load_nes(nes)

    expected = nes.prg_rom
    result = cpu._memory[0x8000:0xc000]
    assert expected == result, result

    expected = nes.prg_rom
    result = cpu._memory[0xc000:]
    assert expected == result, result


def address_for_log_info(addr):
    if addr is None:
        return -1
    else:
        return addr


def test_by_log_differ():
    differ = ld.LogDiffer.from_json('misc/nestest_log.json')
    nes = nft.prepare_nes()
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

        op, addr, imm = cpu._prepare()

        info['op'] = op
        info['address'] = address_for_log_info(addr)

        differ.diff(info)

        cpu._execute(op, addr, imm)


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
    cpu.set_reg_value('s', 16)
    s = cpu.reg_value('s')
    cpu.push(1)

    expected = 1
    addr = s + 0x0100
    result = cpu.mem_value(addr)
    assert expected == result, result


if __name__ == '__main__':
    test_by_log_differ()
