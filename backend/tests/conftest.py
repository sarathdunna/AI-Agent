import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import pytest


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "age": [25, 32, 47, 51, 23, 36, 29, 41, None, 60],
        "salary": [40000, 55000, 72000, 68000, 39000, 61000, 45000, 71000, 50000, 200000],
        "department": ["Sales", "Eng", "Eng", "Sales", "HR", "Eng", "Sales", "HR", "Eng", "Sales"],
        "churn": ["No", "No", "Yes", "No", "Yes", "No", "Yes", "No", "No", "Yes"],
    })
