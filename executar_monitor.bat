@echo off


set "PROJETO_DIR=%~dp0"
set "VENV_DIR=%PROJETO_DIR%\venv"
set "REQ_FILE=%PROJETO_DIR%\requirements.txt"
set "SCRIPT=%PROJETO_DIR%\monitora_preco.py"

cd /d "%PROJETO_DIR%"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo Python não encontrado! Instale o Python 3 e tente novamente.
    pause
    exit /b 1
)

if not exist "%VENV_DIR%" (
    echo Ambiente virtual não encontrado. Criando venv...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo Falha ao criar ambiente virtual!
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate"

if exist "%REQ_FILE%" (
    echo Instalando dependências do requirements.txt...
    pip install -r "%REQ_FILE%"
)

python "%SCRIPT%"

if not exist "%SCRIPT%" (
    echo ERRO: O script "%SCRIPT%" não foi encontrado!
    pause
    exit /b 1
)

if %errorlevel% neq 0 (
    echo O script encontrou um erro durante a execução.
    exit /b 1
)

echo Execução concluída com sucesso!

deactivate

exit /b 0
