@echo off
echo ========================================
echo Simulating WhatsApp Webhook Event
echo ========================================
echo.

set URL=http://localhost:8000/webhooks/whatsapp

echo Sending Message: "Ola, vi voces no Google e gostaria de agendar uma limpeza"
echo.

curl -X POST %URL% ^
  -H "Content-Type: application/json" ^
  -d "{\"event\": \"messages.upsert\", \"instance\": \"demo-instance\", \"data\": {\"key\": {\"remoteJid\": \"5511999999999@s.whatsapp.net\", \"fromMe\": false, \"id\": \"ABC123XYZ\"}, \"pushName\": \"Luiz Teste\", \"message\": {\"conversation\": \"Ola, vi voces no Google e gostaria de agendar uma limpeza\"}}}"

echo.
echo.
echo ========================================
echo Test Finished. Check the server console for logs.
echo ========================================
pause
