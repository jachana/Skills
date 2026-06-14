# Brain-Connect.ps1
# Surface CANDIDATE cross-project links in an Obsidian "brain" vault: pairs of projects
# that share vocabulary / tags / stack, so an agent can then judge whether something built
# in one is reusable in the other. Heuristic only — it nominates, it does not conclude.
#
#   pwsh Brain-Connect.ps1 -BrainRoot "D:/Vaults/Brain"
#   pwsh Brain-Connect.ps1 -Top 15 -MinShared 3
#
# It reads each project's Scope/Milestones text + frontmatter tags/labels/stack, builds a
# keyword set, and ranks project pairs by shared significant terms (Jaccard-ish overlap).

[CmdletBinding()]
param(
    [string]$BrainRoot = $env:BRAIN_PATH,
    [int]$Top = 20,
    [int]$MinShared = 2,
    [switch]$IncludeArchived
)
$ErrorActionPreference = 'Stop'
if (-not $BrainRoot) { throw "BrainRoot not set. Pass -BrainRoot <vault> or set BRAIN_PATH." }
$BrainRoot = (Resolve-Path $BrainRoot).Path
$projDir = Join-Path $BrainRoot 'Projects'
if (-not (Test-Path $projDir)) { throw "No Projects/ folder under: $projDir" }

$STOP = @('the','a','an','and','or','for','to','of','in','on','with','this','that','is','are','be',
  'as','at','by','it','its','from','will','can','we','our','your','their','project','repo','using','use',
  'el','la','los','las','un','una','de','del','y','o','para','por','con','en','que','se','su','sus',
  'es','son','este','esta','como','al','lo','proyecto','usar') | ForEach-Object { $_.ToLower() }

function Get-Frontmatter { param([string]$Path)
    $t = Get-Content $Path -Raw
    if ($t -notmatch '(?s)^---\s*\r?\n(.*?)\r?\n---') { return @{} }
    $fm = @{}
    foreach ($l in ($Matches[1] -split "`n")) { if ($l -match '^\s*([A-Za-z0-9_-]+):\s*(.*?)\s*$') { $fm[$Matches[1]] = $Matches[2].Trim().Trim('"') } }
    return $fm
}
function Get-Section { param([string]$Text,[string]$H)
    if ($Text -match "(?ms)^##\s+$([regex]::Escape($H))\s*\r?\n(.*?)(?=^##\s+|\z)") { return $Matches[1].TrimEnd() }; return '' }

function Tokenize { param([string]$s)
    if (-not $s) { return @() }
    ($s.ToLower() -split '[^a-z0-9áéíóúñ\+\#]+') | Where-Object { $_.Length -ge 3 -and $_ -notin $STOP } | Select-Object -Unique
}

$projs = @()
foreach ($pf in (Get-ChildItem -Path $projDir -Filter '*.md' -Recurse | Where-Object { $_.BaseName -ne '_INDEX' })) {
    $fm = Get-Frontmatter $pf.FullName
    if (-not $IncludeArchived -and $fm.status -eq 'archived') { continue }
    if ($fm.type -eq 'admin') { continue }
    $raw = Get-Content $pf.FullName -Raw
    $bag = New-Object System.Collections.Generic.HashSet[string]
    foreach ($k in @('tags','labels','stack','tech','client')) {
        foreach ($tok in (Tokenize $fm[$k])) { [void]$bag.Add($tok) }
    }
    foreach ($sec in @('Scope','Milestones')) { foreach ($tok in (Tokenize (Get-Section $raw $sec))) { [void]$bag.Add($tok) } }
    if ($bag.Count -gt 0) { $projs += [pscustomobject]@{ Name = $pf.BaseName; Bag = $bag } }
}

$pairs = @()
for ($i = 0; $i -lt $projs.Count; $i++) {
    for ($j = $i + 1; $j -lt $projs.Count; $j++) {
        $a = $projs[$i]; $b = $projs[$j]
        $shared = @($a.Bag | Where-Object { $b.Bag.Contains($_) })
        if ($shared.Count -ge $MinShared) {
            $union = ($a.Bag.Count + $b.Bag.Count - $shared.Count)
            $score = [math]::Round($shared.Count / [math]::Max(1, $union), 3)
            $pairs += [pscustomobject]@{ A = $a.Name; B = $b.Name; Shared = ($shared | Sort-Object); Count = $shared.Count; Score = $score }
        }
    }
}

$pairs = $pairs | Sort-Object Count, Score -Descending | Select-Object -First $Top

Write-Output "# Cross-project link candidates"
Write-Output ""
Write-Output "_Heuristic: shared significant terms (tags/stack/scope). These are CANDIDATES to investigate, not conclusions._"
Write-Output ""
if (-not $pairs) { Write-Output "_No project pairs share >= $MinShared significant terms._"; return }
Write-Output "| A | B | Shared | Score | Terms |"
Write-Output "|---|---|---|---|---|"
foreach ($p in $pairs) {
    Write-Output "| $($p.A) | $($p.B) | $($p.Count) | $($p.Score) | $([string]::Join(', ', $p.Shared)) |"
}
