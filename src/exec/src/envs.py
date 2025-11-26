import os

class MissingEnvError(Exception):
    pass

REQUIRED_VARS = ["IN", "OUT", "STD", "BIN", "CONF", "LOG"]
missing = [v for v in REQUIRED_VARS if v not in os.environ]
if missing:
    raise MissingEnvError(f"Required environment variables missing: {', '.join(missing)}")

IN = os.environ["IN"]
OUT = os.environ["OUT"]
STD = os.environ["STD"]
BIN = os.environ["BIN"]
CONF = os.environ["CONF"]
LOG = os.environ["LOG"]
LOG_MAX_SIZE = int(os.getenv("LOG_MAX_SIZE", 5 * 1024 * 1024))
