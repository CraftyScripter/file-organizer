# Intelligent File Organizer

A PyQt6 desktop application for organizing files (Linux-first) with a cross-platform Python architecture.

## Architecture

- `config/` keeps application settings and the original extension-to-category mapping.
- `core/` contains the business logic: scanning, classification, duplicate detection, moves, SQLite history, and orchestration.
- `services/` contains application services for preview, undo, and realtime folder watching.
- `gui/` contains the PyQt6 interface and worker objects that keep long operations off the UI thread.
- `storage/` stores the SQLite database, JSON settings, and logs.
- `tests/` covers core behavior that should remain stable as the GUI evolves.

The default `type` mode preserves the original script behavior: known extensions are moved into folders such as `document`, `image`, `video`, `audio`, and the other existing categories.

## Features

- Drag-and-drop folder selection
- Direct-folder scanning by default so existing subfolders and project directories are not modified
- Preview before moving
- Start, cancel, and progress feedback
- Undo last organization run
- Hidden file filtering
- Name collision handling
- SHA256 duplicate detection
- SQLite history
- File logging
- Realtime Downloads monitoring with watchdog
- Organization modes for type, extension, size, creation date, modification date, and custom rules

## Custom Rules

Rules are stored in `storage/settings.json` and editable from Settings as JSON.

Example:

```json
[
  {
    "name": "Large PDFs to Books",
    "enabled": true,
    "conditions": {
      "ext": "pdf",
      "size_gt_mb": 50
    },
    "destination": "Books"
  }
]
```

Supported conditions:

- `ext`
- `type`
- `size_gt_mb`
- `size_lt_mb`
- `name_contains`

## Install

Requires Python >= 3.12.

Create a virtual environment and install the runtime dependencies directly:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install "pyqt6>=6.11.0" "pyqt6-charts>=6.11.0" "qtawesome>=1.4.0" "watchdog>=6.0.0" pytest
```

Dependencies are declared in `pyproject.toml`.

## Run

```bash
python main.py
```

## Test

```bash
python -m pytest
```

## Notes

- The app creates `storage/app.db` automatically on first launch.
- Logs are written to `storage/logs/file_organizer.log`.
