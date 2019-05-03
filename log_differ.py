# -*- coding: utf-8 -*-
import json


def logs_from_json(json_path: str):
    with open(json_path, 'rb') as f:
        logs = json.load(f)
    return logs


def bytes_from_x8(x8_num: int):
    low = x8_num & 0x0F
    high = (x8_num & 0xF0) >> 4
    return high, low


class LogDiffer(object):
    def __init__(self, logs):
        self.logs = logs
        self.cursor = 0

    def pop_log(self):
        log = self.logs[self.cursor]
        self.cursor += 1
        assert self.cursor <= 8990, "All tests passed"
        return log

    def correct_op_name(self, info: dict):
        mapping = {
            'SRA': 'LSR',
            'SLA': 'ASL',
        }
        op_name = info['op']
        if op_name in mapping:
            mapped = mapping[op_name]
            info['op'] = mapped

    def diff(self, info: dict):
        self.correct_op_name(info)
        log = self.pop_log()
        passed = True
        for key, expected in log.items():
            result = info[key]
            if result != expected:
                passed = False
        assert passed, self.message_of_diff(log, info)

    def message_of_diff(self, log, info):
        line_number_log = '\nline number:{}'.format(self.cursor)
        flags_name_log = ' ' * (45 - len(line_number_log)) + 'NVss DIZC'
        firs_line_log = line_number_log + flags_name_log
        expected_log = 'expect: '
        result_log = 'result: '

        print_order = ['PC', 'op', 'address', 'A', 'X', 'Y', 'S', 'P']
        for key in print_order:
            expected = log[key]
            result = info[key]

            if key == 'address':
                expected_log += "{:04X} ".format(expected)
                result_log += "{:04X} ".format(result)
            elif key == 'op':
                expected_log += "{} ".format(expected)
                result_log += "{} ".format(result)
            elif key == 'PC':
                expected_log += "{:04X} ".format(expected)
                result_log += "{:04X} ".format(result)
            elif key == 'P':
                e_high, e_low = bytes_from_x8(expected)
                r_high, r_low = bytes_from_x8(result)
                expected_log += "{}:{:04b} {:04b} ".format(key, e_high, e_low)
                result_log += "{}:{:04b} {:04b} ".format(key, r_high, r_low)
            else:
                expected_log += "{}:{:02X} ".format(key, expected)
                result_log += "{}:{:02X} ".format(key, result)

            # if expected == result:
            #     mark_log += ' ' * (len(expected_log) - len(mark_log))
            # else:
            #     mark_log += ' ' * (len(expected_log) - len(mark_log) - 3) + '^    '
        mark_log = '        '
        for e, r in zip(expected_log[8:], result_log[8:]):
            t = '^' if e != r else ' '
            mark_log += t

        result = '\n'.join([firs_line_log, expected_log, result_log, mark_log])
        return result

    @staticmethod
    def from_json(json_path):
        logs = logs_from_json(json_path)
        ld = LogDiffer(logs)
        return ld
