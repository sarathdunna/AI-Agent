import pandas as pd
import pytest

from app.agents.sql_agent import run_sql
from app.utils.security import UnsafeSQLError, validate_readonly_sql


@pytest.fixture
def df():
    return pd.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})


@pytest.mark.parametrize("bad_sql", [
    "DROP TABLE data",
    "DELETE FROM data",
    "UPDATE data SET a = 1",
    "INSERT INTO data VALUES (1, 'x')",
    "ALTER TABLE data ADD COLUMN c INT",
    "TRUNCATE data",
    "ATTACH 'evil.db' AS evil",
    "COPY data TO 'out.csv'",
    "SELECT * FROM data; DROP TABLE data",
    "",
])
def test_unsafe_sql_rejected(bad_sql, df):
    with pytest.raises(UnsafeSQLError):
        run_sql(bad_sql, df)


@pytest.mark.parametrize("good_sql", [
    "SELECT * FROM data",
    "SELECT a, COUNT(*) FROM data GROUP BY a",
    "WITH t AS (SELECT * FROM data) SELECT * FROM t",
])
def test_safe_sql_allowed(good_sql, df):
    validate_readonly_sql(good_sql)  # should not raise
    result = run_sql(good_sql, df)
    assert "rows" in result
