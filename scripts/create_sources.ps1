<#
  create_sources.ps1
  Quick helper to scaffold the `sources/` folder with sample files.
  Run in PowerShell from the repo root.
#>

$root = Resolve-Path .
$sources = Join-Path $root 'sources'
if (-not (Test-Path $sources)) {
    New-Item -ItemType Directory -Path $sources | Out-Null
    Write-Host "Created $sources"
}
else {
    Write-Host "$sources already exists"
}

$urlsFile = Join-Path $sources 'urls.txt'
$youtubeFile = Join-Path $sources 'youtube_urls.txt'

if (-not (Test-Path $urlsFile)) {
    @(
        'https://www.bbc.com/news/example-article-12345678'
        'https://www.cnn.com/2025/11/24/example-article'
    ) | Set-Content -Path $urlsFile -Encoding UTF8
    Write-Host "Wrote sample $urlsFile"
}
else {
    Write-Host "$urlsFile already exists"
}

if (-not (Test-Path $youtubeFile)) {
    @(
        'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    ) | Set-Content -Path $youtubeFile -Encoding UTF8
    Write-Host "Wrote sample $youtubeFile"
}
else {
    Write-Host "$youtubeFile already exists"
}

Write-Host "Done. Edit the files in the 'sources' folder and commit them via VS Code or GitHub UI."
