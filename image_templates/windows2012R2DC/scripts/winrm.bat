:: Current WinRM settings
:: winrm get winrm/config

:: Configure WinRM
:: start "" /WAIT cmd.exe /c net stop winrm
cmd.exe /c winrm quickconfig -q
cmd.exe /c winrm quickconfig -transport:http
cmd.exe /c winrm set winrm/config @{MaxTimeoutms="1800000"}
cmd.exe /c winrm set winrm/config/winrs @{MaxMemoryPerShellMB="2048"}
cmd.exe /c winrm set winrm/config/service @{AllowUnencrypted="true"}
cmd.exe /c winrm set winrm/config/service/auth @{Basic="true"}
cmd.exe /c winrm set winrm/config/client/auth @{Basic="true"}
cmd.exe /c winrm set winrm/config/listener?Address=*+Transport=HTTP @{Port="5985"}

:: Fire up WinRM!
:: cmd.exe /c sc config winrm start= auto
cmd.exe /c net start winrm
cmd.exe /c sc config winrm start= disabled

netsh advfirewall set allprofiles state off