# -*- coding: utf8 -*-

"""통계 관련 utility"""


import pandas as pd
import numpy as np


def calc_prob(series):
    """series에 있는 값들의 분포를 구한다.
       
    series에 있는 값들이 discrete하다고 가정하고 각 value의 확률을 구한다.
    
    :return: index는 series의 value이고, 값이 확률인 pd.Series"""
    
    return series.value_counts().sort_index() / float(len(series))


def __calc_kl(row):
    if np.isnan(row[0]) or (row[0] is None):
        return 0.0
    else:
        return row[0] * np.log(row[0]/row[1])


def calc_kld(ser1, ser2):
    """두 확률 분포 Series의 KL Divergence를 구한다.

    두 시리즈는 각각 index는 해당 아이템이고, value는 해당 아이템의 확률값을 갖는다.
    KL(ser1||ser2)를 계산한 값을 반환한다.
    이 때, ser1와 ser2의 index가 모두 동일할 필요는 없으나,
    ser1에서 확률이 0인 경우의 KL은 0이되고, ser2에서 0은 small epsilon(1e-12)으로 smoothing된다.

    :return: KL(ser1||ser2)
    """
               
    df = pd.concat([ser1, ser2], axis=1)
    df.columns = ["_1", "_2"]
    df.iloc[:, 1].fillna(1.0e-12, inplace=True) # smoothing with very small value.
    
    df["kl"] = df.apply(__calc_kl, axis=1)

    return df["kl"].sum()
