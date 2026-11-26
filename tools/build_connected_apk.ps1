param(
  [Parameter(Mandatory = $true)]
  [ValidatePattern('^https://')]
  [string]$ApiUrl
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $projectRoot 'frontend_recovered'
$flutter = 'C:\dev\flutter\bin\flutter.bat'

if (-not (Test-Path -LiteralPath $flutter)) {
  throw "Flutter was not found at $flutter"
}

$baseUrl = $ApiUrl.TrimEnd('/')
$health = Invoke-RestMethod -Uri "$baseUrl/health" -TimeoutSec 20
if ($health.status -ne 'ok' -or $health.database -ne 'connected') {
  throw 'The VirasatAI API or database health check failed.'
}

$env:GRADLE_OPTS = '-Dorg.gradle.offline=true'
Push-Location $frontend
try {
  & $flutter build apk --debug --no-pub `
    "--dart-define=VIRASATAI_API_BASE_URL=$baseUrl"
  if ($LASTEXITCODE -ne 0) { throw 'Flutter APK build failed.' }
} finally {
  Pop-Location
}

$apk = Join-Path $frontend 'build\app\outputs\flutter-apk\app-debug.apk'
Write-Host "Connected APK ready: $apk" -ForegroundColor Green
