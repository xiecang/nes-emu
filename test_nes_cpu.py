# -*- coding: utf-8 -*-

import nes_cpu as nc


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
