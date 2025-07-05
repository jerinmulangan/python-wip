#!/usr/bin/env python3
# torvik3.py

import numpy as np
import pandas as pd
import optuna
from pathlib import Path

from sklearn.model_selection import (
    TimeSeriesSplit,
    GridSearchCV,
    cross_val_score,
    cross_val_predict
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_recall_fscore_support
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.multiclass import OneVsRestClassifier
from xgboost import XGBClassifier
from sklearn.base import BaseEstimator, ClassifierMixin

def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))

def load_all_views(data_dir="data", years=range(2008,2026)):
    TYPES  = ["R","C","N"]
    VENUES = ["All","H","AN","A"]
    out = []
    for yr in years:
        parts = []
        for t in TYPES:
            for v in VENUES:
                fn = Path(data_dir)/f"trank_{yr}_{t}_{v}.csv"
                df = pd.read_csv(fn)
                pref = f"{t}_{v}_"
                df = df.add_prefix(pref).rename(
                    columns={pref+"year":"year", pref+"team":"team"}
                )
                parts.append(df)
        m = parts[0]
        for p in parts[1:]:
            m = m.merge(p, on=["year","team"], how="inner")
        out.append(m)
    return pd.concat(out, ignore_index=True)

def attach_label(df, post_csv="data/trank_2008_2025_post.csv", max_year=2024):
    post = pd.read_csv(post_csv)[["year","team","tourney_res"]]
    df   = df.merge(post, on=["year","team"], how="left")
    df   = df[(df.year <= max_year) & df.tourney_res.notna()].copy()

    df["tourney_res"] = df["tourney_res"].replace({
        "R68":    "R64",
        "CHAMPS": "Champion",
        "Finals": "Runner-Up",
    })
    print("Unique tourney_res:", df["tourney_res"].unique())

    order = [
        "R64","R32","Sweet Sixteen","Elite Eight",
        "Final Four","Runner-Up","Third Place","Champion"
    ]
    ord_map = {r:i for i,r in enumerate(order)}

    df["label"] = df["tourney_res"].map(ord_map)
    before = len(df)
    df = df[df["label"].notna()].copy()
    df["label"] = df["label"].astype(int)
    print(f"Dropped {before-len(df)} rows with unmapped tourney_res")

    present = sorted(df["label"].unique())
    order   = [r for r in order if ord_map[r] in present]

    remap = {old: new for new, old in enumerate(present)}
    df["label"] = df["label"].map(remap).astype(int)

    feat_df = (
        df
        .drop(columns=["year","team","tourney_res","label"])
        .select_dtypes(include=[np.number])
    )
    X = feat_df.to_numpy()
    y = df["label"].values
    return X, y, df, order, feat_df.columns.tolist()

def build_bracket_for_year(df_all, predictor, order, year, feature_names):
    dfy = df_all[df_all.year == year].copy()
    Xy  = dfy[feature_names].to_numpy()
    if hasattr(predictor, "predict_proba"):
        probs = predictor.predict_proba(Xy)
    else:
        probs = sigmoid(Xy.dot(predictor.T))
    idx = np.argmax(probs, axis=1)
    dfy["pred_round"] = [order[i] for i in idx]
    om = {r:i for i,r in enumerate(order)}
    return {
        "Sweet 16":  dfy[dfy.pred_round >= om["Sweet Sixteen"]]["team"].tolist(),
        "Elite 8":   dfy[dfy.pred_round >= om["Elite Eight"]]["team"].tolist(),
        "Final 4":   dfy[dfy.pred_round >= om["Final Four"]]["team"].tolist(),
        "Finalists": dfy[dfy.pred_round >= om["Runner-Up"]]["team"].tolist(),
        "Champion":  dfy[dfy.pred_round == om["Champion"]]["team"].tolist(),
    }

def evaluate_ensembles(X, y, order):
    print("\n––– RF & GBM Comparison (5-fold CV) –––")
    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    gb = GradientBoostingClassifier(
        n_estimators=200, learning_rate=0.1, max_depth=3, random_state=42
    )
    for name, mdl in [("RF", rf), ("GBM", gb)]:
        scores = cross_val_score(mdl, X, y, cv=5, scoring="accuracy", n_jobs=-1)
        print(f"{name} CV acc: {scores.mean():.4f} ± {scores.std():.4f}")
        mdl.fit(X, y)
        preds = mdl.predict(X)
        labs  = sorted(set(y))
        names = [order[i] for i in labs]
        print(f"\n{name} classification report:")
        print(classification_report(y, preds, labels=labs, target_names=names, zero_division=0))
    return rf, gb

