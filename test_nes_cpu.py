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
        return 0
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


if __name__ == '__main__':
    test_by_log_differ()
