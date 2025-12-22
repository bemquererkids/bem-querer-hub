@echo off
REM Script para gerar SECRET_KEY

echo ========================================
echo Gerando SECRET_KEY
echo ========================================
echo.

REM Verificar se Python esta disponivel
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERRO] Python nao encontrado!
    echo Por favor, instale Python ou use: https://generate-secret.vercel.app/32
    pause
    exit /b 1
)

echo [INFO] Gerando chave secreta...
echo.

REM Ativar ambiente virtual se existir
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Gerar SECRET_KEY
python -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"

echo.
echo [OK] Copie a linha acima e cole no seu arquivo .env
echo.
pause
