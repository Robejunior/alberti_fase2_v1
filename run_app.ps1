# -*- coding: utf-8 -*-
# Script para iniciar API e Frontend simultaneamente
# Uso: .\run_app.ps1

Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   TIA - Projeto 10 - Fase 3 (API + Frontend)             ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Verificar se estamos no diretório correto
$expectedPath = "C:\Users\ralbertijuni\Desktop\tia_api"
if (-not (Test-Path (Join-Path $expectedPath "frontend.py"))) {
    Write-Host "❌ Erro: frontend.py não encontrado em $expectedPath" -ForegroundColor Red
    Write-Host "Por favor, execute este script do diretório tia_api" -ForegroundColor Yellow
    exit 1
}

# Verificar venv
$venvPath = Join-Path $expectedPath "venv"
if (-not (Test-Path $venvPath)) {
    Write-Host "❌ Erro: Ambiente virtual não encontrado" -ForegroundColor Red
    Write-Host "Execute: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Ativar venv
Write-Host "▶️  Ativando ambiente virtual..." -ForegroundColor Green
& "$venvPath\Scripts\Activate.ps1"

# Verificar requirements
Write-Host "▶️  Verificando dependências..." -ForegroundColor Green
pip install -r requirements.txt --quiet

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║              🚀 INICIANDO COMPONENTES                     ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""

# Criar janelas separadas para API e Frontend
Write-Host "📍 API: http://localhost:5000" -ForegroundColor Cyan
Write-Host "📍 Frontend: http://localhost:8501" -ForegroundColor Cyan
Write-Host ""
Write-Host "Iniciando em 3 segundos..." -ForegroundColor Yellow
Start-Sleep 3

# Iniciar API em nova janela
Write-Host "▶️  Iniciando API Flask..." -ForegroundColor Green
$apiScript = {
    param($path)
    cd $path
    python src/app.py
}
Start-Job -ScriptBlock $apiScript -ArgumentList $expectedPath -Name "TIA_API" | Out-Null

# Aguardar um pouco para API iniciar
Write-Host "⏳ Aguardando API iniciar (5 segundos)..." -ForegroundColor Yellow
Start-Sleep 5

# Verificar se API iniciou
$apiJob = Get-Job -Name "TIA_API"
if ($apiJob.State -eq "Failed") {
    Write-Host "❌ Erro ao iniciar API" -ForegroundColor Red
    Receive-Job -Job $apiJob
    exit 1
}

Write-Host "✅ API iniciada" -ForegroundColor Green

# Iniciar Frontend em nova janela
Write-Host "▶️  Iniciando Streamlit Frontend..." -ForegroundColor Green
$frontendScript = {
    param($path)
    cd $path
    streamlit run frontend.py
}
Start-Job -ScriptBlock $frontendScript -ArgumentList $expectedPath -Name "TIA_Frontend" | Out-Null

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║                  ✅ SISTEMA INICIADO                      ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Dashboard: http://localhost:8501" -ForegroundColor Cyan
Write-Host "🔧 API Docs: http://localhost:5000/api/v1/info" -ForegroundColor Cyan
Write-Host ""
Write-Host "Para parar os serviços:" -ForegroundColor Yellow
Write-Host "  Stop-Job -Name TIA_API" -ForegroundColor Gray
Write-Host "  Stop-Job -Name TIA_Frontend" -ForegroundColor Gray
Write-Host ""

# Manter script rodando
Write-Host "Serviços rodando... (Pressione Ctrl+C para parar)" -ForegroundColor Green
try {
    while ($true) {
        Start-Sleep 10
        $apiJob = Get-Job -Name "TIA_API" -ErrorAction SilentlyContinue
        $frontendJob = Get-Job -Name "TIA_Frontend" -ErrorAction SilentlyContinue

        if ($apiJob.State -eq "Failed" -or $frontendJob.State -eq "Failed") {
            Write-Host "❌ Um dos serviços parou" -ForegroundColor Red
            break
        }
    }
}
catch {
    Write-Host "Encerrando..." -ForegroundColor Yellow
}

# Limpar jobs
Write-Host "Parando serviços..." -ForegroundColor Yellow
Stop-Job -Name "TIA_API" -ErrorAction SilentlyContinue
Stop-Job -Name "TIA_Frontend" -ErrorAction SilentlyContinue
Remove-Job -Name "TIA_API" -ErrorAction SilentlyContinue
Remove-Job -Name "TIA_Frontend" -ErrorAction SilentlyContinue

Write-Host "✅ Encerrado" -ForegroundColor Green
