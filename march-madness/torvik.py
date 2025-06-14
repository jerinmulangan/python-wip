#!/usr/bin/env python3
# torvik.py

import numpy as np
import pandas as pd
import warnings

from pathlib      import Path
from sklearn.model_selection import LeaveOneOut
from sklearn.metrics         import accuracy_score, classification_report

from sklearn.ensemble       import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import cross_val_score

#  existing funcs 
def sigmoid(z):
    z = np.clip(z, -500, 500)
    return 1 / (1 + np.exp(-z))

def compute_log_likelihood(X, y, w, lam):
    z = X.dot(w)
    z = np.clip(z, -500, 500)
    return (y*z - np.log(1+np.exp(z))).sum() - (lam/2)*(w**2).sum()

def gradient_ascent(X, y, lam, lr, max_iter=1000):
    w = np.zeros(X.shape[1])
    for i in range(max_iter):
        p = sigmoid(X.dot(w))
        grad = X.T.dot(y - p) - lam*w
        w += lr * grad
    return w

#  1. load & merge all 12 views per year 
def load_all_views(data_dir="data", years=range(2008,2025+1)):
    TYPES  = ["R","C","N"]
    VENUES = ["All","H","AN","A"]  
    all_frames = []
    for yr in years:
        parts = []
        for t in TYPES:
            for v in VENUES:
                fn = Path(data_dir)/f"trank_{yr}_{t}_{v}.csv"
                df = pd.read_csv(fn)
                pref = f"{t}_{v}_"
                df = df.add_prefix(pref)
                df = df.rename(columns={pref+"year":"year", pref+"team":"team"})
                parts.append(df)
        merged = parts[0]
        for df2 in parts[1:]:
            merged = merged.merge(df2, on=["year","team"], how="inner")
        all_frames.append(merged)
    return pd.concat(all_frames, ignore_index=True)

#  2. attach the 7-way label 
def attach_label(df,
                 post_csv="data/trank_2008_2025_post.csv",
                 max_year=2024):
    # 1) merge in tournament results and filter to seasons ≤ max_year
    post = pd.read_csv(post_csv)[["year","team","tourney_res"]]
    df   = df.merge(post, on=["year","team"], how="left")
    df   = df[(df.year <= max_year) & df.tourney_res.notna()].copy()

    #  1) PRINT unique values 
    print("Unique tourney_res values:", df["tourney_res"].unique())

    #  2) EXPAND ord_map to include any extras 
    #    (add any new strings above into this list)
    order = [
        "R64","R32","Sweet Sixteen","Elite Eight",
        "Final Four","Runner-Up","Third Place","Champion"
    ]
    ord_map = {r:i for i,r in enumerate(order)}
    df["label"] = df["tourney_res"].map(ord_map)

    #  3) DROP any rows that didn’t map (i.e. still NaN) 
    before = len(df)
    df = df[df["label"].notna()].copy()
    df["label"] = df["label"].astype(int)
    after = len(df)
    print(f"Dropped {before-after} rows with unmapped tourney_res")

    #  build feature matrix 
    feat_df = (
        df
          .drop(columns=["year","team","tourney_res","label"])
          .select_dtypes(include=[np.number])
    )
    X = feat_df.to_numpy()
    feature_names = feat_df.columns.tolist()
    y = df["label"].values

    return X, y, df, order, feature_names


#  3. LOOCV grid-search for (lr, lam) with OVR 
def loo_tune(X, y, order, lrs=[1e-3,1e-2,1e-1], lams=[0.01,0.1,1,10]):
    loo = LeaveOneOut()
    best_score = -1
    best_params = None
    n = X.shape[0]

    for lr in lrs:
        for lam in lams:
            preds = np.zeros(n, dtype=int)
            for idx, (tr, te) in enumerate(loo.split(X)):
                # train OVR
                K = len(order)
                W = np.zeros((K, X.shape[1]))
                for k in range(K):
                    yk = (y[tr] == k).astype(int)
                    W[k] = gradient_ascent(X[tr], yk, lam, lr, max_iter=1000)
                # predict sample te
                x_te = X[te][0]
                scores = sigmoid(W.dot(x_te))
                preds[idx] = np.argmax(scores)
            acc = accuracy_score(y, preds)
            if acc > best_score:
                best_score = acc
                best_params = (lr, lam)
            print(f"LOOCV @ lr={lr}, lam={lam}  → acc={acc:.4f}")
    print(f"\n★ best LOOCV acc={best_score:.4f} @ lr,lam = {best_params}")
    return best_params

#  4. full train OVR on best params, report importances 
def train_final(X, y, order, lr, lam):
    K = len(order)
    W = np.zeros((K, X.shape[1]))
    for k in range(K):
        yk = (y==k).astype(int)
        W[k] = gradient_ascent(X, yk, lam, lr, max_iter=1000)
    return W

