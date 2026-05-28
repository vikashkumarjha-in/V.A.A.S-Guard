import re
from typing import Tuple, Optional

# Basic but high-speed regex for common SQLi patterns
SQLI_PATTERNS = [
    r"(?i)union\s+select",
    r"(?i)select\s+.*\s+from",
    r"(?i)insert\s+into",
    r"(?i)update\s+.*\s+set",
    r"(?i)delete\s+from",
    r"(?i)drop\s+table",
    r"(?i)truncate\s+table",
    r"(?i)exec\s+xp_cmdshell",
    r"(?i)OR\s+['\"]\d+['\"]=['\"]\d+['\"]",
    r"(?i)OR\s+\d+=\d+",
    r"['\"];\s*--",
    r"--",
    r"/\*.*?\*/"
]

def detect_sqli(content: str) -> Tuple[bool, Optional[str]]:
    if not content:
        return False, None

    for pattern in SQLI_PATTERNS:
        if re.search(pattern, content):
            return True, f"Matched pattern: {pattern}"

    # Placeholder for advanced heuristics
    # Example: entropy analysis or AST parsing could go here

    return False, None
