#!/usr/bin/env python3
# torviktest2.py

import numpy as np
import pandas as pd
import warnings
from pathlib import Path

from sklearn.model_selection import (
    LeaveOneOut, TimeSeriesSplit,
    GridSearchCV, cross_val_score,
    cross_val_predict
)
from sklearn.metrics          import accuracy_score, classification_report
from sklearn.ensemble         import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration      import CalibratedClassifierCV
from sklearn.linear_model     import LogisticRegression
from xgboost                  import XGBClassifier

from sklearn.base import BaseEstimator, ClassifierMixin

def sigmoid(z):
    z = np.clip(z, -500, 500)
    return 1 / (1 + np.exp(-z))

def compute_log_likelihood(X, y, w, lam):
    z = X.dot(w)
    z = np.clip(z, -500, 500)
    return (y*z - np.log1p(np.exp(z))).sum() - (lam/2)*(w**2).sum()

def gradient_ascent(X, y, lam, lr, max_iter=1000):
    w = np.zeros(X.shape[1])
    for _ in range(max_iter):
        p = sigmoid(X.dot(w))
        grad = X.T.dot(y - p) - lam*w
        w += lr * grad
    return w


def load_all_views(data_dir="data", years=range(2008,2026)):
    TYPES  = ["R","C","N"]
    VENUES = ["All","H","AN","A"] 
    frames = []
    for yr in years:
        parts = []
        for t in TYPES:
            for v in VENUES:
                path = Path(data_dir) / f"trank_{yr}_{t}_{v}.csv"
                df = pd.read_csv(path)
                pref = f"{t}_{v}_"
                df = df.add_prefix(pref)
                df = df.rename(columns={pref+"year":"year", pref+"team":"team"})
                parts.append(df)
        merged = parts[0]
        for p in parts[1:]:
            merged = merged.merge(p, on=["year","team"], how="inner")
        frames.append(merged)
    return pd.concat(frames, ignore_index=True)

def attach_label(df, post_csv="data/trank_2008_2025_post.csv", max_year=2024):
    post = pd.read_csv(post_csv)[["year","team","tourney_res"]]
    df = df.merge(post, on=["year","team"], how="left")
    df = df[(df.year <= max_year) & df.tourney_res.notna()].copy()

    print("Unique tourney_res values:", df["tourney_res"].unique())
    order = [
        "R64","R32","Sweet Sixteen","Elite Eight",
        "Final Four","Runner-Up","Third Place","Champion"
    ]
    ord_map = {r:i for i,r in enumerate(order)}
    df["label"] = df["tourney_res"].map(ord_map)

    before = len(df)
    df = df[df.label.notna()].copy()
    df["label"] = df["label"].astype(int)
    print(f"Dropped {before-len(df)} rows with unmapped tourney_res")

    before = len(df)
    df = df[df.label.notna()].copy()
    df["label"] = df["label"].astype(int)
    print(f"Dropped {before-len(df)} rows with unmapped tourney_res")

    # prune for present labels
    present = sorted(df["label"].unique())
    order   = [ cls for cls in order if ord_map[cls] in present ]

    feat_df = (
        df
          .drop(columns=["year","team","tourney_res","label"])
          .select_dtypes(include=[np.number])
    )
    X = feat_df.to_numpy()
    y = df["label"].values
    return X, y, df, order, feat_df.columns.tolist()

def loo_tune(X, y, order, lrs=[1e-3,1e-2,1e-1], lams=[0.01,0.1,1,10]):
    loo = LeaveOneOut()
    best_score, best_params = -1, None
    n = len(y)

    for lr in lrs:
        for lam in lams:
            preds = np.zeros(n, dtype=int)
            for i, (tr, te) in enumerate(loo.split(X)):
                # train one-vs-rest
                K = len(order)
                W = np.zeros((K, X.shape[1]))
                for k in range(K):
                    yk = (y[tr] == k).astype(int)
                    W[k] = gradient_ascent(X[tr], yk, lam, lr)
                # predict held-out
                scores = sigmoid(W.dot(X[te][0]))
                preds[i] = np.argmax(scores)
            acc = accuracy_score(y, preds)
            print(f"LOOCV @ lr={lr}, lam={lam} → acc={acc:.4f}")
            if acc > best_score:
                best_score, best_params = acc, (lr, lam)
    print(f"\n★ Best LOOCV acc={best_score:.4f} @ lr,lam={best_params}")
    return best_params

def train_final(X, y, order, lr, lam):
    K = len(order)
    W = np.zeros((K, X.shape[1]))
    for k in range(K):
        yk = (y == k).astype(int)
        W[k] = gradient_ascent(X, yk, lam, lr)
    return W

def build_bracket_for_year(df_all, predictor, order, year, feature_names):
    df_year = df_all[df_all.year == year].copy()
    feat_df = (df_year.drop(columns=["year","team"])
                      .select_dtypes(include=[np.number]))
    Xy = feat_df[feature_names].to_numpy()
    if hasattr(predictor, "predict_proba"):
        probs = predictor.predict_proba(Xy)
    else:
        probs = sigmoid(Xy.dot(predictor.T))
    idx = np.argmax(probs, axis=1)
    df_year["pred_round"] = [order[i] for i in idx]
    om = {r:i for i,r in enumerate(order)}
    return {
        "Sweet 16":  df_year[df_year.pred_round >= om["Sweet Sixteen"]]["team"].tolist(),
        "Elite 8":   df_year[df_year.pred_round >= om["Elite Eight"]]["team"].tolist(),
        "Final 4":   df_year[df_year.pred_round >= om["Final Four"]]["team"].tolist(),
        "Finalists": df_year[df_year.pred_round >= om["Runner-Up"]]["team"].tolist(),
        "Champion":  df_year[df_year.pred_round == om["Champion"]]["team"].tolist(),
    }

