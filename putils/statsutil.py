# -*- coding: utf8 -*-

"""통계 관련 utility"""


import pandas as pd
import numpy as np
from pandas.tools.plotting import table


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


def good_ratio(target, feature, bins=10, accumulative=False, ascending=True):
    """P(target = 1 | a < feature < b) 인 확률 P를 구한다.

    feature가 특정 구간 안에 있을 때 target이 1인 확률을 구한다.
    구간은 bins의 개수로 조절하며, bins의 개수에 따라 qcut으로 feature의 구간을 구한다.

    :param target: good / bad 여부를 나타내는 Series.
    :param feature: 분포를 구할 feature Series.
    :param bins: feature의 구간 개수. default: 10
    :param accumulative: 확률을 구할 때 누적 확률을 구할 것인지 여부. False이면 해당 구간에서의 확률만 구하고, True이면 누적 확률을 구한다. default: False
    :param ascending: accumulative == True일 때, 누적 확률을 큰 값에서부터 누적할지, 작은 값부터 누적할지 결정한다. True이면 작은 값부터, False이면 큰 값부터 누적한다.
    :return: (base, prob. by section), accumulative == True라면 accumulative prob.을 추가한 triple이 반환된다.
    """

    if len(target) != len(feature):
        raise ValueError("target lenngth and feature length must be same.")

    tn = target.name
    fn = feature.name
    X = pd.concat([target, feature], axis=1)
    X['_cut'] = pd.qcut(X[fn], bins)

    # P(target = 1 | all)
    base = target.sum() / float(len(target))

    # P(target = 1 | by section)
    stat_df = X.groupby('_cut').aggregate({tn: {'count': 'count', 'good': np.sum, 'bad': lambda x: (1-x).sum()}})
    stat_df = stat_df[tn]
    stat_df.loc[:, "ratio"] = stat_df.apply(lambda row: row['good'] / float(row['count']), axis=1)

    # P(target = 1 | accumulative)
    if accumulative:
        accu = stat_df.sort_index(ascending=ascending).cumsum()
        accu.loc[:, "ratio"] = accu.apply(lambda row: row['good'] / float(row['count']), axis=1)
        accu.sort_index(inplace=True) # 역순 정렬이었을 경우 다시 순서를 맞추기 위해 재정렬한다.

    # return value
    if accumulative:
        return (base, stat_df, accu)
    else:
        return (base, stat_df)


def plot_good_ratio(target, feature, bins=10, accumulative=False, ascending=True, show_table=True, **kwargs):
    """good_ratio로 구한 P(target = 1) 확률을 그래프로 표현한다.
   
    :param target: good / bad 여부를 나타내는 Series.
    :param feature: 분포를 구할 feature Series.
    :param bins: feature의 구간 개수. default: 10
    :param accumulative: 확률을 구할 때 누적 확률을 구할 것인지 여부. False이면 해당 구간에서의 확률만 구하고, True이면 누적 확률을 구한다. default: False
    :param ascending: accumulative == True일 때, 누적 확률을 큰 값에서부터 누적할지, 작은 값부터 누적할지 결정한다. True이면 작은 값부터, False이면 큰 값부터 누적한다.
    :param show_table: feature 구간별 data table을 출력할 지 여부.
    """

    if accumulative:
        base, _, ratio_df = good_ratio(target, feature, bins, accumulative, ascending)
        title_str = "good ratio of %s / accumulative / ascending = %s" % (feature.name, ascending)
    else:
        base, ratio_df = good_ratio(target, feature, bins, accumulative, ascending)
        title_str = "good ratio of %s" % (feature.name)

    ax = ratio_df["ratio"].plot(**kwargs)
    ax.axhline(base)
    ax.set_title(title_str)
    ax.set_xlabel("%s_cut" % feature.name)
    ax.set_ylabel("good ratio")

    if show_table:
        ax.set_xlabel("")
        ax.get_xaxis().set_ticklabels([])

        ratio_df['ratio'] = ratio_df['ratio'].round(3)
        t = table(ax, ratio_df[['ratio', 'good', 'count']].T)
        t.scale(1.0, 2.0)
