import functools
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from platformdirs import user_cache_dir

CACHE_DIR = Path(user_cache_dir("colombia-hydrodata", ensure_exists=True))
INDEX_FILE = CACHE_DIR / "index.txt"
DEFAULT_TTL_DAYS = 7


def _read_index() -> dict[str, datetime]:
    index = {}
    if INDEX_FILE.exists():
        for line in INDEX_FILE.read_text().strip().splitlines():
            parts = line.split(",", maxsplit=1)
            if len(parts) == 2:
                name, expires = parts
                index[name] = datetime.fromisoformat(expires)
    return index


def _write_index(index: dict[str, datetime]) -> None:
    lines = [f"{name},{expires.isoformat()}" for name, expires in index.items()]
    INDEX_FILE.write_text("\n".join(lines))


def _get_cache_path(table_name: str) -> Path:
    return CACHE_DIR / f"{table_name}.parquet"


def save_table(table_name: str, ttl_days: int = DEFAULT_TTL_DAYS):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            index = _read_index()
            cache_path = _get_cache_path(table_name)

            if table_name in index and cache_path.exists():
                if datetime.now() < index[table_name]:
                    return pd.read_parquet(cache_path)

            result = func(*args, **kwargs)
            result.to_parquet(cache_path)
            index[table_name] = datetime.now() + timedelta(days=ttl_days)
            _write_index(index)
            return result

        return wrapper

    return decorator
