# Manual Test Commands for UazAPI Authentication

## Test 1: Header 'token'
```bash
curl -X GET "https://bemquerer.uazapi.com/instance/status" \
  -H "token: 093b971c-f10f-4af1-b0aa-a13c6ad15909" \
  -H "Content-Type: application/json"
```

## Test 2: Header 'admintoken'
```bash
curl -X GET "https://bemquerer.uazapi.com/instance/status" \
  -H "admintoken: 093b971c-f10f-4af1-b0aa-a13c6ad15909" \
  -H "Content-Type: application/json"
```

## Test 3: Header 'apikey'
```bash
curl -X GET "https://bemquerer.uazapi.com/instance/status" \
  -H "apikey: 093b971c-f10f-4af1-b0aa-a13c6ad15909" \
  -H "Content-Type: application/json"
```

## Test 4: Authorization Bearer
```bash
curl -X GET "https://bemquerer.uazapi.com/instance/status" \
  -H "Authorization: Bearer 093b971c-f10f-4af1-b0aa-a13c6ad15909" \
  -H "Content-Type: application/json"
```

## Test 5: Query Parameter 'token'
```bash
curl -X GET "https://bemquerer.uazapi.com/instance/status?token=093b971c-f10f-4af1-b0aa-a13c6ad15909" \
  -H "Content-Type: application/json"
```

## Test 6: Query Parameter 'admintoken'
```bash
curl -X GET "https://bemquerer.uazapi.com/instance/status?admintoken=093b971c-f10f-4af1-b0aa-a13c6ad15909" \
  -H "Content-Type: application/json"
```

## Alternative Endpoints to Test
- `/instance/list`
- `/instance/connect`
- `/webhook`

## Expected Success Response
```json
{
  "connected": true,
  "status": "open",
  "instance": {
    "name": "bemquerer",
    "phone": "5511991026844"
  }
}
```
