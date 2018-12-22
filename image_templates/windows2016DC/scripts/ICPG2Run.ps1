# Step 1: Disable UAC
New-ItemProperty -Path HKLM:Software\Microsoft\Windows\CurrentVersion\Policies\System -Name EnableLUA -PropertyType DWord -Value 0 -Force | Out-Null
Write-Host "User Access Control (UAC) has been disabled." -ForegroundColor Green
 
# Step 2: Disable IE ESC
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A7-37EF-4b3f-8CFC-4F3A74704073}" -Name "IsInstalled" -Value 0 | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Active Setup\Installed Components\{A509B1A8-37EF-4b3f-8CFC-4F3A74704073}" -Name "IsInstalled" -Value 0 | Out-Null
Stop-Process -Name Explorer | Out-Null
Write-Host "IE Enhanced Security Configuration (ESC) has been disabled." -ForegroundColor Green
 
# Step 3: Disable the shutdown tracker
# Reference: http://www.askvg.com/how-to-disable-remove-annoying-shutdown-event-tracker-in-windows-server-2003-2008/
If (!(Test-Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Reliability")) {
  New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Reliability"
}
New-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Reliability" -Name "ShutdownReasonOn" -PropertyType DWord -Value 0 -Force -ErrorAction continue 
New-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Reliability" -Name "ShutdownReasonUI" -PropertyType DWord -Value 0 -Force -ErrorAction continue 
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Reliability" -Name "ShutdownReasonOn" -Value 0
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows NT\Reliability" -Name "ShutdownReasonUI" -Value 0
Write-Host "Shutdown Tracker has been disabled." -ForegroundColor Green
 
# Step 4: Disable Automatic Updates
# Reference: http://www.benmorris.me/2012/05/1st-test-blog-post.html
$AutoUpdate = (New-Object -com "Microsoft.Update.AutoUpdate").Settings
$AutoUpdate.NotificationLevel = 1
$AutoUpdate.Save()
Write-Host "Windows Update has been disabled." -ForegroundColor Green

# Step 5: Enable Remote Desktop
# Reference: http://social.technet.microsoft.com/Forums/windowsserver/en-US/323d6bab-e3a9-4d9d-8fa8-dc4277be1729/enable-remote-desktop-connections-with-powershell
(Get-WmiObject Win32_TerminalServiceSetting -Namespace root\cimv2\TerminalServices).SetAllowTsConnections(1,1) 
(Get-WmiObject -Class "Win32_TSGeneralSetting" -Namespace root\cimv2\TerminalServices -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0) 
exit 1002