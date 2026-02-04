# Setup automatic weekly data updates via Windows Task Scheduler
# Run this script as Administrator

$WorkspacePath = "C:\Users\w.pleasantsii\Desktop\Testcode"
$PythonExe = "$WorkspacePath\.venv\Scripts\python.exe"
$ScriptPath = "$WorkspacePath\weekly_data_update.py"

# Create the scheduled task trigger (every Monday at 2:00 AM)
$Trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At 2am

# Create the action (run Python script)
$Action = New-ScheduledTaskAction -Execute $PythonExe `
    -Argument $ScriptPath `
    -WorkingDirectory $WorkspacePath

# Set task settings
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable

# Register the task
$TaskName = "PitcherDataWeeklyUpdate"

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "Task already exists. Updating..."
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
}

Register-ScheduledTask -TaskName $TaskName `
    -Trigger $Trigger `
    -Action $Action `
    -Settings $Settings `
    -Description "Weekly update of pitcher statistics from Baseball Savant and rebuild dashboards"

Write-Host "✓ Scheduled task created: $TaskName"
Write-Host "  Runs: Every Monday at 2:00 AM"
Write-Host "  Script: $ScriptPath"
Write-Host ""
Write-Host "To manually run the update, execute:"
Write-Host "  & '$PythonExe' '$ScriptPath'"
