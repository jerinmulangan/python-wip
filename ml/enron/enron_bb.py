import os
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string
from collections import Counter

nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    text = str(text).lower() 
    text = text.translate(str.maketrans('', '', string.punctuation)) 
    tokens = word_tokenize(text) 
    stop_words = set(stopwords.words('english')) 
    tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
    return tokens


def load_emails_from_folder(folder_path):
    emails = []
    print(f"Checking folder: {folder_path}") 
    if not os.path.exists(folder_path):
        print(f"Error: Path not found {folder_path}")
        return emails
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        if file.endswith(".txt"):  
            try:
                with open(file_path, "r", encoding="latin1") as f:  
                    email_text = f.read().strip() 
                    emails.append(email_text) 
            except Exception as e:
                print(f"Error reading {file}: {e}") 
    print(f"Loaded {len(emails)} emails from {folder_path}") 
    return emails

def build_vocabulary(emails):
    vocab_counter = Counter()
    for email in emails:
        tokens = preprocess_text(email)
        vocab_counter.update(tokens)
    vocab = sorted(vocab_counter.keys()) 
    print(f"Vocabulary size: {len(vocab)}")
    print(f"Sample vocabulary words: {vocab[:20]}") 
    return vocab



def generate_feature_matrix(emails, vocab, representation):
    feature_matrix = []
    print(f"\nGenerating {representation} feature matrix...")
    vocab_set = set(vocab)
    for email in emails:
        tokens = preprocess_text(email)
        token_counts = Counter(tokens)
        if representation == "bow":
            row = [token_counts[word] if word in vocab_set else 0 for word in vocab]
        elif representation == "bernoulli":
            row = [1 if word in token_counts else 0 for word in vocab]
        feature_matrix.append(row)
    empty_rows = sum(1 for row in feature_matrix if sum(row) == 0)
    print(f"Total emails processed: {len(feature_matrix)} | Empty feature rows: {empty_rows}")
    return feature_matrix


def process_dataset(dataset_name, dataset_path):
    train_ham_path = os.path.join(dataset_path, "train", "ham")
    train_spam_path = os.path.join(dataset_path, "train", "spam")
    test_ham_path = os.path.join(dataset_path, "test", "ham")
    test_spam_path = os.path.join(dataset_path, "test", "spam")
    train_ham = load_emails_from_folder(train_ham_path)
    train_spam = load_emails_from_folder(train_spam_path)
    test_ham = load_emails_from_folder(test_ham_path)
    test_spam = load_emails_from_folder(test_spam_path)
    train_emails = train_ham + train_spam
    train_labels = [0] * len(train_ham) + [1] * len(train_spam)
    test_emails = test_ham + test_spam
    test_labels = [0] * len(test_ham) + [1] * len(test_spam)
    vocab = build_vocabulary(train_emails)

    for representation in ["bow", "bernoulli"]:
        train_features = generate_feature_matrix(train_emails, vocab, representation)
        test_features = generate_feature_matrix(test_emails, vocab, representation)
        train_df = pd.DataFrame(train_features, columns=vocab)
        test_df = pd.DataFrame(test_features, columns=vocab)
        print(f"train_df shape: {train_df.shape} | Expected rows: {len(train_labels)}")
        print(f"test_df shape: {test_df.shape} | Expected rows: {len(test_labels)}")
        if len(train_df) != len(train_labels):
            print("ERROR: train_df and train_labels length mismatch! Fixing...")
            train_df = train_df.iloc[:len(train_labels)] 
        if len(test_df) != len(test_labels):
            print("ERROR: test_df and test_labels length mismatch! Fixing...")
            test_df = test_df.iloc[:len(test_labels)]
        train_df['label'] = train_labels
        test_df['label'] = test_labels
        train_df.to_csv(f"{dataset_name}_{representation}_train.csv", index=False)
        test_df.to_csv(f"{dataset_name}_{representation}_test.csv", index=False)

dataset_paths = {
    "enron1": "./enron1",
    "enron2": "./enron2",
    "enron4": "./enron4"
}

for dataset_name, dataset_path in dataset_paths.items():
    process_dataset(dataset_name, dataset_path)
