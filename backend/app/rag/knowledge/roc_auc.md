# ROC-AUC

ROC-AUC (Area Under the Receiver Operating Characteristic Curve) measures a
classifier's ability to distinguish between classes across all possible
decision thresholds.

The ROC curve plots the true positive rate against the false positive rate at
various thresholds. AUC ranges from 0.5 (no better than random guessing) to
1.0 (perfect separation). ROC-AUC is threshold-independent, making it useful
for comparing models regardless of the chosen classification cutoff.
