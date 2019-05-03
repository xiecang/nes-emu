# -*- coding: utf-8 -*-
import utils


def test_signed_number():
    test_cases = [
        ([1], 1),
        ([1, 0], 1),
        ([0, 1], 256),
        ([255], -1),
        ([0, 255], -256),
    ]
    for case in test_cases:
        input = case[0]
        expected = case[1]
        result = utils.signed_number(input)
        assert expected == result, (case, result)
