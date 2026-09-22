$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$run = Join-Path $root 'run.ps1'
$taskName = 'BrownEye Local GPU Worker'

if (-not $env:SUPABASE_URL) { throw 'Set SUPABASE_URL before installing the task.' }
if (-not $env:SUPABASE_SECRET_KEY -and -not $env:SUPABASE_SERVICE_ROLE_KEY) { throw 'Set SUPABASE_SECRET_KEY or SUPABASE_SERVICE_ROLE_KEY before installing the task.' }

$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument ('-NoProfile -ExecutionPolicy Bypass -File "' + $run + '"')
$trigger = New-ScheduledTaskTrigger -AtLogOn
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -RestartCount 999 -RestartInterval (New-TimeSpan -Minutes 1)

Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings -Description 'BrownEye local GPU bridge worker. Claims leased Supabase work and reports results.' -Force | Out-Null
Start-ScheduledTask -TaskName $taskName

Write-Host 'BrownEye local GPU worker startup task installed and started.'
