::Set Execution Policy 64 Bit
 cmd.exe /c powershell -Command "Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Force"
::Set Execution Policy 32 Bit
 C:\Windows\SysWOW64\cmd.exe /c powershell -Command "Set-ExecutionPolicy -ExecutionPolicy Unrestrcited -Force"

:: disable integrity checks
bcdedit.exe -set loadoptions DISABLE_INTEGRITY_CHECKS

echo "disable firewall"
netsh firewall set opmode mode=DISABLE

echo "setup disk policy"
diskpart /s a:\enable-online.bat

::Disable Hibernation
%SystemRoot%\System32\reg.exe ADD HKLM\SYSTEM\CurrentControlSet\Control\Power\ /v HibernateFileSizePercent /t REG_DWORD /d 0 /f
%SystemRoot%\System32\reg.exe ADD HKLM\SYSTEM\CurrentControlSet\Control\Power\ /v HibernateEnabled /t REG_DWORD /d 0 /f
