# Inicia a API de classificacao (Arvore de Decisao + Gemini) usada pelo painel
# para avaliar risco e registrar revisao humana.
# Uso: .\iniciar_api_fase3.ps1

$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$apiDir = Join-Path $PSScriptRoot 'api_fase3'
$venvPython = Join-Path $apiDir 'venv\Scripts\python.exe'

if (-not (Test-Path -LiteralPath $venvPython)) {
    throw "Ambiente api_fase3\venv nao encontrado. Rode primeiro:`n  cd api_fase3`n  python -m venv venv`n  .\venv\Scripts\Activate.ps1`n  pip install -r requirements.txt"
}

Write-Host "API Fase 3: http://127.0.0.1:5000 - Ctrl+C para encerrar" -ForegroundColor Cyan
Set-Location -LiteralPath $apiDir
& $venvPython app.py
