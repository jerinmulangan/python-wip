#!/usr/bin/env python3
# torviktest3.py

import numpy as np
import pandas as pd
import optuna
from pathlib import Path
from sklearn.model_selection import (
    LeaveOneOut,
    TimeSeriesSplit,
    GridSearchCV,
    cross_val_score,
    cross_val_predict,
)
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_recall_fscore_support,
)
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from xgboost import XGBClassifier

def sigmoid(z):
    return 1 / (1 + np.exp(-np.clip(z, -500, 500)))

def gradient_ascent(X, y, lam, lr, max_iter=1000):
    w = np.zeros(X.shape[1])
    for _ in range(max_iter):
        p = sigmoid(X.dot(w))
        w += lr * (X.T.dot(y - p) - lam*w)
    return w

def load_all_views(data_dir="data", years=range(2008,2026)):
    TYPES  = ["R","C","N"]
    VENUES = ["All","H","AN","A"]
    out = []
    for yr in years:
        parts = []
        for t in TYPES:
            for v in VENUES:
                df = pd.read_csv(Path(data_dir)/f"trank_{yr}_{t}_{v}.csv")
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

def attach_label(df,
                 post_csv="data/trank_2008_2025_post.csv",
                 max_year=2024):
    post = pd.read_csv(post_csv)[["year","team","tourney_res"]]
    df   = df.merge(post, on=["year","team"], how="left")
    df   = df[(df.year <= max_year) & df.tourney_res.notna()].copy()

    # 1) synonym cleanup
    df["tourney_res"] = df["tourney_res"].replace({
        "R68":    "R64",
        "CHAMPS": "Champion",
        "Finals": "Runner-Up",
    })

    # 2) inspect
    print("Unique tourney_res:", df["tourney_res"].unique())

    # 3) build your ordered classes
    order = [
        "R64","R32","Sweet Sixteen","Elite Eight",
        "Final Four","Runner-Up","Third Place","Champion"
    ]
    ord_map = {r:i for i,r in enumerate(order)}

    # 4) map & drop any that still weren’t in ord_map
    df["label"] = df["tourney_res"].map(ord_map)
    before = len(df)
    df = df[df["label"].notna()].copy()
    df["label"] = df["label"].astype(int)
    print(f"Dropped {before-len(df)} rows with unmapped tourney_res")

    # 4b) prune order down to present labels
    present = sorted(df["label"].unique())
    order = [ r for r in order if ord_map[r] in present]

    # 5) binary flags
    df["made_S16"] = (df.label >= ord_map["Sweet Sixteen"]).astype(int)
    df["is_champ"] = (df.label == ord_map["Champion"]).astype(int)

    # 6) feature matrix
    feat_df = (
        df
          .drop(columns=["year","team","tourney_res","label"])
          .select_dtypes(include=[np.number])
    )
    X = feat_df.to_numpy()
    y = df["label"].values
    return (
        X,
        y,
        df["made_S16"].values,
        df["is_champ"].values,
        df,
        order,
        feat_df.columns.tolist()
    )


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
        mdl.fit(X, y)
        print(f"{name} report:\n{classification_report(y, mdl.predict(X), target_names=order)}")
        # nly report on labels that are present
        labels_present = sorted(set(y))
        target_names = [ order[i] for i in labels_present ]
        print(f"{name} report:\n" +
              classification_report(
                  y,
                  mdl.predict(X),
                  labels=labels_present,
                  target_names=target_names
              )
        )
    return rf, gb


