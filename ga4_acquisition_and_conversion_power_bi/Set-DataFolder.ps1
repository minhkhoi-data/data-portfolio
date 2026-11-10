param([switch]$ConfigureOnly)
$ErrorActionPreference = 'Stop'

$dataFolder = Join-Path $PSScriptRoot 'data'
$csvFiles = @('fact_sessions.csv', 'fact_purchases.csv', 'dim_date.csv',
              'dim_channel.csv', 'dim_device.csv', 'funnel_stage.csv')
foreach ($name in $csvFiles) {
    if (-not (Test-Path -LiteralPath (Join-Path $dataFolder $name) -PathType Leaf)) {
        throw "Missing data/$name. Extract the whole ZIP before opening the report."
    }
}

$project = Join-Path $PSScriptRoot 'GA4AcquisitionAndConversion.pbip'
$parameter = Join-Path $PSScriptRoot 'GA4AcquisitionAndConversion.SemanticModel/definition/expressions.tmdl'
$utf8 = [System.Text.UTF8Encoding]::new($false)
$content = [System.IO.File]::ReadAllText($parameter, $utf8)
$match = [regex]::Match($content, '(?m)^expression DataFolder = [^\r\n]*')
if (-not $match.Success) { throw 'The DataFolder parameter was not found.' }

$escaped = $dataFolder.Replace('#', '#(#)').Replace('"', '""')
$line = 'expression DataFolder = "' + $escaped + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
$configured = $content.Substring(0, $match.Index) + $line + $content.Substring($match.Index + $match.Length)
if ($configured -ne $content) {
    [System.IO.File]::WriteAllText($parameter, $configured, $utf8)
}
if ($ConfigureOnly) { return }

try {
    Start-Process -FilePath $project
    Write-Host 'In Power BI Desktop, select Home > Refresh.'
} catch {
    Write-Host 'The data folder is configured. Open GA4AcquisitionAndConversion.pbip from Power BI Desktop, then select Home > Refresh.'
    exit 1
}
