@echo off
REM Script para configurar o ambiente do Bem-Querer Hub

echo ========================================
echo Bem-Querer Hub - Configuracao Inicial
echo ========================================
echo.

REM Verificar se .env.example existe
if not exist .env.example (
    echo [ERRO] Arquivo .env.example nao encontrado!
    pause
    exit /b 1
)

REM Verificar se .env ja existe
if exist .env (
    echo [AVISO] Arquivo .env ja existe!
    echo.
    set /p OVERWRITE="Deseja sobrescrever? (S/N): "
    if /i not "%OVERWRITE%"=="S" (
        echo Operacao cancelada.
        pause
        exit /b 0
    )
)

REM Copiar template
echo [INFO] Copiando .env.example para .env...
copy .env.example .env >nul

echo [OK] Arquivo .env criado com sucesso!
echo.
echo ========================================
echo PROXIMOS PASSOS:
echo ========================================
echo.
echo 1. Abra o arquivo .env em um editor de texto
echo 2. Siga as instrucoes em SETUP.md para obter as credenciais
echo 3. Preencha todas as variaveis obrigatorias
echo 4. Execute start.bat para iniciar o servidor
echo.
echo Arquivo .env localizado em:
echo %CD%\.env
echo.
echo Guia completo em:
echo %CD%\..\SETUP.md
echo.
pause
