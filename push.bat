@echo off
echo --- Iniciando Envio para o GitHub ---
echo.

:: Configurar Remote (caso nao esteja)
git remote remove origin
git remote add origin https://github.com/bemquererkids/bem-querer-hub.git

:: Verificar Status
git status

:: Enviar
echo.
echo Tentando enviar para 'master'...
git push -u origin master

echo.
if %errorlevel% neq 0 (
    echo [ERRO] O envio falhou.
    echo Verifique se o repositorio existe no GitHub e se voce tem permissao.
    pause
) else (
    echo [SUCESSO] Projeto enviado para o GitHub!
    pause
)
