# Overfitting

Overfitting occurs when a model learns the training data too well, including
its noise and random fluctuations, resulting in poor generalization to new,
unseen data.

Signs of overfitting: very high training accuracy/R2 but much lower
performance on a held-out test set.

Mitigations: simpler models, regularization (Ridge/Lasso), cross-validation,
more training data, early stopping, pruning decision trees, ensembling.
