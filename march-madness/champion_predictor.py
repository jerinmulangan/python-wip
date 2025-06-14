#!/usr/bin/env python3

from pathlib import Path
import re

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import LeaveOneOut, cross_val_predict
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score

from lightgbm import LGBMClassifier

PRE_MASTER       = Path("data/trank_2008_2025_pre.csv")
POST_MASTER      = Path("data/trank_2008_2025_post.csv")
PRE_2025         = Path("data/pre2025.csv")
# (post-tourney 2025 rows are in POST_MASTER when year==2025)
RANDOM_SEED      = 42
TOP_N            = 20

df_pre  = pd.read_csv(PRE_MASTER)
df_post = pd.read_csv(POST_MASTER)
df_pre["snapshot"]  = "pre"
df_post["snapshot"] = "post"
df_all = pd.concat([df_pre, df_post], ignore_index=True)

df_all["champion"] = (
    (df_all.snapshot == "post") &
    (df_all.tourney_res.str.upper() == "CHAMPS")
).astype(int)

NUM_RE = re.compile(r"([-+]?\d*\.?\d+)")
def first_number(x):
    if pd.isna(x): return np.nan
    m = NUM_RE.search(str(x))
    return float(m.group(1)) if m else np.nan

def win_pct(rec):
    try:
        w, l = map(int, str(rec).split("-"))
        return w / (w + l)
    except:
        return np.nan

def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    skip = {"team","conf","tourney_res","snapshot","year","champion","rk","seed"}
    for c in df.columns:
        if c in skip:
            continue
        df[c] = df[c].map(first_number)
    if "rec" in df.columns:
        df["win_pct"] = df["rec"].map(win_pct)
        df.drop(columns=["rec"], inplace=True)
    return df

df_all = preprocess(df_all)

train = df_all[df_all.year < 2025].reset_index(drop=True)

# Pre-tourney 2025 snapshot
test_pre = pd.read_csv(PRE_2025).pipe(preprocess)
test_pre["snapshot"] = "pre"

# Full-season 2025 (post rows from master)
test_post = df_all[
    (df_all.year == 2025) &
    (df_all.snapshot == "post")
].reset_index(drop=True)

y_train   = train["champion"].values
# drop only non-features: keep 'conf'
drop_cols = ["team","tourney_res","year","rk","champion"]

X_train   = train.drop(columns=drop_cols)

def build_X(df_t):
    X = df_t.drop(columns=drop_cols, errors="ignore")
    # align to training columns
    for c in X_train.columns:
        if c not in X.columns:
            X[c] = np.nan
    return X[X_train.columns]

X_test_pre  = build_X(test_pre)
X_test_post = build_X(test_post)

cat_cols = ["conf","snapshot"]
num_cols = [c for c in X_train.columns if c not in cat_cols]

preprocessor = ColumnTransformer([
    ("num", Pipeline([
        ("imp", SimpleImputer(strategy="median")),
        ("sc",  StandardScaler())
    ]), num_cols),
    ("cat", OneHotEncoder(handle_unknown="ignore"), cat_cols),
])

lgb = LGBMClassifier(
    n_estimators=1000,
    learning_rate=0.03,
    num_leaves=31,
    class_weight="balanced",
    random_state=RANDOM_SEED,
    n_jobs=-1,
)

# use positional estimator argument (no base_estimator)
clf = CalibratedClassifierCV(lgb, cv=3, method="isotonic")

model = Pipeline([
    ("prep", preprocessor),
    ("clf",  clf),
])

loo      = LeaveOneOut()
probs_cv = cross_val_predict(
    model, X_train, y_train, cv=loo, method="predict_proba"
)[:, 1]
preds_cv = (probs_cv >= 0.5).astype(int)

print("\nLOOCV (2008–2024) with Calibrated LGBM:")
print(classification_report(y_train, preds_cv, zero_division=0))
print("ROC-AUC :", roc_auc_score(y_train, probs_cv).round(3))
print("PR-AUC  :", average_precision_score(y_train, probs_cv).round(3))

model.fit(X_train, y_train)

def show(df_t, X_t, title):
    probs = model.predict_proba(X_t)[:, 1]
    out   = df_t.copy()
    out["champ_prob"] = probs
    print(f"\n{title} top {TOP_N}:")
    print(
        out[["team","seed","conf","rk","snapshot","champ_prob"]]
        .sort_values("champ_prob", ascending=False)
        .head(TOP_N)
        .to_string(index=False, formatters={"champ_prob":"{:.4f}".format})
    )
    out.to_csv(f"data/{title.replace(' ', '_')}_champ_probs.csv", index=False)

show(test_pre,  X_test_pre,  "Pre-tourney_2025")
show(test_post, X_test_post, "Full-season_2025")
