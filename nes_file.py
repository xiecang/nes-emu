# -*- coding: utf-8 -*-


class NesFile(object):
    def __init__(self, data: bytes):
        self.format = None
        self.size_of_prg_rom_unit = None
        self.size_of_prg_chr_unit = None
        self.prg_rom = None
        self.chr_rom = None

        self._setup(data)

    def _setup(self, data: bytes):
        self.format: str = data[0: 3].decode('ascii')
        self.size_of_prg_rom_unit: int = data[4]
        self.size_of_chr_rom_unit: int = data[5]
        prom_len = self.size_of_prg_rom_unit * 16384
        self.prg_rom = list(data[16:16 + prom_len])
        crom_len = self.size_of_chr_rom_unit * 8192
        self.chr_rom = list(data[16 + prom_len:16 + prom_len + crom_len])

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            data = f.read()
            return cls(data)
