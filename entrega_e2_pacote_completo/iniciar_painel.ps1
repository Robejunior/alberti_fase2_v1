$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonPainel = Join-Path $PSScriptRoot '.venv-colab\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPainel)) { throw 'Ambiente .venv-colab nao encontrado. Configure o ambiente E2 primeiro.' }
& $pythonPainel -B -m src.painel
