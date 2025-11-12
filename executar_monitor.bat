@echo off

set "PROJETO_DIR=%~dp0"
set "VENV_DIR=%PROJETO_DIR%\venv"
set "REQ_FILE=%PROJETO_DIR%\requirements.txt"
set "SCRIPT=%PROJETO_DIR%\monitora_preco.py"
set "LOG_DIR=%PROJETO_DIR%logs"

cd /d "%PROJETO_DIR%"

if not exist "%LOG_DIR%" (
    mkdir "%LOG_DIR%"
)

set "LOG_FILE=%LOG_DIR%\script_windows_%date:~6,4%-%date:~3,2%-%date:~0,2%_%time:~0,2%-%time:~3,2%.log"
set "LOG_FILE=%LOG_FILE: =0%"

echo ================================================ >> "%LOG_FILE%"
echo Execução iniciada em %date% %time% >> "%LOG_FILE%"
echo ================================================ >> "%LOG_FILE%"

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python não encontrado! Instale o Python 3 e tente novamente. >> "%LOG_FILE%"
    echo ERRO: Python não encontrado! Instale o Python 3 e tente novamente.
    pause
    exit /b 1
)

if not exist "%VENV_DIR%" (
    echo Ambiente virtual não encontrado. Criando venv... >> "%LOG_FILE%"
    echo Ambiente virtual não encontrado. Criando venv...
    python -m venv "%VENV_DIR%" >> "%LOG_FILE%" 2>&1
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao criar ambiente virtual! >> "%LOG_FILE%"
        echo ERRO: Falha ao criar ambiente virtual! 
        pause
        exit /b 1
    )
)

call "%VENV_DIR%\Scripts\activate"

if exist "%REQ_FILE%" (
    echo Instalando dependências do requirements.txt... >> "%LOG_FILE%"
    echo Instalando dependências do requirements.txt...
    pip install -r "%REQ_FILE%" >> "%LOG_FILE%" 2>&1
)

echo Executando o monitor de preços... >> "%LOG_FILE%"
echo Executando o monitor de preços... 
python "%SCRIPT%" 

if not exist "%SCRIPT%" (
    echo ERRO: O script "%SCRIPT%" não foi encontrado! >> "%LOG_FILE%"
    echo ERRO: O script "%SCRIPT%" não foi encontrado!
    pause
    exit /b 1
)

if %errorlevel% neq 0 (
    echo ERRO: O script encontrou um erro durante a execução. >> "%LOG_FILE%"
    echo ERRO: O script encontrou um erro durante a execução.
    pause
    exit /b 1
)

echo Execução concluída com sucesso! >> "%LOG_FILE%"
echo Execução concluída com sucesso! 

deactivate

echo Log salvo em: "%LOG_FILE%"
echo ================================================
pause
exit /b 0