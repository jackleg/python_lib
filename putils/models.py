#!/usr/bin/env python
# -*- coding: utf8 -*-

from pyspark import SparkConf, SparkContext
from pyspark.sql import SQLContext
import pyspark.sql.functions as F
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import math
from datetime import datetime



def calculate_mpg_lambda(df, user_key_field = 'pur_mbr_no', ord_date_field = 'ord_dt', today = None):
    """
    Buy It Again: Modeling Repeat Purchase Recommendations 구현 (https://www.kdd.org/kdd2018/accepted-papers/view/buy-it-again-modeling-repeat-purchase-recommendations)
    
    :params df: 사용자 주문 테이블, 특정 아이템의 주문 정보만 있음.
    :params user_key_field: 사용자 키 필드명
    :params ord_date_field: 주문 날짜
    :returns: prior alpha, beta와 사용자별 결과값이 담긴 dataframe
    """
    
    # 실험용으로 today는 7월 10일로 고정
    today = datetime.strptime("2020-07-10", '%Y-%m-%d') if today is None else today

    # 계산 편의를 위한 전처리
    # 사용자의 구매 횟수 정보 추가
    user_count_df = df.groupby(user_key_field).count()
    df_with_count = df.join(user_count_df, user_key_field)
    
    # ord_date: 주문 날짜 (datetime)
    # first_order / last_order: 사용자의 해당 아이템 처음 / 마지막 주문일
    # count: 주문 횟수
    # duration: first_order ~ today까지의 기간
    # lambda: 사용자의 prior용 lambda, 첫번째 구매는 시작점이므로, count - 1이 실제 '기간' 동안 구매한 횟수.
    summary_df = df_with_count.withColumn('ord_date',
                                          to_date(col(ord_date_field), 'yyyyMMdd')) \
                              .groupby(user_key_field) \
                              .agg(F.min('ord_date').alias('first_order'),
                                   F.max('ord_date').alias('last_order'),
                                   F.min('count').alias('count')) \
                              .withColumn('duration',
                                          datediff(to_date(lit(today)), 'first_order')) \
                              .withColumn('lambda', (col('count') - 1) / col('duration'))
    
    # lambda sampling으로부터 gamma의 alpha, beta prior 계산
    # alpha, beta pameterization보다 단순한 방법으로 처리.
    res = summary_df.agg(F.mean('lambda').alias("mean"),
                         F.variance('lambda').alias("var"),
                        ).collect()[0].asDict()
    
    alpha = math.pow(res['mean'], 2) / res_dict['var']
    beta = res['mean'] / res_dict['var']

    # posterior 계산
    # order_period: 사용자의 평균 반복 구매 기간
    # p_alpha, p_beta, p_lambda: posterior alpha, beta, lambda
    # t_purch: 첫 구매 ~ 마지막 구매 기간
    # t_mean: 사용자별 평균 구매 주기
    # date_from_last: 마지막 구매 이후 날짜
    # mpg_beta: MPG 모델용 beta. (alpha는 기본 posterior와 동일.)
    result_df = summary_df.withColumn('p_alpha', alpha + col('count') - 1) \
                          .withColumn('p_beta', beta + col('duration')) \
                          .withColumn('p_lambda', col('p_alpha') / col('p_beta')) \
                          .withColumn('t_purch', datediff('last_order', 'first_order')) \
                          .withColumn('t_mean', col('t_purch') / (col('count')-1)) \
                          .withColumn('date_from_last', datediff(to_date(lit(today)), 'last_order')) \
                          .withColumn('mpg_beta', col('t_purch') + 2 * F.abs(col('t_mean') - col('date_from_last')) + beta) \
                          .withColumn('mpg_lambda', col('p_alpha') / col('mpg_beta'))
    
    return (alpha, beta, result_df)
