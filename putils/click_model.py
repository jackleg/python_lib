# -*- coding: utf8 -*-

"""click model 관련 소스 모음"""

import pandas as pd
import numpy as np



def calculate_rank_prob(df, i_cols=["query", "prdno"], j_cols=["rank"], c_col="clk_count", v_col="imp_count",
                        alpha=1.2, beta=0.01, view_sf=40, max_iter=100):
    """gamma-poisson model에 의한 position 정규화
    
    Position-Normalized Click Prediction in Search Advertising의 gamma-poisson model 구현
    https://dl.acm.org/citation.cfm?id=2339654
    
    df: i, j index에서 사용할 column들과 impression, click 데이터를 가지고 있는 dataframe
    i_cols: i index에서 사용할 column. default: ["query", "prdno"]
    j_cols: j index에서 사용할 column. default: ["rank"]
    c_col: click count column. default: "clk_count"
    v_col: impression count column. default: "imp_count"
    alpha: gamma parameter, default: 1.2
    beta: gamma parameter, default: 0.01
    view_sf: ctr 계산시 view에 적용하는 smoothing factor.
    max_iter: max iteration count.
    
    return:
        (qj, qj_df, pi)
    """
    
    # calculate initial pi
    _imm = df.groupby(i_cols) \
                .aggregate({v_col: "sum", c_col: "sum"}) \
                .reset_index()
    
    _imm.loc[:, "pi"] = np.minimum(_imm[c_col] / (_imm[v_col] + view_sf), 1.0)
    
    pi = _imm[i_cols + ["pi"]]

    # 각각 e-, m- step에서 사용하는 numerator.
    # iteration이 돌아도 변하지 않는 값들이므로 미리 계산해 둔 값을 사용
    e_numerator = df.groupby(j_cols).aggregate({c_col: "sum"}) + (alpha - 1.0)
    m_numerator = df.groupby(i_cols).aggregate({c_col: "sum"}).reset_index()

    t_count = 0
    prev_qj = pd.Series()
    qj_df = pd.DataFrame()
    while True:
        t_count += 1
        logging.info("%d-iter..." % t_count)
        
        # E-step: qj
        _immediate = pd.merge(df, pi, on=i_cols)
        _immediate.loc[:, "vijpi"] = (_immediate[v_col] + view_sf) * _immediate["pi"]
        _denominator = _immediate.groupby(j_cols).aggregate({"vijpi": "sum"}) + 1/beta

        qj = e_numerator[c_col] / _denominator["vijpi"]
        qj_df[t_count] = qj

        if (not prev_qj.empty) and np.allclose(prev_qj, qj, atol=1e-4): break

        prev_qj = qj

        # M-step: pi
        _immediate = pd.merge(df, pd.DataFrame({"qj": qj}), left_on=j_cols, right_index=True)
        _immediate.loc[:, "vijqj"] = (_immediate[v_col] + view_sf) * _immediate["qj"]
        _denominator = _immediate.groupby(i_cols).aggregate({"vijqj": "sum"}).reset_index()

        _final = pd.merge(m_numerator, _denominator, on=i_cols)
        _final.loc[:, "pi"] = _final[c_col] / _final["vijqj"]

        pi = _final[i_cols + ["pi"]]

        if (t_count % 10 == 0):
            display(qj_df)
            
        if t_count >= max_iter: break
            
    return qj, qj_df, pi

