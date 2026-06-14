# Brain-Report.ps1
# Generate a generalized progress report across ALL projects in an Obsidian "brain" vault.
# Deterministic aggregation (no LLM): reads Projects/*.md frontmatter + dated ## Log entries
# + task checkboxes, and emits a structured Markdown report:
#   - Overview table (status / phase / progress / priority / activity / open tasks)
#   - Activity in the period (dated log entries per project)
#   - Completed in the period (milestones + ticked tasks)
#   - Pending tasks (all open, grouped by project, priority-sorted)
#   - Needs attention (active but stale, or with blockers)
#
# Generic / portable — nothing hardcoded.
#   pwsh Brain-Report.ps1 -BrainRoot "D:/Vaults/Brain" -Since 7d
#   pwsh Brain-Report.ps1 -Since 2026-06-01 -Until 2026-06-14 -Out report.md
#   pwsh Brain-Report.ps1                              # uses $env:BRAIN_PATH, last 7 days

[CmdletBinding()]
param(
    [string]$BrainRoot = $env:BRAIN_PATH,
    [string]$Since = '7d',          # "7d" / "30d" or an ISO date "YYYY-MM-DD"
    [string]$Until = '',            # ISO date; default = today
    [string]$Out = '',              # file path; default = stdout
    [switch]$IncludeArchived
)

$ErrorActionPreference = 'Stop'
if (-not $BrainRoot) { throw "BrainRoot not set. Pass -BrainRoot <vault> or set BRAIN_PATH." }
$BrainRoot = (Resolve-Path $BrainRoot).Path
$projDir = Join-Path $BrainRoot 'Projects'
if (-not (Test-Path $projDir)) { throw "No Projects/ folder under: $projDir" }

# ── date window ─────────────────────────────────────────────────────────────
$today = (Get-Date).Date
if ($Until) { $untilDate = [datetime]::ParseExact($Until, 'yyyy-MM-dd', $null).Date } else { $untilDate = $today }
if ($Since -match '^(\d+)d$') { $sinceDate = $untilDate.AddDays(-1 * [int]$Matches[1]) }
else { $sinceDate = [datetime]::ParseExact($Since, 'yyyy-MM-dd', $null).Date }

# ── helpers ─────────────────────────────────────────────────────────────────
function Get-Frontmatter {
    param([string]$Path)
    $text = Get-Content $Path -Raw
    if ($text -notmatch '(?s)^---\s*\r?\n(.*?)\r?\n---') { return @{} }
    $fm = @{}
    foreach ($line in ($Matches[1] -split "`n")) {
        if ($line -match '^\s*([A-Za-z0-9_-]+):\s*(.*?)\s*$') { $fm[$Matches[1]] = $Matches[2].Trim().Trim('"') }
    }
    return $fm
}
function Get-Section {
    param([string]$Text, [string]$Heading)
    if ($Text -match "(?ms)^##\s+$([regex]::Escape($Heading))\s*\r?\n(.*?)(?=^##\s+|\z)") { return $Matches[1].TrimEnd() }
    return ''
}
function PriorityRank { param($p) switch ($p) { 'p0' {0} 'p1' {1} 'p2' {2} default {3} } }

# ── gather ──────────────────────────────────────────────────────────────────
$projectFiles = Get-ChildItem -Path $projDir -Filter '*.md' -Recurse | Where-Object { $_.BaseName -ne '_INDEX' }
$projects = @()

foreach ($pf in $projectFiles) {
    $fm = Get-Frontmatter $pf.FullName
    if (-not $IncludeArchived -and $fm.status -eq 'archived') { continue }
    if ($fm.type -in @('admin')) { continue }
    $raw = Get-Content $pf.FullName -Raw
    $name = $pf.BaseName

    # log entries in window
    $logText = Get-Section $raw 'Log'
    $entries = @()
    foreach ($line in ($logText -split "`n")) {
        if ($line -match '^\s*-\s*(\d{4}-\d{2}-\d{2})') {
            $d = [datetime]::ParseExact($Matches[1], 'yyyy-MM-dd', $null).Date
            if ($d -ge $sinceDate -and $d -le $untilDate) { $entries += [pscustomobject]@{ Date = $d; Text = $line.Trim() } }
        }
    }

    # tasks (Brain → Repo · Tasks + any ## Tasks)
    $taskText = (Get-Section $raw 'Brain → Repo · Tasks') + "`n" + (Get-Section $raw 'Tasks')
    $open = @(); $doneCount = 0
    foreach ($line in ($taskText -split "`n")) {
        if ($line -match '^\s*-\s*\[\s\]\s*(.+?)\s*$') { $open += $Matches[1].Trim() }
        elseif ($line -match '^\s*-\s*\[(x|X)\]\s*(.+?)\s*$') { $doneCount++ }
    }

    $lastAct = $null
    if ($fm.'last-activity' -and $fm.'last-activity' -match '^\d{4}-\d{2}-\d{2}') {
        $lastAct = [datetime]::ParseExact($fm.'last-activity'.Substring(0,10), 'yyyy-MM-dd', $null).Date
    }

    $projects += [pscustomobject]@{
        Name = $name; Status = $fm.status; Phase = $fm.phase; Progress = $fm.progress
        Priority = $fm.priority; Client = $fm.client; NextMilestone = $fm.'next-milestone-label'
        Blockers = $fm.blockers; LastActivity = $lastAct
        Entries = $entries; OpenTasks = $open; DoneCount = $doneCount
    }
}

