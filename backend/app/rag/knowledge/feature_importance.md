# Feature Importance

Feature importance quantifies how much each input feature contributes to a
model's predictions.

Tree-based models (Random Forest, Gradient Boosting) expose
`feature_importances_` directly. Linear models use the magnitude of their
coefficients. For models without a native importance measure, permutation
importance can be used: it shuffles one feature at a time and measures how
much performance drops.

Feature importance helps with model interpretability and can guide feature
selection.
