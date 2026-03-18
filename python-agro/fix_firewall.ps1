# Скрипт для настройки файрвола Windows
# Разрешает входящие подключения на порт 8000

Write-Host "[*] Настройка файрвола Windows для порта 8000..." -ForegroundColor Yellow

# Проверяем, запущен ли скрипт от администратора
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[!] ВНИМАНИЕ: Скрипт нужно запустить от имени администратора!" -ForegroundColor Red
    Write-Host "   Щелкните правой кнопкой -> Запуск от имени администратора" -ForegroundColor Yellow
    pause
    exit 1
}

# Добавляем правило для входящих подключений на порт 8000
try {
    $ruleName = "AgroVision-Port-8000"
    
    # Проверяем, существует ли правило
    $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    
    if ($existingRule) {
        Write-Host "[*] Правило файрвола уже существует. Обновляю..." -ForegroundColor Yellow
        Remove-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    }
    
    # Создаем новое правило
    New-NetFirewallRule -DisplayName $ruleName `
        -Direction Inbound `
        -LocalPort 8000 `
        -Protocol TCP `
        -Action Allow `
        -Profile Domain,Private,Public | Out-Null
    
    Write-Host "[OK] Правило файрвола успешно создано!" -ForegroundColor Green
    Write-Host "   Разрешены входящие подключения на порт 8000" -ForegroundColor Green
    Write-Host ""
    Write-Host "Теперь попробуйте открыть с телефона:" -ForegroundColor Cyan
    Write-Host "   http://192.168.1.188:8000" -ForegroundColor White
    Write-Host "   или" -ForegroundColor Cyan
    Write-Host "   https://192.168.1.188:8000" -ForegroundColor White
    
} catch {
    Write-Host "[ERROR] Ошибка при создании правила файрвола:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Попробуйте вручную:" -ForegroundColor Yellow
    Write-Host "1. Откройте 'Брандмауэр Защитника Windows'" -ForegroundColor Yellow
    Write-Host "2. 'Дополнительные параметры'" -ForegroundColor Yellow
    Write-Host "3. 'Правила для входящих подключений' -> 'Создать правило'" -ForegroundColor Yellow
    Write-Host "4. Выберите 'Порт' -> TCP -> 8000 -> 'Разрешить подключение'" -ForegroundColor Yellow
}

Write-Host ""
pause

