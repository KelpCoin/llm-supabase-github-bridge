$ErrorActionPreference = 'Stop'

if (-not $env:SUPABASE_URL) { throw 'SUPABASE_URL is required' }
if (-not $env:SUPABASE_SECRET_KEY -and -not $env:SUPABASE_SERVICE_ROLE_KEY) { throw 'SUPABASE_SECRET_KEY or SUPABASE_SERVICE_ROLE_KEY is required' }

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$worker = Join-Path $root 'worker.py'

python $worker
