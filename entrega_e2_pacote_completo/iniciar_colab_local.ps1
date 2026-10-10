$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pyLocal = Join-Path $PSScriptRoot '.venv-colab\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pyLocal)) {
    python -m venv .venv-colab
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao criar ambiente Colab.' }
}
& $pyLocal -m pip install -r requirements-colab-local.txt
if ($LASTEXITCODE -ne 0) { throw 'Falha ao instalar dependencias.' }
Write-Host 'Mantenha esta janela aberta. Copie a URL com token somente para Conectar ao ambiente local no Colab.'
& $pyLocal -m notebook --no-browser --ServerApp.ip=127.0.0.1 --ServerApp.port=8888 --ServerApp.port_retries=0 --ServerApp.allow_origin=https://colab.research.google.com --ServerApp.allow_credentials=True