def evaluate_xgb(X, y, order):
    print("\n––– XGBoost with TimeSeriesSplit CV –––")
    tscv = TimeSeriesSplit(n_splits=5)
    xgb = XGBClassifier(
        objective="multi:softprob",
        num_class=len(order),
        eval_metric="mlogloss",
        use_label_encoder=False,
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
    print("\nXGB report:\n" +
          classification_report(y, best.predict(X), target_names=order))
    
    # report on present labels
    yp = best.predict(X)
    labels_present = sorted(set(y))
    target_names = [ order[i] for i in labels_present ]
    print("\nXGB report:\n" +
          classification_report(
              y,
              yp,
              labels=labels_present,
              target_names=target_names
          )
    )    

    return best

class LogisticWrapper:
    def __init__(self, W):
        self.W = W
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
    print("\nMeta-model report:\n" +
          classification_report(y, meta.predict(oof), target_names=order))
    
    # report present labels
    ypred = meta.predict(oof)
    labels_present = sorted(set(y))
    target_names = [ order[i] for i in labels_present ]
    print("\nMeta-model report:\n" +
          classification_report(
              y,
              ypred,
              labels=labels_present,
              target_names=target_names
          )
    )    

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

def time_series_splits(years, skip=2020):

    all_years = sorted(set(years) - {skip})
    splits = []
    for i in range(10, len(all_years)): 
        train = all_years[:i]
        test  = [all_years[i]]
        splits.append((train, test))
    return splits

def optimize_rf(trial, X, y):
    params = {
        "n_estimators": trial.suggest_int("n_estimators", 100, 1000),
        "max_depth":    trial.suggest_int("max_depth", 3, 15),
        "max_features": trial.suggest_categorical("max_features", ["sqrt","log2", None]),
    }
    rf = RandomForestClassifier(**params, random_state=42)
    scores = cross_val_score(rf, X, y, cv=5, scoring="accuracy")
    return scores.mean()

def optimize_gb(trial, X, y):
    params = {
        "n_estimators":    trial.suggest_int("n_estimators", 100, 1000),
        "max_depth":       trial.suggest_int("max_depth", 3, 10),
        "learning_rate":   trial.suggest_loguniform("learning_rate", 1e-3, 0.3),
        "subsample":       trial.suggest_float("subsample", 0.5, 1.0),
        "max_features":    trial.suggest_categorical("max_features", ["sqrt","log2", None]),
    }
    gb = GradientBoostingClassifier(**params, random_state=42)
    scores = cross_val_score(gb, X, y, cv=5, scoring="accuracy")
    return scores.mean()

def evaluate_time_series(X, y, years, model):
    splits = time_series_splits(years)
    accs, prs, rcs, f1s = [], [], [], []
    for train_y, test_y in splits:
        idx_tr = [i for i,yr in enumerate(years) if yr in train_y]
        idx_te = [i for i,yr in enumerate(years) if yr in test_y]
        Xtr, Xte = X[idx_tr], X[idx_te]
        ytr, yte = y[idx_tr], y[idx_te]
        mdl = model.fit(Xtr,ytr)
        pred = mdl.predict(Xte)
        accs.append(accuracy_score(yte,pred))
        p,r,f,_ = precision_recall_fscore_support(yte,pred,average="weighted")
        prs.append(p); rcs.append(r); f1s.append(f)
    print("Time-series CV: ACC={:.3f}±{:.3f}".format(np.mean(accs),np.std(accs)))
    print("               PR={:.3f}±{:.3f}".format(np.mean(prs),np.std(prs)))
    print("               RC={:.3f}±{:.3f}".format(np.mean(rcs),np.std(rcs)))
    print("               F1={:.3f}±{:.3f}".format(np.mean(f1s),np.std(f1s)))

def loo_tune(X, y, order, lrs=[1e-3,1e-2,1e-1], lams=[0.01,0.1,1,10]):
    loo = LeaveOneOut()
    best_score, best_params = -1, None
    n = len(y)
    for lr in lrs:
        for lam in lams:
            preds = np.zeros(n, dtype=int)
            for i, (tr, te) in enumerate(loo.split(X)):
                K = len(order)
                W = np.zeros((K, X.shape[1]))
                for k in range(K):
                    yk = (y[tr] == k).astype(int)
                    W[k] = gradient_ascent(X[tr], yk, lam, lr)
                preds[i] = np.argmax(sigmoid(W.dot(X[te][0])))
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

def main():
    # Load & label 
    df_all = load_all_views("data", range(2008,2025))
    X, y, y_s16, y_champ, df, order, feat_names = attach_label(df_all)

    # Fit OVR‐logistic, get W for stacking/calibration
    print("\n→ Tuning & training one-vs-rest logistic")
    lr, lam = loo_tune(X, y, order)
    W     = train_final(X, y, order, lr, lam)

    # 1a) Predict made Sweet 16?
    print("\n→ Binary: made Sweet 16?")
    model_s16 = LogisticRegression(class_weight="balanced", max_iter=1000)
    evaluate_time_series(X, y_s16, df.year.values, model_s16)

    # 1b) Hierarchical on those that made S16
    print("\n→ Hierarchical: exit round for S16 teams")
    idx_s16 = y_s16==1
    model_hier = GradientBoostingClassifier()
    evaluate_time_series(X[idx_s16], y[idx_s16], df.year.values[idx_s16], model_hier)

    # 1c) Champion vs. rest
    print("\n→ Binary: Champion vs Rest")
    model_champ = LogisticRegression(class_weight="balanced", max_iter=1000)
    evaluate_time_series(X, y_champ, df.year.values, model_champ)

    # 2) Bayesian‐optimized RF & GBM via Optuna
    print("\n→ Optimizing Random Forest")
    study_rf = optuna.create_study(direction="maximize")
    study_rf.optimize(lambda tr: optimize_rf(tr, X, y), n_trials=30)
    rf_opt = RandomForestClassifier(**study_rf.best_params, random_state=42)
    evaluate_time_series(X, y, df.year.values, rf_opt)

    print("\n→ Optimizing Gradient Boosting")
    study_gb = optuna.create_study(direction="maximize")
    study_gb.optimize(lambda tr: optimize_gb(tr, X, y), n_trials=30)
    gb_opt = GradientBoostingClassifier(**study_gb.best_params, random_state=42)
    evaluate_time_series(X, y, df.year.values, gb_opt)

    # 2) and 4) Standard RF/GBM & XGB grid CV for comparison
    rf_base, gb_base = evaluate_ensembles(X, y, order)
    xgb_base       = evaluate_xgb(X, y, order)

    # 6) Calibration & stacking —
    base_models = {
        "LogisticOVR": LogisticWrapper(W), 
        "RF": rf_base, 
        "GBM": gb_base, 
        "XGB": xgb_base
    }
    cal_models = calibrate_models(base_models, X, y)
    stack_mod  = stack_models(base_models, X, y, order)

    # Feature importances (OVR logistic)
    print("\nFeature importances (Logistic OVR):")
    for k, cls in enumerate(order):
        idx = np.argsort(np.abs(W[k]))[::-1][:10]
        print(f"\nTop features for '{cls}':")
        for i in idx:
            print(f"  {feat_names[i]:<30s} {W[k,i]:+.4f}")

    # 6) Build & print brackets for each predictor
    predictors = [
        ("LogisticOVR",    W),
        ("RandomForest",   rf_base),
        ("GradientBoosting",gb_base),
        ("XGBoost",        xgb_base)
    ]
    predictors += [(f"Cal_{n}", m) for n, m in cal_models.items()]
    predictors.append(("Stacked", stack_mod))

    for name, mdl in predictors:
        surv = build_bracket_for_year(df_all, mdl, order, 2025, feat_names)
        print(f"\n=== Predicted bracket for 2025 ({name}) ===")
        print("Sweet 16  :", surv["Sweet 16"])
        print("Elite 8   :", surv["Elite 8"])
        print("Final 4   :", surv["Final 4"])
        print("Finalists :", surv["Finalists"])
        print("Champion  :", surv["Champion"])

if __name__ == "__main__":
    main()