def evaluate_ensembles(X, y, order):
    print("\n––– RF & GBM Comparison (5-fold CV) –––")
    rf = RandomForestClassifier(n_estimators=200, random_state=42, n_jobs=-1)
    gb = GradientBoostingClassifier(n_estimators=200, learning_rate=0.1,
                                    max_depth=3, random_state=42)
    for name, mdl in [("RandomForest", rf), ("GradientBoosting", gb)]:
        scores = cross_val_score(mdl, X, y, cv=5, scoring="accuracy", n_jobs=-1)
        print(f"{name} CV acc: {scores.mean():.4f} ± {scores.std():.4f}")
        

        labels_present = sorted(set(y))
        names_present  = [order[i] for i in labels_present]
        preds = cross_val_predict(mdl, X, y, cv=5, method="predict", n_jobs=-1)
        print(f"\n{name} 5-fold CV classification report:")
        print(classification_report(
            y,
            preds,
            labels=labels_present,
            target_names=names_present
        ))

        return rf, gb


def evaluate_xgb(X, y, order):
    print("\n––– XGBoost with TimeSeriesSplit CV –––")
    tscv = TimeSeriesSplit(n_splits=5)
    xgb = XGBClassifier(
        objective="multi:softprob",
        num_class=len(order),
        eval_metric="mlogloss",
        random_state=42,
        n_jobs=-1
    )
    param_grid = {
        "n_estimators":    [200, 500],
        "max_depth":       [3, 5],
        "learning_rate":   [0.01, 0.1],
        "subsample":       [0.7, 1.0],
        "colsample_bytree":[0.7, 1.0],
    }
    search = GridSearchCV(xgb, param_grid, cv=tscv, scoring="accuracy", n_jobs=-1)
    search.fit(X, y)
    best = search.best_estimator_
    print("Best XGB params:", search.best_params_)
    print(f"XGB CV accuracy: {search.best_score_:.4f}")
    
    yp = best.predict(X)
    labels_present = sorted(set(y))
    names_present  = [order[i] for i in labels_present]
    print("\nXGB classification report:")
    print(classification_report(
        y,
        yp,
        labels=labels_present,
        target_names=names_present
    ))

    return best

class LogisticWrapper(BaseEstimator, ClassifierMixin):
    def __init__(self, W):
        self.W = W

    def fit(self, X, y=None):
        return self

    def predict_proba(self, X):
        return sigmoid(X.dot(self.W.T))

def stack_models(models, X, y, order):
    print("\n––– Stacking via out-of-fold predictions –––")
    K = len(order)
    oof = np.zeros((len(y), K * len(models)))
    for i, (name, mdl) in enumerate(models.items()):
        prob = cross_val_predict(mdl, X, y, cv=5, method="predict_proba", n_jobs=-1)
        oof[:, i*K:(i+1)*K] = prob
        print(f"  collected OOF prob for {name}")
    meta = LogisticRegression(multi_class="multinomial", max_iter=2000)
    meta.fit(oof, y)
    
    ypred = meta.predict(oof)
    labels_present = sorted(set(y))
    names_present  = [order[i] for i in labels_present]
    print("\nMeta-model classification report:")
    print(classification_report(
        y,
        ypred,
        labels=labels_present,
        target_names=names_present
    ))

    return meta

def calibrate_models(models, X, y):
    print("\n––– Calibrating probabilities –––")
    calibrated = {}
    for name, mdl in models.items():
        cal = CalibratedClassifierCV(mdl, cv=5, method="isotonic")
        cal.fit(X, y)
        calibrated[name] = cal
        print(f"  calibrated {name}")
    return calibrated

def main():

    df_all = load_all_views("data", range(2008,2026))
    X, y, df_train, order, feat_names = attach_label(df_all)

    lr, lam = loo_tune(X, y, order)
    W = train_final(X, y, order, lr, lam)

    rf_model, gb_model = evaluate_ensembles(X, y, order)

    xgb_model = evaluate_xgb(X, y, order)

    base_models = {
        "LogisticOVR": LogisticWrapper(W),
        "RandomForest": rf_model,
        "GradientBoosting": gb_model,
        "XGBoost": xgb_model
    }
    cal_models = calibrate_models(base_models, X, y)

    stack_model = stack_models(base_models, X, y, order)

    print("\nFeature importances (Logistic OVR):")
    for k, cls in enumerate(order):
        idx = np.argsort(np.abs(W[k]))[::-1][:10]
        print(f"\nTop features for '{cls}':")
        for i in idx:
            print(f"  {feat_names[i]:<30s} {W[k,i]:+.4f}")

    predictors = [
        ("LogisticOVR", W),
        ("RandomForest", rf_model),
        ("GradientBoosting", gb_model),
        ("XGBoost", xgb_model)
    ]
    predictors += [(f"Cal_{name}", mdl) for name, mdl in cal_models.items()]
    predictors.append(("Stacked", stack_model))

    for name, mdl in predictors:
        surv = build_bracket_for_year(df_all, mdl, order, 2025, feat_names)
        print(f"\n=== Bracket for 2025 ({name}) ===")
        print("Sweet 16  :", surv["Sweet 16"])
        print("Elite 8   :", surv["Elite 8"])
        print("Final 4   :", surv["Final 4"])
        print("Finalists :", surv["Finalists"])
        print("Champion  :", surv["Champion"])

if __name__ == "__main__":
    main()