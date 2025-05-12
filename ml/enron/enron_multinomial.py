import numpy as np
import pandas as pd
import os
from collections import Counter
from math import log
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

def train_multinomial_nb(X_train, y_train):
    vocab = list(X_train.columns)
    classes = np.unique(y_train) 

    N = len(y_train)
    prior = {}
    condprob = {}
    for c in classes:
        class_docs = X_train[y_train == c]
        Nc = len(class_docs)  
        prior[c] = Nc / N
        textc = class_docs.sum(axis=0)
        total_terms = textc.sum()
        condprob[c] = (textc + 1) / (total_terms + len(vocab))
    return vocab, prior, condprob

def apply_multinomial_nb(vocab, prior, condprob, X_test):
    classes = list(prior.keys()) 
    y_pred = []
    for i in range(X_test.shape[0]):
        W = X_test.iloc[i]
        scores = {}
        for c in classes:
            scores[c] = log(prior[c])
            for t in vocab:
                if W[t] > 0:
                    scores[c] += W[t] * log(condprob[c][t])
        y_pred.append(max(scores, key=scores.get))
    return y_pred

def load_all_data():
    datasets = ["enron1", "enron2", "enron4"]
    data = {}
    for dataset in datasets:
        X_train = pd.read_csv(f"{dataset}_bow_train.csv")
        y_train = X_train["label"]
        X_train = X_train.drop(columns=["label"])
        X_test = pd.read_csv(f"{dataset}_bow_test.csv")
        y_test = X_test["label"]
        X_test = X_test.drop(columns=["label"])
        data[dataset] = (X_train, y_train, X_test, y_test)
    return data

def evaluate_model(y_true, y_pred, dataset_name):
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred)
    rec = recall_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred)
    print(f"\nResults for {dataset_name}")
    print(f"Accuracy: {acc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall: {rec:.4f}")
    print(f"F1-score: {f1:.4f}")


data = load_all_data()
for dataset_name, (X_train, y_train, X_test, y_test) in data.items():
    print(f"\nTraining on {dataset_name} dataset")
    vocab, prior, condprob = train_multinomial_nb(X_train, y_train)
    y_pred = apply_multinomial_nb(vocab, prior, condprob, X_test)
    evaluate_model(y_test, y_pred, dataset_name)


X_train, y_train, X_test, y_test = load_all_data()
vocab, prior, condprob = train_multinomial_nb(X_train, y_train)
y_pred = apply_multinomial_nb(vocab, prior, condprob, X_test)

evaluate_model(y_test, y_pred)
