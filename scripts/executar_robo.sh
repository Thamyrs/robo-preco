#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJETO_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$PROJETO_DIR/venv"
REQ_FILE="$PROJETO_DIR/requirements.txt"
SCRIPT="$PROJETO_DIR/main.py"
LOG_DIR="$PROJETO_DIR/logs"

LOG_FILE="$LOG_DIR/script_linux_$(date +'%Y-%m-%d_%H-%M-%S').log"

exec > >(tee -a "$LOG_FILE") 2>&1

echo "================================================"
echo "Iniciando execução do robô de preços..."
echo "Data/Hora: $(date)"
echo "================================================"

if ! command -v python3 &>/dev/null; then
    echo "Python 3 não encontrado! Instale com: sudo apt install python3 python3-venv -y"
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Falha ao criar ambiente virtual."
        exit 1
    fi
fi

source "$VENV_DIR/bin/activate"

if [ -f "$REQ_FILE" ]; then
    echo "Instalando dependências do requirements.txt..."
    pip install -r "$REQ_FILE"
fi

echo "Iniciando execução do script Python..."
python3 "$SCRIPT"


if [ $? -eq 0 ]; then
    echo "Execução concluída com sucesso!"
else
    echo "Ocorreu um erro durante a execução do script."
fi

deactivate
exit 0
