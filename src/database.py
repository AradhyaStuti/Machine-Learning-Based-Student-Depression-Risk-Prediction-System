# SQLite store for prediction history

import json
import sqlite3
from datetime import datetime, timezone

from src.config import DB_PATH


def _connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    # Create the predictions table if it doesn't exist
    conn = _connect()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS predictions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id   TEXT NOT NULL,
            timestamp    TEXT NOT NULL,
            input_json   TEXT NOT NULL,
            probability  REAL NOT NULL,
            risk_level   TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def save_prediction(request_id, input_data, probability, risk_level):
    # Save one prediction row
    conn = _connect()
    conn.execute(
        "INSERT INTO predictions (request_id, timestamp, input_json, probability, risk_level)"
        " VALUES (?, ?, ?, ?, ?)",
        (
            request_id,
            datetime.now(timezone.utc).isoformat(),
            json.dumps(input_data),
            probability,
            risk_level,
        ),
    )
    conn.commit()
    conn.close()


def get_predictions(limit=50):
    # Return recent predictions, newest first
    conn = _connect()
    rows = conn.execute(
        "SELECT * FROM predictions ORDER BY id DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]
