# RMSE (Root Mean Squared Error)

RMSE measures the average magnitude of prediction errors in a regression
model, in the same units as the target variable.

Formula: RMSE = sqrt(mean((y_true - y_pred)^2))

RMSE penalizes large errors more heavily than MAE because errors are squared
before averaging. Lower RMSE indicates a better-fitting model.
