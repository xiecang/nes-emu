# -*- coding: utf-8 -*-


class NesCPU(object):
    def __init__(self):
        self._reg_values = None
        self._memory = None

        self._setup()

    def _setup(self):
        # at power-up
        self._reg_values = {
            'PC': 0x34,
            'P': 0,
            'A': 0,
            'X': 0,
            'Y': 0,
            'S': 0xfd,
        }
        self._memory = [0] * 64 * 1024

    def reg_value(self, name: str):
        n = name.upper()
        return self._reg_values[n]

    def set_reg_value(self, name: str, value: int):
        n = name.upper()

        if n not in self._reg_values:
            raise ValueError('未知的寄存器：<{}>'.format(n))
        if n == 'PC':
            if value < 0 or value > 2 ** 16 - 1:
                raise ValueError('<{}>超过了<{}>寄存器的取值范围'.format(value, n))
        else:
            if value < 0 or value > 2 ** 8 - 1:
                raise ValueError('<{}>超过了<{}>寄存器的取值范围'.format(value, n))

        self._reg_values[n] = value

    def reset(self):
        s = self.reg_value('s')
        self.set_reg_value('s', s - 3)
