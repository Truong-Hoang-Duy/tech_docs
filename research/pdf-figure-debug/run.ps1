# Chay debug_figure_matching.py bang dung venv cua backend (da co fitz/pydantic_ai/openai).
$ErrorActionPreference = "Stop"

$Dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$RepoRoot = Resolve-Path (Join-Path $Dir "..\..\..")
$PythonBin = Join-Path $RepoRoot "backend\services\api\.venv\Scripts\python.exe"

if (-not (Test-Path $PythonBin)) {
    Write-Error "Khong thay venv backend tai $PythonBin -- xem README.md de biet cach tao venv."
    exit 1
}

& $PythonBin (Join-Path $Dir "debug_figure_matching.py") @args
exit $LASTEXITCODE
