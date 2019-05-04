# -*- coding: utf-8 -*-
import nes_file as nf


def prepared_nes():
    return nf.NesFile.load('misc/nestest.nes')


def test_load1():
    nes = prepared_nes()
    excepted = 'NES'
    result = nes.format
    assert excepted == result, result


def test_load2():
    nes = prepared_nes()
    excepted = 16384 * nes.size_of_prg_rom_unit
    result = len(nes.prg_rom)
    assert excepted == result, result


def test_load3():
    nes = prepared_nes()
    expected = 8192 * nes.size_of_chr_rom_unit
    result = len(nes.chr_rom)
    assert expected == result, result


def test_bytes_to_int_list():
    test_cases = [
        (b'', []),
        (b'\x00', [0]),
        (b'\x00\x01', [0, 1]),
        (b'\xff', [255]),
    ]
    for case in test_cases:
        result = list(case[0])
        expected = case[1]
        assert expected == result, (case, result)


def test():
    test_load1()
    test_load2()
    test_load3()
    test_bytes_to_int_list()


if __name__ == '__main__':
    test()
