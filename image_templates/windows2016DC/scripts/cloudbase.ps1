$Host.UI.RawUI.WindowTitle = "Downloading Cloudbase-Init..."

$url = "http://10.2.32.9/soft/cloud_init/2018/CloudbaseInitSetup_Stable_x64.msi"
(new-object System.Net.WebClient).DownloadFile($url, "C:\Windows\Temp\cloudbase-init.msi")

$Host.UI.RawUI.WindowTitle = "Installing Cloudbase-Init..."

$serialPortName = @(Get-WmiObject Win32_SerialPort)[0].DeviceId

$p = Start-Process -Wait -PassThru -FilePath msiexec -ArgumentList "/i C:\Windows\Temp\cloudbase-init.msi /qn /l*v C:\Windows\Temp\cloudbase-init.log LOGGINGSERIALPORTNAME=$serialPortName USERNAME=Administrator INJECTMETADATAPASSWORD=TRUE"
if ($p.ExitCode -ne 0) {
    throw "Installing Cloudbase-Init failed. Log: C:\Windows\Temp\cloudbase-init.log"
}

Copy-Item "A:\cloudbase-init.conf" -Destination "${env:ProgramFiles}\Cloudbase Solutions\Cloudbase-Init\conf\cloudbase-init.conf"
# Copy-Item "A:\ICPG2Run.ps1" -Destination "${env:ProgramFiles}\Cloudbase Solutions\Cloudbase-Init\LocalScripts\"

$Host.UI.RawUI.WindowTitle = "Running Cloudbase-Init SetSetupComplete..."
& "${env:ProgramFiles}\Cloudbase Solutions\Cloudbase-Init\bin\SetSetupComplete.cmd"

(Get-WmiObject -class Win32_TSGeneralSetting -Namespace root\cimv2\terminalservices -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0)

# cloudbase-init will setup setcomplete iteself
#New-Item -Path "${env:WINDIR}\Setup\Scripts" -type Directory -Force
Copy-Item "A:\SetupComplete.cmd" -Destination "${env:WINDIR}\Setup\Scripts\SetupComplete.cmd"

# run sysprep will disable administrator account
#$Host.UI.RawUI.WindowTitle = "Running Sysprep..."
#$unattendedXmlPath = "${env:ProgramFiles}\Cloudbase Solutions\Cloudbase-Init\conf\Unattend.xml"
#& "${env:SystemRoot}\System32\Sysprep\Sysprep.exe" `/generalize `/oobe `/unattend:"$unattendedXmlPath"

net user "Administrator" /active:yes
netsh advfirewall set allprofile state off
Set-Service -Name cloudbase-init -StartupType automatic
Set-Service -Name QEMU-GA -StartupType automatic
Set-Service -Name "QEMU Guest Agent VSS Provider" -StartupType automatic
Start-Service -Name QEMU-GA
Start-Service -Name "QEMU Guest Agent VSS Provider"
shutdown /s /t 60
