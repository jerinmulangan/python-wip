import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def load_data(dataset, representation):
    train_df = pd.read_csv(f"{dataset}_{representation}_train.csv")
    test_df = pd.read_csv(f"{dataset}_{representation}_test.csv")

    y_train = train_df["label"].values
    X_train = train_df.drop(columns=["label"]).values
    
    y_test = test_df["label"].values
    X_test = test_df.drop(columns=["label"]).values

    return X_train, y_train, X_test, y_test

def sigmoid(z):
    z = np.clip(z, -500, 500)
    return 1 / (1 + np.exp(-z))

def compute_log_likelihood(X, y, weights, lambd):
    z = np.dot(X, weights)
    z = np.clip(z, -500, 500)
    return np.sum(y * z - np.log(1 + np.exp(z))) - (lambd / 2) * np.sum(weights ** 2)

def gradient_ascent(X, y, lambd, learning_rate=0.01, max_iter=1000):
    n_samples, n_features = X.shape
    weights = np.zeros(n_features)
    
    for iteration in range(max_iter):
        z = np.dot(X, weights)
        predictions = sigmoid(z)
        gradient = np.dot(X.T, (y - predictions)) - lambd * weights
        weights += learning_rate * gradient
        if iteration % 100 == 0:
            print(f"Iteration {iteration}: Log-Likelihood = {compute_log_likelihood(X, y, weights, lambd):.4f}")
    
    return weights

def tune_hyperparameter(X_train, y_train, X_val, y_val, lambdas=[0.01, 0.1, 1, 10]):
    best_lambda, best_f1 = None, -1
    for lambd in lambdas:
        print(f"\nTraining with λ = {lambd}")
        weights = gradient_ascent(X_train, y_train, lambd)
        predictions = sigmoid(np.dot(X_val, weights)) >= 0.5
        f1 = f1_score(y_val, predictions)
        print(f"F1-score for λ={lambd}: {f1:.4f}")
        if f1 > best_f1:
            best_f1, best_lambda = f1, lambd
    
    print(f"\nBest λ: {best_lambda} with F1-score: {best_f1:.4f}")
    return best_lambda

def evaluate_model(y_true, y_pred, dataset_name, representation):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    print(f"\nResults for {dataset_name} ({representation} representation):")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-score: {f1:.4f}")

def process_dataset(dataset_name):
    results = {}
    for representation in ["bow", "bernoulli"]:
        X_train, y_train, X_test, y_test = load_data(dataset_name, representation)
        X_train_full, X_val, y_train_full, y_val = train_test_split(X_train, y_train, test_size=0.3)
        best_lambda = tune_hyperparameter(X_train_full, y_train_full, X_val, y_val)
        final_weights = gradient_ascent(X_train, y_train, best_lambda)
        y_pred = sigmoid(np.dot(X_test, final_weights)) >= 0.5
        evaluate_model(y_test, y_pred, dataset_name, representation)
        results[representation] = (y_test, y_pred)
    return results

def main():
    datasets = ["enron1", "enron2", "enron4"]
    for dataset in datasets:
        print(f"\nProcessing dataset: {dataset}")
        process_dataset(dataset)

if __name__ == "__main__":
    main()
