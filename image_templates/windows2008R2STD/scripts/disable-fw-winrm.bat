::Disable firewall
cmd.exe /c netsh advfirewall set allprofiles state off

::Disable winrm
cmd.exe /c sc config winrm start= disabled