@echo off
REM Launcher for File Organizer (Windows)

cd /d "%~dp0"

REM Prefer the project's virtual environment Python if present.
if exist ".venv\Scripts\python.exe" (
  rem If 'uv' is available, use it
  where uv >nul 2>&1 && (
    if exist "pyproject.toml" (
      uv sync || exit /b %ERRORLEVEL%
    )
    uv run main.py %* || exit /b %ERRORLEVEL%
  )
  rem Fallback to venv python if uv not used
  ".venv\Scripts\python.exe" main.py %*
  exit /b %ERRORLEVEL%
)

REM Fallback to system Python
where uv >nul 2>&1 && (
  if exist "pyproject.toml" (
    uv sync || exit /b %ERRORLEVEL%
  )
  uv run main.py %*
  exit /b %ERRORLEVEL%
)

python main.py %*
exit /b %ERRORLEVEL%
