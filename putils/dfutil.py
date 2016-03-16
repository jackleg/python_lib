# -*- coding: utf8 -*-

"""pandas.DataFrame 관련 utility"""


import pandas as pd
import numpy as np


def find_by_value(df, column_name, value, first=True):
    """df의 column에 있는 특정 값의 위치를 찾는다.
    
    :param df: 값을 찾을 DataFrame
    :param column_name: 값을 찾을 column name(df[column_name])
    :param value: 찾을 값.
    :param first: 동일한 값이 여러 개 있는 경우 처음 나타나는 값을 반환할 지 여부. False이면 마지막 값을 반환.
    :return: df[column_name] == value인 index. 해당하는 값이 없다면 None.
    """
    index_list = df[df[column_name] == value].index.tolist()

    if index_list:
        if first:
            return index_list[0]
        else:
            return index_list[-1]
    else:
        return None


def has_null(ser, need_count=False):
    """series에서 null value가 있는지 여부 확인.

    :param ser: 확인할 값이 있는 Series.
    :param need_count: null 값이 몇 개나 있는지 값을 함께 반환할 지 여부.
    :return: ser에 null value가 있으면 true 없다면 false. need_count가 True라면 (null value 여부, null value 개수)의 pair.
    """

    rel_list = pd.isnull(ser)
    if need_count:
        count = rel_list.sum()
        return pd.Series([(count > 0), count], index=["has_null", "count"])
    else:
        return any(rel_list)
