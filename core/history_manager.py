"""SQLite persistence for organization runs and undo data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import sqlite3

from config.constants import DATABASE_PATH


@dataclass(frozen=True, slots=True)
class HistoryRun:
    id: int
    timestamp: str
    mode: str
    root_path: Path
    files_moved: int
    undone: bool


@dataclass(frozen=True, slots=True)
class QuarantinedDuplicate:
    move_id: int
    run_id: int
    timestamp: str
    original_path: Path
    quarantine_path: Path
    restored: bool


class HistoryManager:
    """Stores completed file moves in SQLite."""

    def __init__(self, db_path: Path = DATABASE_PATH) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self._db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    mode TEXT NOT NULL,
                    root_path TEXT NOT NULL,
                    files_moved INTEGER NOT NULL,
                    undone INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS moves (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id INTEGER NOT NULL,
                    source_path TEXT NOT NULL,
                    destination_path TEXT NOT NULL,
                    action TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    error TEXT,
                    FOREIGN KEY(run_id) REFERENCES runs(id)
                )
                """
            )

    def create_run(self, mode: str, root_path: Path) -> int:
        timestamp = datetime.now().isoformat(timespec="seconds")
        with self._connect() as connection:
            cursor = connection.execute(
                "INSERT INTO runs(timestamp, mode, root_path, files_moved) VALUES (?, ?, ?, 0)",
                (timestamp, mode, str(root_path)),
            )
            return int(cursor.lastrowid)

    def add_move(
        self,
        run_id: int,
        source_path: Path,
        destination_path: Path,
        action: str,
        success: bool,
        error: str | None,
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO moves(run_id, source_path, destination_path, action, success, error)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (run_id, str(source_path), str(destination_path), action, int(success), error),
            )
            if success and action == "moved":
                connection.execute("UPDATE runs SET files_moved = files_moved + 1 WHERE id = ?", (run_id,))

    def list_runs(self, limit: int = 100) -> list[HistoryRun]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM runs ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [
            HistoryRun(
                id=int(row["id"]),
                timestamp=str(row["timestamp"]),
                mode=str(row["mode"]),
                root_path=Path(row["root_path"]),
                files_moved=int(row["files_moved"]),
                undone=bool(row["undone"]),
            )
            for row in rows
        ]

    def get_last_active_run_id(self) -> int | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT id FROM runs WHERE undone = 0 AND files_moved > 0 ORDER BY id DESC LIMIT 1"
            ).fetchone()
        return int(row["id"]) if row else None

    def list_successful_moves(self, run_id: int) -> list[tuple[Path, Path]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT source_path, destination_path
                FROM moves
                WHERE run_id = ? AND success = 1 AND action = 'moved'
                ORDER BY id DESC
                """,
                (run_id,),
            ).fetchall()
        return [(Path(row["source_path"]), Path(row["destination_path"])) for row in rows]

    def list_quarantined_duplicates(self, limit: int = 200) -> list[QuarantinedDuplicate]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    moves.id AS move_id,
                    moves.run_id AS run_id,
                    runs.timestamp AS timestamp,
                    moves.source_path AS source_path,
                    moves.destination_path AS destination_path,
                    runs.undone AS undone
                FROM moves
                JOIN runs ON runs.id = moves.run_id
                WHERE runs.mode = 'duplicate_cleanup'
                  AND moves.success = 1
                  AND moves.action = 'moved'
                ORDER BY moves.id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            QuarantinedDuplicate(
                move_id=int(row["move_id"]),
                run_id=int(row["run_id"]),
                timestamp=str(row["timestamp"]),
                original_path=Path(row["source_path"]),
                quarantine_path=Path(row["destination_path"]),
                restored=bool(row["undone"]),
            )
            for row in rows
        ]

    def mark_undone(self, run_id: int) -> None:
        with self._connect() as connection:
            connection.execute("UPDATE runs SET undone = 1 WHERE id = ?", (run_id,))
