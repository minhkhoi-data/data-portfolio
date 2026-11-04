param([switch]$ConfigureOnly)
Set-StrictMode -Version 2.0
$ErrorActionPreference = 'Stop'

try {
    $root = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
    $manifestPath = Join-Path $root 'runtime_manifest.json'
    $manifest = [System.IO.File]::ReadAllText($manifestPath, [System.Text.Encoding]::UTF8) | ConvertFrom-Json
    if ($manifest.release -ne 'GA4_CSV_REBUILD_2026_10_13' -or $manifest.files.Count -ne 8) {
        throw 'Unexpected release manifest. Extract the complete new ZIP into a new folder.'
    }
    foreach ($item in $manifest.files) {
        if ($item.path -notmatch '^data/(fact_sessions|fact_purchases|dim_date|dim_channel|dim_device|dim_geo|funnel_stage|measures)\.csv$') {
            throw 'Unexpected CSV path in release manifest.'
        }
        $csvPath = Join-Path $root ($item.path -replace '/', [System.IO.Path]::DirectorySeparatorChar)
        if (-not (Test-Path -LiteralPath $csvPath -PathType Leaf)) {
            throw ('Missing CSV: ' + $item.path + '. Extract the entire ZIP first.')
        }
        if ((Get-Item -LiteralPath $csvPath).Length -ne $item.bytes -or
            (Get-FileHash -LiteralPath $csvPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $item.sha256) {
            throw ('CSV differs from this release: ' + $item.path + '. Use a fresh extraction.')
        }
    }
    $definition = Join-Path $root 'powerbi/EcommerceGrowth.Model/definition'
    $parameterPath = Join-Path $definition 'expressions.tmdl'
    $projectPath = Join-Path $root 'powerbi/MO_GA4_CSV_13_10.pbip'
    if (-not (Test-Path -LiteralPath $projectPath -PathType Leaf)) {
        throw 'The Power BI project file is missing. Extract the complete ZIP.'
    }
    $utf8 = New-Object System.Text.UTF8Encoding($false)
    $before = [System.IO.File]::ReadAllText($parameterPath, $utf8)
    $pattern = '(?m)^expression DataFolder = [^\r\n]*'
    if ([regex]::Matches($before, $pattern).Count -ne 1) {
        throw 'Expected one DataFolder parameter. The model folder does not match this release.'
    }
    $dataFolder = [System.IO.Path]::GetFullPath((Join-Path $root 'data'))
    # M strings escape hash-sign sequences and quotes; Windows backslashes are literal.
    $escaped = $dataFolder.Replace('#', '#(#)').Replace('"', '""').Replace("`r", '#(cr)').Replace("`n", '#(lf)')
    $line = 'expression DataFolder = "' + $escaped + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
    $match = [regex]::Match($before, $pattern)
    $after = $before.Substring(0, $match.Index) + $line + $before.Substring($match.Index + $match.Length)
    if ($after -ne $before) {
        $tempPath = $parameterPath + '.' + [guid]::NewGuid().ToString('N') + '.tmp'
        try {
            [System.IO.File]::WriteAllText($tempPath, $after, $utf8)
            Move-Item -LiteralPath $tempPath -Destination $parameterPath -Force
        } finally {
            if (Test-Path -LiteralPath $tempPath) { Remove-Item -LiteralPath $tempPath }
        }
    }
    Write-Output 'All eight CSV files verified. The local DataFolder parameter is configured.'
    if ($ConfigureOnly) { exit 0 }
    if ([System.Environment]::OSVersion.Platform -ne [System.PlatformID]::Win32NT) {
        throw 'Opening Power BI Desktop requires Windows. ConfigureOnly can run on other systems.'
    }
    try {
        Start-Process -FilePath $projectPath -WorkingDirectory (Split-Path -Parent $projectPath)
        Write-Output 'Power BI opening requested. Click Refresh in Desktop to load the CSV snapshot.'
    } catch {
        Write-Output 'The data path is ready, but Windows could not open the PBIP association.'
        Write-Output 'Open Power BI Desktop, choose File > Open, and select powerbi/MO_GA4_CSV_13_10.pbip.'
        exit 2
    }
} catch {
    Write-Error $_.Exception.Message
    exit 1
}