def build_bracket_for_year(df_all, predictor, order, year, feature_names):
    # filter to that year
    df_year = df_all[df_all["year"] == year].copy()

    # grab only numeric features, in the same order
    feat_df = (
        df_year
          .drop(columns=["year","team"])
          .select_dtypes(include=[np.number])
    )
    X_year = feat_df[feature_names].to_numpy()

    # get class‐prob scores shape (n_teams, K)
    if hasattr(predictor, "predict_proba"):
        probs = predictor.predict_proba(X_year)
    else:
        # predictor is W: shape (K, n_features)
        W = predictor
        probs = sigmoid(X_year.dot(W.T))

    # pick the class with highest probability
    pred_idx = np.argmax(probs, axis=1)

    # map back to labels
    df_year["pred_round"] = [order[i] for i in pred_idx]

    # collect survivors
    ord_map = {r:i for i,r in enumerate(order)}
    survivors = {
        "Sweet 16":  df_year[df_year.pred_round >= ord_map["Sweet Sixteen"]]["team"].tolist(),
        "Elite 8":   df_year[df_year.pred_round >= ord_map["Elite Eight"]]["team"].tolist(),
        "Final 4":   df_year[df_year.pred_round >= ord_map["Final Four"]]["team"].tolist(),
        "Finalists": df_year[df_year.pred_round >= ord_map["Runner-Up"]]["team"].tolist(),
        "Champion":  df_year[df_year.pred_round == ord_map["Champion"]]["team"].tolist(),
    }
    return survivors

def evaluate_ensembles(X, y, order):
    print("\n––– Ensemble Comparison (5-fold CV) –––")

    # 1) Random Forest
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        random_state=42,
        n_jobs=-1
    )
    rf_scores = cross_val_score(rf, X, y, cv=5, scoring='accuracy', n_jobs=-1)
    print(f"Random Forest 5-fold accuracy: {rf_scores.mean():.4f} ± {rf_scores.std():.4f}")
    rf.fit(X, y)
    y_rf = rf.predict(X)
    print("\nRF classification report:")
    print(classification_report(y, y_rf, target_names=order))

    # 2) Gradient Boosting
    gb = GradientBoostingClassifier(
        n_estimators=200,
        learning_rate=0.1,
        max_depth=3,
        random_state=42
    )
    gb_scores = cross_val_score(gb, X, y, cv=5, scoring='accuracy', n_jobs=-1)
    print(f"\nGradient Boosting 5-fold accuracy: {gb_scores.mean():.4f} ± {gb_scores.std():.4f}")
    gb.fit(X, y)
    y_gb = gb.predict(X)
    print("\nGB classification report:")
    print(classification_report(y, y_gb, target_names=order))

    return rf, gb


def main():
    # 1) load & prepare
    df_all = load_all_views("data", range(2008,2025+1))
    X, y, df_train, order, feature_names = attach_label(
        df_all, post_csv="data/trank_2008_2025_post.csv", max_year=2024
    )

    # 2) LOOCV tune & final logistic‐OVR
    lr, lam = loo_tune(X, y, order)
    W = train_final(X, y, order, lr, lam)

    # 3) ensemble comparison
    rf_model, gb_model = evaluate_ensembles(X, y, order)

    # 4) print original feature‐importances
    print("\nFeature importances per class (Logistic OVR):")
    for k, cls in enumerate(order):
        idx = np.argsort(np.abs(W[k]))[::-1][:10]
        print(f"\nTop features for '{cls}':")
        for i in idx:
            print(f"  {feature_names[i]:<30s} {W[k,i]:+.4f}")

    # 5) build & print three brackets: OVR, RF, GB
    print("\n=== Predicted bracket for 2025 (Logistic OVR) ===")
    surv_lr = build_bracket_for_year(df_all, W, order, 2025, feature_names)
    print("Sweet 16  :", surv_lr["Sweet 16"])
    print("Elite 8   :", surv_lr["Elite 8"])
    print("Final 4   :", surv_lr["Final 4"])
    print("Finalists :", surv_lr["Finalists"])
    print("Champion  :", surv_lr["Champion"])

    print("\n=== Predicted bracket for 2025 (Random Forest) ===")
    surv_rf = build_bracket_for_year(df_all, rf_model, order, 2025, feature_names)
    print("Sweet 16  :", surv_rf["Sweet 16"])
    print("Elite 8   :", surv_rf["Elite 8"])
    print("Final 4   :", surv_rf["Final 4"])
    print("Finalists :", surv_rf["Finalists"])
    print("Champion  :", surv_rf["Champion"])

    print("\n=== Predicted bracket for 2025 (Gradient Boosting) ===")
    surv_gb = build_bracket_for_year(df_all, gb_model, order, 2025, feature_names)
    print("Sweet 16  :", surv_gb["Sweet 16"])
    print("Elite 8   :", surv_gb["Elite 8"])
    print("Final 4   :", surv_gb["Final 4"])
    print("Finalists :", surv_gb["Finalists"])
    print("Champion  :", surv_gb["Champion"])

if __name__=="__main__":
    main()

