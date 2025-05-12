import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def load_data(dataset="enron1", representation="bernoulli"):
    train_df = pd.read_csv(f"{dataset}_{representation}_train.csv")
    test_df = pd.read_csv(f"{dataset}_{representation}_test.csv")
    y_train = train_df["label"].values
    X_train = train_df.drop(columns=["label"]).values
    y_test = test_df["label"].values
    X_test = test_df.drop(columns=["label"]).values 
    return X_train, y_train, X_test, y_test


X_train, y_train, X_test, y_test = load_data(dataset="enron1", representation="bernoulli")

def log_add_one_laplace_smoothing(X, y, num_classes):
    n_samples, n_features = X.shape
    log_likelihood = np.zeros((num_classes, n_features))
    log_class_prob = np.zeros(num_classes)
    for c in range(num_classes):
        log_class_prob[c] = np.log(np.sum(y == c) / n_samples)
    for c in range(num_classes):
        class_docs = X[y == c]
        word_counts = np.sum(class_docs, axis=0) + 1 
        log_likelihood[c] = np.log(word_counts / (np.sum(word_counts) + n_features))  
    return log_likelihood, log_class_prob

def predict(X, log_likelihood, log_class_prob):
    log_posteriors = np.dot(X, log_likelihood.T) + log_class_prob
    return np.argmax(log_posteriors, axis=1)

def evaluate_model(y_true, y_pred):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    print(f"\nTest Set Performance:")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-score: {f1:.4f}")

num_classes = len(np.unique(y_train))
log_likelihood, log_class_prob = log_add_one_laplace_smoothing(X_train, y_train, num_classes)
y_pred = predict(X_test, log_likelihood, log_class_prob)
evaluate_model(y_test, y_pred)
