from sklearn.datasets import fetch_openml
from sklearn.model_selection import train_test_split

from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score

# Load MNIST dataset
X, y = fetch_openml('mnist_784', version=1, return_X_y=True)
X = X / 255.0 # Normalize pixel values to [0,1]
# Split into training (60K) and test (10K) sets
X_train, X_test = X[:60000], X[60000:]
y_train, y_test = y[:60000], y[60000:]

param_grid = {
    "criterion": ["gini", "entropy"],
    "max_depth": [5, 10, 20, 50, 100, None],
    "min_samples_split": [2, 5, 10, 20]
}

#Tune the hyperparameters for the next steps
def tune_hyperparameters(X_train, y_train):
    #Print Line to follow step
    print("Starting hyperparameter tuning...")
    #Set Random State to 0 to ensure reproducibility when running the code again to double-check
    clf = DecisionTreeClassifier(random_state=0)
    #Cross-validation set to 3, train on 2/3 of data, test on rest
    #Set n_jobs=-1 to boost CPU performance
    grid_search = GridSearchCV(clf, param_grid, cv=3, scoring="accuracy", n_jobs=-1)
    grid_search.fit(X_train, y_train)
    #Print the best parameters
    print(f"Best Params: {grid_search.best_params_}")
    return grid_search.best_params_

#Function call to actually tune and store hyperparameters
best_params = tune_hyperparameters(X_train, y_train)

#Train the Decision Tree on the hyperparameters
#Fit and Predict the data and store the accuracy on the test set
dt_clf = DecisionTreeClassifier(**best_params)
dt_clf.fit(X_train, y_train)
y_pred = dt_clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
#F1 score not needed
#f1 = f1_score(y_test, y_pred, average="weighted")
print("------------------------------")
print(f"MNIST - Decision Tree: Best Params={best_params}, Accuracy={acc:.4f}")
print("------------------------------")

#Same as above, train the Bagging Method
#Fit and Predict the data and store the accuracy on the test set
bagging_clf = BaggingClassifier(estimator=dt_clf, n_estimators=100, random_state=0)
bagging_clf.fit(X_train, y_train)
y_pred = bagging_clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
#F1 score not needed
#f1 = f1_score(y_test, y_pred, average="weighted")
print(f"MNIST - Bagging Classifier: Accuracy={acc:.4f}")
print("------------------------------")

#Random Forest
#Fit and Predict the data and store the accuracy on the test set
randomForest_clf = RandomForestClassifier(n_estimators=1000, random_state=0)
randomForest_clf.fit(X_train, y_train)
y_pred = randomForest_clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
#F1 score not needed
#f1 = f1_score(y_test, y_pred, average="weighted")
print(f"MNIST - Random Forest Classifier: Accuracy={acc:.4f}")
print("------------------------------")

#Gradient Boosting
#Fit and Predict the data and store the accuracy on the test set
#Setting n_estimators to 1000 here may have been overkill
gradientBosting_clf = GradientBoostingClassifier(n_estimators=1000, random_state=0)
gradientBosting_clf.fit(X_train, y_train)
y_pred = gradientBosting_clf.predict(X_test)
acc = accuracy_score(y_test, y_pred)
#F1 score not needed
#f1 = f1_score(y_test, y_pred, average="weighted")
print(f"MNIST - Gradient Boosting Classifier: Accuracy={acc:.4f}")
print("------------------------------")


    