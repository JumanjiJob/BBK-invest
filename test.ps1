# test.ps1
Clear-Host
Write-Host "Тестирование ИИ-консультанта BBKinvest" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# Функция для отправки запроса
function Send-ChatMessage {
    param(
        [string]$SessionId,
        [string]$Message
    )

    if ($SessionId) {
        $body = @{
            session_id = $SessionId
            message = $Message
        } | ConvertTo-Json
    } else {
        $body = @{
            message = $Message
        } | ConvertTo-Json
    }

    $response = curl.exe -X POST "http://localhost:8000/api/v1/chat" -H "Content-Type: application/json" -d $body
    return $response
}

# Начало диалога
Write-Host "`n[1/6] Начинаем диалог..." -ForegroundColor Yellow
$resp = Send-ChatMessage -Message ""
$respJson = $resp | ConvertFrom-Json
$sessionId = $respJson.session_id
Write-Host "ИИ: $($respJson.message)" -ForegroundColor Green
Write-Host "Варианты: $($respJson.options -join ', ')" -ForegroundColor Gray

# Выбор "Займ"
Write-Host "`n[2/6] Отвечаем: Займ" -ForegroundColor Yellow
$resp = Send-ChatMessage -SessionId $sessionId -Message "Займ"
$respJson = $resp | ConvertFrom-Json
Write-Host "ИИ: $($respJson.message)" -ForegroundColor Green
Write-Host "Варианты: $($respJson.options -join ', ')" -ForegroundColor Gray

# Выбор "Физическое лицо"
Write-Host "`n[3/6] Отвечаем: Физическое лицо" -ForegroundColor Yellow
$resp = Send-ChatMessage -SessionId $sessionId -Message "Физическое лицо"
$respJson = $resp | ConvertFrom-Json
Write-Host "ИИ: $($respJson.message)" -ForegroundColor Green

Write-Host "`n✅ Диалог успешно начат!" -ForegroundColor Green
Write-Host "Session ID: $sessionId" -ForegroundColor Magenta
Write-Host "Текущий шаг: $($respJson.step)" -ForegroundColor Magenta