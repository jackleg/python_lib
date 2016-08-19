# -*- coding: utf8 -*-

"""pandas.DataFrame 관련 utility"""

import json
import csv
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


###############################################################################
# display
###############################################################################
def display_full(df):
    """
    truncation view로 들어가지 않고, df를 모두 출력한다.
    """
    with pd.option_context("display.max_rows", len(df)), pd.option_context("display.max_columns", len(df.columns)):
        display(df)


###############################################################################
# data_util
###############################################################################
def read_tsv(filepath_or_buffer, **kwargs):
    """seperator가 tab인 csv 읽기
    
    아래와 같은 옵션이 default로 셋팅된 read_csv의 wrapper.
    sep = tab
    header = None
    quoting = csv.QUOTE_NONE
    """
    sep = "\t" if "sep" not in kwargs else kwargs.pop("sep")
    header = None if "header" not in kwargs else kwargs.pop("header")
    quoting = csv.QUOTE_NONE if "quoting" not in kwargs else kwargs.pop("quoting")

    return pd.read_csv(filepath_or_buffer, sep=sep, header=header, quoting=quoting, **kwargs)


def read_json(filepath_or_buffer, index_col=None):
    """row 데이터가 json 포맷으로 구성된 데이터 읽기"""

    with open(filepath_or_buffer) as infile:
        df = pd.DataFrame([pd.Series(json.loads(line)) for line in infile])

        if index_col: return df.set_index(index_col)
        else: return df
