#!/usr/bin/env python
# -*- coding: utf8 -*-

import sys
import pandas as pd
import statsutil

def test_calc_kld():
    ser1 = pd.Series([0.1, 0.2, 0.3, 0.4])
    ser2 = pd.Series([0.1, 0.2, 0.3, 0.4])
    assert 0.0 == statsutil.calc_kld(ser1, ser2)

    ser3 = pd.Series([0.4, 0.3, 0.2, 0.1])
    assert (0.456434819147 - statsutil.calc_kld(ser1, ser3)) <= 1.e-12


if __name__ == "__main__":
    test_calc_kld()
