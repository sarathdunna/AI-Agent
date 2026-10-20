from app.agents import profiling


def test_profile_basic(sample_df):
    result = profiling.profile_dataset(sample_df)
    assert result["n_rows"] == 10
    assert result["n_cols"] == 4
    assert "age" in result["numeric_columns"]
    assert "department" in result["categorical_columns"]
    age_info = next(c for c in result["columns"] if c["name"] == "age")
    assert age_info["missing_count"] == 1
