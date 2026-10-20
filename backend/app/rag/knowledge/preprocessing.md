# Preprocessing

Preprocessing transforms raw data into a format suitable for machine learning
models.

Typical steps: handling missing values (imputation), encoding categorical
variables (one-hot encoding), scaling numeric features (standardization), and
outlier handling.

Best practice: fit all preprocessing steps only on the training data, then
apply the same transformation to the test data, to avoid data leakage.
scikit-learn's ColumnTransformer and Pipeline make this easy and safe.
