"""Isolated test server: one production-equivalent API on port 9899 against a
throwaway SQLite database. Never touches the production DB.

Run:  python3 foundation/run_test_server.py
Stop: Ctrl+C
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

# Ensure project root is on sys.path
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from foundation import config as foundation_config  # noqa: E402
from foundation.store import Store  # noqa: E402
from foundation.api import set_store, make_server  # noqa: E402


def build_test_store():
    _TEST_DB = Path(tempfile.mkdtemp(prefix="sai_test_")) / "test.sqlite"
    _store = Store(_TEST_DB)
    foundation_config._deep_merge(
        foundation_config.load_config(),
        {"db_path": str(_TEST_DB), "port": 9899, "host": "127.0.0.1"},
    )
    _store._migrate()  # schema + seeds (idempotent)
    return _store, _TEST_DB


def start_test_server(host="127.0.0.1", port=9899):
    store, test_db = build_test_store()
    from foundation.api import set_store  # local import to keep top-level light
    set_store(store)
    httpd = make_server(host, port)
    print(f"SHAI ISOLATED TEST API listening on http://{host}:{port} (db={test_db})")
    return httpd, store, test_db


def main():
    httpd, _, _ = start_test_server()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        httpd.server_close()


if __name__ == "__main__":
    main()
