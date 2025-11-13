$SCRIPT_DIR  = Split-Path -Parent $MyInvocation.MyCommand.Definition
$PROJETO_DIR = Split-Path -Parent $SCRIPT_DIR
$VENV_DIR    = Join-Path $PROJETO_DIR "venv"
$REQ_FILE    = Join-Path $PROJETO_DIR "requirements.txt"
$SCRIPT      = Join-Path $PROJETO_DIR "main.py"
$LOG_DIR     = Join-Path $PROJETO_DIR "logs"

if (-not (Test-Path $LOG_DIR)) {
    New-Item -ItemType Directory -Path $LOG_DIR | Out-Null
}

$timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm"
$LOG_FILE  = Join-Path $LOG_DIR "script_windows_$timestamp.log"

Start-Transcript -Path $LOG_FILE -Append

Write-Host "==========================================="
Write-Host "Iniciando execucao do robo de preços..."
Write-Host "Data/Hora: $(Get-Date)"
Write-Host "==========================================="

function Abort-Script($message) {
    Write-Host "ERRO: $message"
    Write-Host "Encerrando execucao..."
    Stop-Transcript | Out-Null
    exit 1
}

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Abort-Script "Python 3 nao encontrado! Instale o Python 3 e tente novamente."
}

if (-not (Test-Path $VENV_DIR)) {
    Write-Host "Criando ambiente virtual..."
    try {
        python -m venv $VENV_DIR
    }
    catch {
        Abort-Script "Falha ao criar o ambiente virtual. Detalhes: $($_.Exception.Message)"
    }
}


try {
    $activateScript = Join-Path $VENV_DIR "Scripts\Activate.ps1"

    if (-not (Test-Path $activateScript)) {
        throw "O script de ativacao não foi encontrado em: $activateScript"
    }

    . $activateScript

    $pythonPath = (Get-Command python).Source
    if ($pythonPath -notlike "*$VENV_DIR*") {
        throw "Falha ao ativar o ambiente virtual."
    }

    Write-Host "Ambiente virtual ativado com sucesso!"
}
catch {
    Abort-Script "Erro ao ativar o ambiente virtual. Detalhes: $($_.Exception.Message)"
}


if (Test-Path $REQ_FILE) {
    Write-Host "Instalando dependencias..."
    try {
        pip install -r $REQ_FILE
        Write-Host "Dependencias instaladas com sucesso!"
    }
    catch {
        Abort-Script "Erro ao instalar dependencias. Detalhes: $($_.Exception.Message)"
    }
}

Write-Host "Executando script Python..."
try {
    & "$VENV_DIR\Scripts\python.exe" $SCRIPT
    if ($LASTEXITCODE -ne 0) {
        throw "O script Python retornou codigo de erro $LASTEXITCODE."
    }
    Write-Host "Execucao concluida com sucesso!"
}
catch {
    Abort-Script "Falha ao executar o script Python. Detalhes: $($_.Exception.Message)"
}

try {
    deactivate
}
catch {
    Write-Host "Aviso: falha ao desativar o ambiente virtual."
}

Stop-Transcript
Write-Host "Logs gravados em: $LOG_FILE"
