"""Security helpers: safe filenames, path traversal protection, SQL allowlist enforcement."""
import re
import uuid
from pathlib import Path

SAFE_NAME_RE = re.compile(r"[^A-Za-z0-9_.-]")

# Only these statement-starting keywords are allowed. Anything else is rejected.
ALLOWED_SQL_START = {"select", "with"}

# Hard blocklist as defense-in-depth (checked as whole-word anywhere in the query).
FORBIDDEN_SQL_KEYWORDS = {
    "drop", "delete", "update", "insert", "alter", "truncate", "attach", "detach",
    "copy", "create", "replace", "grant", "revoke", "pragma", "call", "exec",
    "execute", "vacuum", "export", "import",
}


def safe_filename(filename: str) -> str:
    """Strip directory components and unsafe characters; prefix with a uuid to avoid collisions."""
    base = Path(filename).name  # drops any directory / path traversal components
    base = SAFE_NAME_RE.sub("_", base)
    if not base:
        base = "file"
    return f"{uuid.uuid4().hex}_{base}"


def resolve_within(base_dir: Path, filename: str) -> Path:
    """Resolve a filename within base_dir, raising if it would escape the directory."""
    candidate = (base_dir / filename).resolve()
    base_resolved = base_dir.resolve()
    if base_resolved not in candidate.parents and candidate != base_resolved:
        raise ValueError("Path traversal detected")
    return candidate


class UnsafeSQLError(Exception):
    pass


def validate_readonly_sql(sql: str) -> str:
    """Allowlist-enforced read-only SQL validation. Raises UnsafeSQLError if unsafe."""
    if not sql or not sql.strip():
        raise UnsafeSQLError("Empty SQL query")
    cleaned = sql.strip().rstrip(";")
    if ";" in cleaned:
        raise UnsafeSQLError("Multiple statements are not allowed")
    lowered = cleaned.lower()
    first_word = re.split(r"\s+", lowered.strip(), maxsplit=1)[0]
    if first_word not in ALLOWED_SQL_START:
        raise UnsafeSQLError(f"Only SELECT/WITH queries are allowed (got '{first_word}')")
    tokens = set(re.findall(r"[a-z_]+", lowered))
    forbidden_hit = tokens & FORBIDDEN_SQL_KEYWORDS
    if forbidden_hit:
        raise UnsafeSQLError(f"Query contains forbidden keyword(s): {', '.join(sorted(forbidden_hit))}")
    return cleaned
