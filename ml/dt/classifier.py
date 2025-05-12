import os
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score, f1_score

datasets = [
    "_c300_d100", "_c300_d1000", "_c300_d5000",
    "_c500_d100", "_c500_d1000", "_c500_d5000",
    "_c1000_d100", "_c1000_d1000", "_c1000_d5000",
    "_c1500_d100", "_c1500_d1000", "_c1500_d5000",
    "_c1800_d100", "_c1800_d1000", "_c1800_d5000"
]

#Load datasets
def load_dataset(file_prefix):
    print(f"Loading dataset: {file_prefix}") 
    train = pd.read_csv(f"train{file_prefix}.csv", header=None)
    valid = pd.read_csv(f"valid{file_prefix}.csv", header=None)
    test = pd.read_csv(f"test{file_prefix}.csv", header=None)
    return train, valid, test

#Preprocess data, features are all columns except last one, which is labels, print check for shape
def preprocess_data(df, dataset_name):
    print(f"Preprocessing dataset: {dataset_name}")
    X = df.iloc[:, :-1]  
    y = df.iloc[:, -1]  
    print(f"X shape: {X.shape}, y shape: {y.shape}") 
    return X, y

#Hyperparameter Grid, changed to include more options in tuning (originally fewer options)
param_grid = {
    "criterion": ["gini", "entropy"],
    "max_depth": [5, 10, 20, 50, 100, None],
    "min_samples_split": [2, 5, 10, 20]
}

#Use grid search to tune hyperparameters, given criterion, max_depth and min_samples_split from above
def tune_hyperparameters(X_train, y_train):
    #Print Line to make sure code is running here
    print("Starting hyperparameter tuning...")
    #Set Random State to 0 to ensure reproducibility when running the code again to double-check
    clf = DecisionTreeClassifier(random_state=0)
    #Cross-validation set to 3, train on 2/3 of data, test on rest
    #Set n_jobs=-1 to boost CPU performance
    grid_search = GridSearchCV(clf, param_grid, cv=3, scoring="accuracy", n_jobs=-1)
    grid_search.fit(X_train, y_train)
    print(f"Best Params: {grid_search.best_params_}")
    return grid_search.best_params_

for dataset in datasets:
    #Load, preprocess data and tune hyperparameters and store in X_train, y_train, etc.
    train, valid, test = load_dataset(dataset)

    X_train, y_train = preprocess_data(train, f"{dataset} (Train)")
    X_valid, y_valid = preprocess_data(valid, f"{dataset} (Validation)")
    X_test, y_test = preprocess_data(test, f"{dataset} (Test)")

    best_params = tune_hyperparameters(X_train, y_train)

    #Decision Tree
    dt_clf = DecisionTreeClassifier(**best_params)
    dt_clf.fit(X_train, y_train)
    y_pred = dt_clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    print("------------------------------")
    print(f"Dataset {dataset} - Decision Tree: Best Params={best_params}, Accuracy={acc:.4f}, F1 Score={f1:.4f}")
    print("------------------------------")

    #Bagging
    bagging_clf = BaggingClassifier(estimator=dt_clf, n_estimators=100, random_state=0)
    bagging_clf.fit(X_train, y_train)
    y_pred = bagging_clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    print(f"Dataset {dataset} - Bagging Classifier: Accuracy={acc:.4f}, F1 Score={f1:.4f}")
    print("------------------------------")

    #Random Forest
    randomForest_clf = RandomForestClassifier(n_estimators=1000, random_state=0)
    randomForest_clf.fit(X_train, y_train)
    y_pred = randomForest_clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    print(f"Dataset {dataset} - Random Forest Classifier: Accuracy={acc:.4f}, F1 Score={f1:.4f}")
    print("------------------------------")

    #Gradient Boosting
    gradientBosting_clf = GradientBoostingClassifier(n_estimators=1000, random_state=0)
    gradientBosting_clf.fit(X_train, y_train)
    y_pred = gradientBosting_clf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred, average="weighted")
    print(f"Dataset {dataset} - Gradient Boosting Classifier: Accuracy={acc:.4f}, F1 Score={f1:.4f}")
    print("------------------------------")