$projects = $projects | Sort-Object @{ E = { PriorityRank $_.Priority } }, @{ E = 'Name' }

# ── render ──────────────────────────────────────────────────────────────────
$sb = [System.Text.StringBuilder]::new()
function W { param($s = '') [void]$sb.AppendLine($s) }

W "# Brain Progress Report"
W ""
W "**Period:** $($sinceDate.ToString('yyyy-MM-dd')) → $($untilDate.ToString('yyyy-MM-dd'))  ·  **Generated:** $((Get-Date).ToString('yyyy-MM-dd HH:mm'))  ·  **Projects:** $($projects.Count)"
W ""

# Overview
W "## Overview"
W ""
W "| Project | Status | Phase | Progress | Prio | Activity | Open |"
W "|---|---|---|---|---|---|---|"
foreach ($p in $projects) {
    $act = $p.Entries.Count
    W "| $($p.Name) | $($p.Status) | $($p.Phase) | $($p.Progress) | $($p.Priority) | $act | $($p.OpenTasks.Count) |"
}
W ""

# Activity in period
W "## Activity in period"
W ""
$any = $false
foreach ($p in ($projects | Where-Object { $_.Entries.Count -gt 0 })) {
    $any = $true
    W "### $($p.Name)"
    foreach ($e in ($p.Entries | Sort-Object Date -Descending)) { W "$($e.Text)" }
    W ""
}
if (-not $any) { W "_No dated log activity in this window._"; W "" }

# Completed in period
W "## Completed in period"
W ""
$comp = $false
foreach ($p in $projects) {
    $milestones = $p.Entries | Where-Object { $_.Text -match '\[(MILESTONE|DELIVERED)\]' }
    if ($milestones) { $comp = $true; W "**$($p.Name)**"; foreach ($m in $milestones) { W "$($m.Text)" }; W "" }
}
if (-not $comp) { W "_No milestones logged in this window. (Tick tasks + log [MILESTONE] entries to populate this.)_"; W "" }

# Pending tasks
W "## Pending tasks"
W ""
$pend = $false
foreach ($p in ($projects | Where-Object { $_.OpenTasks.Count -gt 0 })) {
    $pend = $true
    W "**$($p.Name)** ($($p.Priority)) — $($p.OpenTasks.Count) open"
    foreach ($t in $p.OpenTasks) { W "- [ ] $t" }
    W ""
}
if (-not $pend) { W "_No open tasks across tracked projects._"; W "" }

# Needs attention
W "## Needs attention"
W ""
$att = $false
foreach ($p in $projects) {
    $reasons = @()
    if ($p.Status -eq 'active' -and $p.Entries.Count -eq 0) {
        $staleFor = if ($p.LastActivity) { ($untilDate - $p.LastActivity).Days } else { '?' }
        $reasons += "active but no activity in window (last activity $staleFor d ago)"
    }
    if ($p.Blockers -and $p.Blockers -notin @('[]', '')) { $reasons += "blockers: $($p.Blockers)" }
    if ($reasons.Count -gt 0) { $att = $true; W "- **$($p.Name)** — $([string]::Join('; ', $reasons))" }
}
if (-not $att) { W "_Nothing flagged. All active projects show movement and no blockers._" }
W ""

$report = $sb.ToString()
if ($Out) { Set-Content -Path $Out -Value $report -Encoding UTF8; Write-Host "Report written to $Out" }
else { Write-Output $report }
