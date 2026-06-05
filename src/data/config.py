import getpass
import os
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / ".env")


def get_env(name: str, default: Optional[str] = None) -> Optional[str]:
    value = os.environ.get(name)
    return value if value is not None else default


def get_db_config() -> Dict[str, Optional[str]]:
    return {
        "dbname": get_env("DB_NAME", "tradewinds"),
        "user": get_env("DB_USER", getpass.getuser()),
        "password": get_env("DB_PASSWORD"),
        "host": get_env("DB_HOST", "localhost"),
        "port": get_env("DB_PORT"),
    }
