import pandas as pd

from app.agents.cleaning import CleaningStep, apply_cleaning


def test_drop_duplicates():
    df = pd.DataFrame({"a": [1, 1, 2], "b": [1, 1, 2]})
    cleaned, log = apply_cleaning(df, [CleaningStep(action="drop_duplicates")])
    assert len(cleaned) == 2
    assert log[0]["action"] == "drop_duplicates"


def test_fill_missing_mean(sample_df):
    cleaned, log = apply_cleaning(sample_df, [CleaningStep(action="fill_missing", columns=["age"], strategy="mean")])
    assert cleaned["age"].isna().sum() == 0


def test_handle_outliers_clip(sample_df):
    cleaned, log = apply_cleaning(sample_df, [CleaningStep(action="handle_outliers", columns=["salary"], strategy="iqr_clip")])
    assert cleaned["salary"].max() < sample_df["salary"].max()


def test_original_never_mutated(sample_df):
    original_copy = sample_df.copy()
    apply_cleaning(sample_df, [CleaningStep(action="drop_duplicates")])
    pd.testing.assert_frame_equal(sample_df, original_copy)
