import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split, StratifiedKFold, ParameterGrid
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

mnist = fetch_openml('mnist_784', version=1, as_frame=False)
X, y = mnist.data, mnist.target.astype(int)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, train_size=10000, test_size=10000,
    random_state=42, stratify=y
)
print(f"Training samples: {X_train.shape}, Testing samples: {X_test.shape}\n")

# setting up the parameter grid
param_grid = [
    {'kernel': ['linear'], 'C': [0.1, 1, 10]},
    {'kernel': ['poly'],   'C': [0.1, 1, 10], 'degree': [2, 3, 4]},
    {'kernel': ['rbf'],    'C': [0.1, 1, 10], 'gamma': ['scale', 0.01, 0.001]}
]
grid = list(ParameterGrid(param_grid))
cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=0)

# for gridsearchcv, setting params for grid
records = []
for params in grid:
    k    = params['kernel']
    C    = params['C']
    deg  = params.get('degree', None)
    g    = params.get('gamma', None)
    print(f"=== Kernel={k}, C={C}"
          + (f", degree={deg}" if deg  is not None else "")
          + (f", gamma={g}" if g   is not None else "") + " ===")
    #printing fold scores for each fold
    fold_scores = []
    for fold_idx, (tr_idx, val_idx) in enumerate(cv.split(X_train, y_train), start=1):
        X_tr, y_tr = X_train[tr_idx], y_train[tr_idx]
        X_val, y_val = X_train[val_idx], y_train[val_idx]
        print(f" Fold {fold_idx}: train={len(tr_idx)}, val={len(val_idx)}")

        clf = SVC(**params)
        clf.fit(X_tr, y_tr)
        acc = clf.score(X_val, y_val)
        print(f"  → Fold {fold_idx} acc = {acc:.4f}")

        fold_scores.append(acc)
        records.append({
            'kernel': k,
            'C':       C,
            'degree':  deg,
            'gamma':   g,
            'fold':    fold_idx,
            'accuracy':acc
        })

    mean_score = np.mean(fold_scores)
    std_score  = np.std(fold_scores, ddof=1)
    print(f" Completed → mean = {mean_score:.4f}, std = {std_score:.4f}\n")

# printing all fold results together so uts easier to see
df = pd.DataFrame(records)
print("=== All fold results ===")
print(df.to_string(index=False, na_rep='-'))

# graphing stuff
#linear graph
lin = df[df.kernel=='linear']
plt.figure(figsize=(6,4))
for C_val in sorted(lin.C.unique()):
    sub = lin[lin.C==C_val]
    plt.scatter([C_val]*len(sub), sub.accuracy, label=f'C={C_val}')
plt.xscale('log')
plt.title('Linear kernel — all fold accuracies')
plt.xlabel('C'); plt.ylabel('Accuracy'); plt.legend(); plt.grid(True)
plt.show()

# poly by deg graph
poly = df[df.kernel=='poly']
for deg in sorted(poly.degree.unique()):
    subdeg = poly[poly.degree==deg]
    plt.figure(figsize=(6,4))
    for C_val in sorted(subdeg.C.unique()):
        sub = subdeg[subdeg.C==C_val]
        plt.scatter([C_val]*len(sub), sub.accuracy, label=f'C={C_val}')
    plt.xscale('log')
    plt.title(f'Poly kernel (degree={deg}) — fold accuracies')
    plt.xlabel('C'); plt.ylabel('Accuracy'); plt.legend(); plt.grid(True)
    plt.show()

# rbf gamma
rbf = df[df.kernel=='rbf']
for gamma_val in rbf.gamma.unique():
    subg = rbf[rbf.gamma==gamma_val]
    plt.figure(figsize=(6,4))
    for C_val in sorted(subg.C.unique()):
        sub = subg[subg.C==C_val]
        plt.scatter([C_val]*len(sub), sub.accuracy, label=f'C={C_val}')
    plt.xscale('log')
    plt.title(f'RBF kernel (gamma={gamma_val}) — fold accuracies')
    plt.xlabel('C'); plt.ylabel('Accuracy'); plt.legend(); plt.grid(True)
    plt.show()

# test best result model on test
#print best model and its accuracy
agg = df.groupby(['kernel','C','degree','gamma']).accuracy.mean().reset_index()
best = agg.loc[agg['accuracy'].idxmax()]
print("Best CV setting:", best.to_dict())

best_params = {'kernel': best.kernel, 'C': best.C}
if best.kernel == 'poly':
    best_params['degree'] = int(best.degree)
if best.kernel == 'rbf':
    best_params['gamma'] = best.gamma

final_clf = SVC(**best_params)
final_clf.fit(X_train, y_train)
test_acc = accuracy_score(y_test, final_clf.predict(X_test))
print(f"Test-set accuracy of best model: {test_acc:.4f}")
