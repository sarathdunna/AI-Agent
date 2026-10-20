# Cross-Validation

Cross-validation is a technique for more robustly estimating model
performance by splitting the data into k folds, training on k-1 folds, and
validating on the remaining fold, repeated k times.

k-fold cross-validation reduces the variance of the performance estimate
compared to a single train-test split, and is especially useful with smaller
datasets. It is commonly used during hyperparameter tuning (e.g.
GridSearchCV, RandomizedSearchCV).
