#!/usr/bin/env python
# -*- coding: utf8 -*-

import strutil

def test_join():
    data = [1, 2, 3, 4]
    assert "1\t2\t3\t4" == strutil.str_join(data)


if __name__ == "__main__":
    test_join()
