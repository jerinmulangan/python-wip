import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import BaggingClassifier


datasets = [
"_c300_d100", "_c300_d1000", "_c300_d5000", 
"_c500_d100", "_c500_d1000", "_c500_d5000", 
"_c1000_d100", "_c1000_d1000", "_c1000_d5000",
"_c1500_d100", "_c1500_d1000", "_c1500_d5000",
"_c1800_d100", "_c1800_d1000", "_c1800_d5000"
]



def load_dataset(file_prefix):
    print(f"Loading dataset: {file_prefix}")  # Debugging print
    train = pd.read_csv((f"train{file_prefix}.csv"), header=None)
    valid = pd.read_csv((f"valid{file_prefix}.csv"), header=None)
    test = pd.read_csv((f"test{file_prefix}.csv"), header=None)
    return train, valid, test

# Function to preprocess data (split into X and y)
def preprocess_data(df, dataset_name):
    print(f"Preprocessing dataset: {dataset_name}")  # Debugging print
    X = df.iloc[:, :-1]  # Features (all columns except last two)
    y = df.iloc[:, -1]   # Labels (second to last column)
    print(f"X shape: {X.shape}, y shape: {y.shape}")  # Check dimensions
    return X, y

# Hyperparameter grid
param_grid = {
    "criterion": ["gini", "entropy"],
    "max_depth": [5, 10, 20, 50, 100, None],
    "min_samples_split": [2, 5, 10, 20]
}

# Function to tune hyperparameters
def tune_hyperparameters(X_train, y_train, X_valid, y_valid):
    print("Starting hyperparameter tuning...")  # Debugging print
    clf = DecisionTreeClassifier()
    grid_search = GridSearchCV(clf, param_grid, cv=3, scoring="accuracy", n_jobs=-1)
    grid_search.fit(X_train, y_train)
    print(f"Best Params: {grid_search.best_params_}")  # Debugging print
    return grid_search.best_params_

# Define the base estimator
base_estimator = DecisionTreeClassifier()

# Define the parameter grid
param_grid_bagging = {
    'base_estimator__criterion': ['gini', 'entropy'],
    'base_estimator__max_depth': [5, 10, 20, None],
    'base_estimator__min_samples_split': [2, 5, 10],
    'n_estimators': [10, 50, 100],
    'max_samples': [0.5, 1.0],
    'max_features': [0.5, 1.0],
    'bootstrap': [True, False]
}

bagging_clf = BaggingClassifier(base_estimator=base_estimator, random_state=42)

grid_search_bagging = GridSearchCV(estimator=bagging_clf, param_grid=param_grid_bagging, cv=3, scoring='accuracy', n_jobs=-1)

# Fit GridSearchCV
grid_search_bagging.fit(X_train, y_train)

# Best parameters and corresponding accuracy
best_params_bagging = grid_search_bagging.best_params_
best_score_bagging = grid_search_bagging.best_score_

print(f"Best Parameters: {best_params_bagging}")
print(f"Best Cross-Validation Accuracy: {best_score_bagging:.4f}")


for dataset in datasets:
    train, valid, test = load_dataset(dataset)

    X_train, y_train = preprocess_data(train, f"{dataset} (Train)")
    X_valid, y_valid = preprocess_data(valid, f"{dataset} (Validation)")
    X_test, y_test = preprocess_data(test, f"{dataset} (Test)")

    best_params = tune_hyperparameters(X_train, y_train, X_valid, y_valid)

    clf = DecisionTreeClassifier(**best_params)
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"Dataset {dataset}: Best Params={best_params}, Accuracy={acc:.4f}, F1 Score={f1:.4f}")
    print("------------------------------")

    print("------------------------------")
    print(f"Bagging Classifier:")
    clf = BaggingClassifier(estimator=None, **best_params).fit(X_train, y_train)
    y_pred = clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")

    print(f"Dataset {dataset}: Best Params={best_params}, Accuracy={acc:.4f}, F1 Score={f1:.4f}")
    print("------------------------------")