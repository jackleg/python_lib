import statsmodels.api as sm
from sklearn.metrics import roc_auc_score


def calculate_TPR_FPR(df, score_col="pred", target_col="click"):
    pred_df = df[[score_col, target_col]].sort_values(score_col, ascending=False)
    pred_TPR = pred_df[target_col].cumsum() / pred_df[target_col].sum()
    pred_FPR = (1-pred_df[target_col]).cumsum() / (1-pred_df[target_col]).sum()
    
    return (pred_TPR, pred_FPR)


def draw_roc(df, score_col="pred", target_col="click", base=[]):
    ax = plt.subplots(figsize=(7, 7))
    plt.plot([0, 1], [0, 1], "--")

    for i, data in enumerate(base):
        plt.plot(data["FPR"], data["TPR"], label=data["name"], color=plt.cm.Pastel1(i))
        
    pred_TPR, pred_FPR = calculate_TPR_FPR(df, score_col, target_col)
    plt.plot(pred_FPR, pred_TPR, label="pred", color="red")

    ax[1].legend()
    
    print "auc: ", roc_auc_score(df[target_col], df[score_col])

    
def make_logit_model(training_df, test_df, cols, target_col="click", base=[]):
    train_X = training_df[cols]
    train_Y = training_df[target_col]

    logit = sm.Logit(train_Y, train_X)
    logit_result = logit.fit()
        
    display(logit_result.summary())
        
    test_df.loc[:, "pred"] = logit_result.predict(test_df[cols])

    draw_roc(test_df, base=base)
    
    return logit_result