def evaluate_xgb(X, y, order):
    print("\n––– XGBoost with TimeSeriesSplit CV –––")
    tscv = TimeSeriesSplit(n_splits=5)
    labs = sorted(set(y))
    xgb = XGBClassifier(
        objective="multi:softprob",
        num_class=len(labs),
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1
    )
    grid = {
        "n_estimators":[200,500],
        "max_depth":[3,5],
        "learning_rate":[0.01,0.1],
        "subsample":[0.7,1.0],
        "colsample_bytree":[0.7,1.0],
    }
    search = GridSearchCV(xgb, grid, cv=tscv, scoring="accuracy", n_jobs=-1)
    search.fit(X, y)
    best = search.best_estimator_
    print("Best XGB params:", search.best_params_)
    print(f"XGB CV accuracy: {search.best_score_:.4f}")

    yp = best.predict(X)
    names = [order[i] for i in labs]
    print("\nXGB classification report:")
    print(classification_report(y, yp, labels=labs, target_names=names, zero_division=0))
    return best

class LogisticWrapper(BaseEstimator, ClassifierMixin):
    def __init__(self, W):
        self.W = W

    def fit(self, X, y=None):
        self.classes_ = np.arange(self.W.shape[0])
        return self

    def predict(self, X):
        return np.argmax(self.predict_proba(X), axis=1)

    def predict_proba(self, X):
        return sigmoid(X.dot(self.W.T))

def stack_models(models, X, y, order):
    print("\n––– Stacking via out-of-fold predictions –––")
    K = len(order)
    oof = np.zeros((len(y), K * len(models)))
    for i, (name, mdl) in enumerate(models.items()):
        prob = cross_val_predict(
            mdl, X, y,
            cv=5,
            method="predict_proba",
            n_jobs=-1
        )
        oof[:, i*K:(i+1)*K] = prob
        print(f"  collected OOF prob for {name}")
    meta = LogisticRegression(multi_class="multinomial", max_iter=2000)
    meta.fit(oof, y)
    yp = meta.predict(oof)
    labs  = sorted(set(y))
    names = [order[i] for i in labs]
    print("\nMeta-model classification report:")
    print(classification_report(y, yp, labels=labs, target_names=names, zero_division=0))
    return meta

def calibrate_models(models, X, y):
    print("\n––– Calibrating probabilities –––")
    calibrated = {}
    for name, mdl in models.items():
        if isinstance(mdl, LogisticWrapper):
            continue
        cal = CalibratedClassifierCV(mdl, cv=5, method="isotonic", n_jobs=-1)
        cal.fit(X, y)
        calibrated[name] = cal
        print(f"  calibrated {name}")
    return calibrated

def time_series_splits(years, skip=2020):
    yrs = sorted(set(years) - {skip})
    splits = []
    for i in range(10, len(yrs)):
        splits.append((yrs[:i], [yrs[i]]))
    return splits

def main():
    df_all = load_all_views("data", range(2008,2025))
    X, y, df, order, feats = attach_label(df_all)

    # Tune OVR Logistic via TS CV
    print("\n→ Tuning OVR LogisticRegression via TS CV")
    tscv = TimeSeriesSplit(n_splits=5)
    best_score, best_C = -np.inf, None
    for C in [100, 10, 1, 0.1, 0.01]:
        lr = LogisticRegression(C=C, solver="liblinear", max_iter=2000)
        sc = cross_val_score(lr, X, y, cv=tscv, scoring="accuracy", n_jobs=-1)
        print(f"  C={C:<6} → acc={sc.mean():.4f} ± {sc.std():.4f}")
        if sc.mean() > best_score:
            best_score, best_C = sc.mean(), C
    print(f"\n★ Best CV acc={best_score:.4f} @ C={best_C}")

    ovr = OneVsRestClassifier(
        LogisticRegression(C=best_C, solver="liblinear", max_iter=2000),
        n_jobs=-1
    )
    ovr.fit(X, y)
    coefs = np.vstack([est.coef_[0] for est in ovr.estimators_])

    print("\nFeature importances (Logistic OVR):")
    for k, cls in enumerate(order):
        top10 = np.argsort(np.abs(coefs[k]))[::-1][:10]
        print(f"\nTop features for '{cls}':")
        for idx in top10:
            print(f"  {feats[idx]:<30s} {coefs[k,idx]:+.4f}")

    # RF & GBM
    rf_base, gb_base = evaluate_ensembles(X, y, order)

    # XGBoost
    xgb_base = evaluate_xgb(X, y, order)


    base_models = {
        "LogisticOVR": LogisticWrapper(coefs),
        "RF":          rf_base,
        "GBM":         gb_base,
        "XGB":         xgb_base
    }
    cal_models = calibrate_models(base_models, X, y)
    stack_mod  = stack_models(base_models, X, y, order)

    predictors = [
        ("LogisticOVR", coefs),
        ("RF",          rf_base),
        ("GBM",         gb_base),
        ("XGB",         xgb_base),
    ]
    for n,m in cal_models.items():
        predictors.append((f"Cal_{n}", m))
    predictors.append(("Stacked", stack_mod))

    for name, mdl in predictors:
        surv = build_bracket_for_year(df, mdl, order, 2025, feats)
        print(f"\n=== Predicted bracket for 2025 ({name}) ===")
        for stage in ["Sweet 16", "Elite 8", "Final 4", "Finalists", "Champion"]:
            print(f"{stage:10s}: {surv[stage]}")

if __name__=="__main__":
    main()
