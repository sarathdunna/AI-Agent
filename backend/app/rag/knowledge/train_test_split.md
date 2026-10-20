# Train-Test Split

A train-test split divides a dataset into two parts: a training set used to
fit the model, and a test set held out to evaluate how well the model
generalizes to unseen data.

A common split ratio is 80% train / 20% test. For classification with
imbalanced classes, stratified splitting preserves class proportions in both
sets.

Never evaluate a model on data it was trained on — this gives an overly
optimistic and misleading performance estimate.
