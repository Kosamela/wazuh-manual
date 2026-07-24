#requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet(
        'WIN-FEATURE-DEFENDER','WIN-FEATURE-POWERSHELL-ENHANCED','WIN-FEATURE-SYSMON',
        'WIN-ROLE-RDS','WIN-ROLE-FILESERVER','WIN-ROLE-DC','WIN-ROLE-BACKUP-VEEAM',
        'WIN-ROLE-DATABASE-MSSQL','WIN-ROLE-DATABASE-OTHER','WIN-ROLE-WEB-IIS','WIN-ROLE-APP',
        'WIN-ROLE-DNS-DHCP','WIN-ROLE-NPS-RADIUS','WIN-ROLE-HYPERV','WIN-ROLE-PRINT'
    )]
    [string[]]$Roles,

    [string]$BasePath = (Join-Path $PSScriptRoot '..\base\sysmon-win-server-baseline.xml'),
    [string]$FragmentsPath = (Join-Path $PSScriptRoot '..\fragments'),
    [string]$OutputPath = (Join-Path $PWD 'sysmon-merged.xml')
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$map = @{
    'WIN-FEATURE-DEFENDER'            = 'win-feature-defender.fragment.xml'
    'WIN-FEATURE-POWERSHELL-ENHANCED' = 'win-feature-powershell-enhanced.fragment.xml'
    'WIN-FEATURE-SYSMON'              = 'win-feature-sysmon.fragment.xml'
    'WIN-ROLE-RDS'                     = 'win-role-rds.fragment.xml'
    'WIN-ROLE-FILESERVER'              = 'win-role-fileserver.fragment.xml'
    'WIN-ROLE-DC'                      = 'win-role-dc.fragment.xml'
    'WIN-ROLE-BACKUP-VEEAM'            = 'win-role-backup-veeam.fragment.xml'
    'WIN-ROLE-DATABASE-MSSQL'          = 'win-role-database-mssql.fragment.xml'
    'WIN-ROLE-DATABASE-OTHER'          = 'win-role-database-other.fragment.xml'
    'WIN-ROLE-WEB-IIS'                 = 'win-role-web-iis.fragment.xml'
    'WIN-ROLE-APP'                     = 'win-role-app.fragment.xml'
    'WIN-ROLE-DNS-DHCP'                = 'win-role-dns-dhcp.fragment.xml'
    'WIN-ROLE-NPS-RADIUS'              = 'win-role-nps-radius.fragment.xml'
    'WIN-ROLE-HYPERV'                  = 'win-role-hyperv.fragment.xml'
    'WIN-ROLE-PRINT'                   = 'win-role-print.fragment.xml'
}

if (-not (Test-Path -LiteralPath $BasePath)) { throw "Brak pliku bazowego: $BasePath" }
[xml]$base = Get-Content -LiteralPath $BasePath -Raw -Encoding UTF8
if ($base.DocumentElement.Name -ne 'Sysmon') { throw 'Plik bazowy nie ma korzenia <Sysmon>.' }
$eventFiltering = $base.Sysmon.EventFiltering
if ($null -eq $eventFiltering) { throw 'Plik bazowy nie zawiera <EventFiltering>.' }

foreach ($role in ($Roles | Select-Object -Unique)) {
    $fragmentFile = Join-Path $FragmentsPath $map[$role]
    if (-not (Test-Path -LiteralPath $fragmentFile)) { throw "Brak fragmentu dla $role: $fragmentFile" }
    [xml]$fragment = Get-Content -LiteralPath $fragmentFile -Raw -Encoding UTF8
    if ($fragment.DocumentElement.Name -ne 'SysmonRoleFragment') { throw "Nieprawidlowy korzen fragmentu: $fragmentFile" }

    $roleComment = $base.CreateComment(" DODANO ROLE: $role ")
    [void]$eventFiltering.AppendChild($roleComment)
    foreach ($node in $fragment.SysmonRoleFragment.EventFiltering.ChildNodes) {
        $imported = $base.ImportNode($node, $true)
        [void]$eventFiltering.AppendChild($imported)
    }
}

$settings = New-Object System.Xml.XmlWriterSettings
$settings.Indent = $true
$settings.IndentChars = '  '
$settings.Encoding = New-Object System.Text.UTF8Encoding($false)
$settings.NewLineChars = "`r`n"
$settings.NewLineHandling = 'Replace'

$outDir = Split-Path -Parent $OutputPath
if ($outDir -and -not (Test-Path -LiteralPath $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
$writer = [System.Xml.XmlWriter]::Create($OutputPath, $settings)
try { $base.Save($writer) } finally { $writer.Dispose() }

# Kontrola poprawnosci XML. Walidacje semantyczna wykonaj na hoście testowym komenda Sysmon64.exe -c.
[xml](Get-Content -LiteralPath $OutputPath -Raw -Encoding UTF8) | Out-Null
$hash = (Get-FileHash -Algorithm SHA256 -LiteralPath $OutputPath).Hash
Write-Host "Utworzono: $OutputPath"
Write-Host "Role: $($Roles -join ', ')"
Write-Host "SHA256: $hash"
