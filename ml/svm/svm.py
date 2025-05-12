from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV, StratifiedKFold
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import joblib


def load_data(train_size=10000, test_size=10000, random_state=42):
    # Fetch MNIST
    mnist = fetch_openml('mnist_784', version=1, as_frame=False)
    X, y = mnist.data, mnist.target.astype(int)
    # Stratified split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        train_size=train_size, test_size=test_size,
        random_state=random_state, stratify=y
    )
    return X_train, X_test, y_train, y_test

def run_grid_search(X, y):
    cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=0)
    param_grid = [
        # linear kernel
        {'kernel': ['linear'], 'C': [0.1, 1, 10]},
        # polynomial kernel
        {'kernel': ['poly'], 'C': [0.1, 1, 10], 'degree': [2, 3, 4]},
        # RBF kernel
        {'kernel': ['rbf'], 'C': [0.1, 1, 10], 'gamma': ['scale', 0.01, 0.001]}
    ]
    svc = SVC()
    grid = GridSearchCV(
        svc, param_grid,
        cv=cv, scoring='accuracy',
        return_train_score=False, n_jobs=-1, verbose=2
    )
    grid.fit(X, y)
    # collect results
    results = pd.DataFrame(grid.cv_results_)[[
        'param_kernel', 'param_C', 'param_degree', 'param_gamma',
        'mean_test_score', 'std_test_score'
    ]]
    return grid, results

def plot_results(results: pd.DataFrame, out_png='cv_results.png'):
    # Pivot table for each kernel vs C
    for kern in results.param_kernel.unique():
        dfk = results[results.param_kernel == kern]
        plt.figure(figsize=(6,4))
        if kern == 'linear':
            plt.errorbar(dfk.param_C, dfk.mean_test_score, yerr=dfk.std_test_score, marker='o')
            plt.title(f'Linear kernel CV')
            plt.xlabel('C')
        elif kern == 'poly':
            for deg in sorted(dfk.param_degree.unique()):
                sub = dfk[dfk.param_degree==deg]
                plt.errorbar(sub.param_C, sub.mean_test_score, yerr=sub.std_test_score, marker='o', label=f'deg={deg}')
            plt.title('Poly kernel CV')
            plt.xlabel('C'); plt.legend()
        else:  # rbf
            # plot separate series per gamma
            for g in dfk.param_gamma.unique():
                sub = dfk[dfk.param_gamma==g]
                plt.errorbar(sub.param_C, sub.mean_test_score, yerr=sub.std_test_score, marker='o', label=f'γ={g}')
            plt.title('RBF kernel CV')
            plt.xlabel('C'); plt.legend()
        plt.ylabel('Accuracy'); plt.xscale('log')
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f'{kern}_{out_png}')
    print("Plots saved.")

def main():
    # 1. Load data
    X_train, X_test, y_train, y_test = load_data()
    print(f'Training samples: {X_train.shape}, Testing samples: {X_test.shape}')

    # 2. Grid search + CV
    grid, results = run_grid_search(X_train, y_train)
    results.to_csv('cv_results.csv', index=False)
    print("CV complete. Best params:", grid.best_params_)
    print(f'Best CV accuracy: {grid.best_score_:.4f}')

    # 3. Plot
    plot_results(results)

    # 4. Final evaluation
    best_clf: SVC = grid.best_estimator_
    y_pred = best_clf.predict(X_test)
    test_acc = accuracy_score(y_test, y_pred)
    print(f'Test accuracy: {test_acc:.4f}')

    # 5. Save model & test results
    joblib.dump(best_clf, 'best_svm_mnist.pkl')
    with open('test_accuracy.txt', 'w') as f:
        f.write(f'{test_acc:.4f}\n')

if __name__ == '__main__':
    main()


