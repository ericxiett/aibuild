function UnzipFile([string]$souceFile, [string]$targetFolder)
{
    if(!(Test-Path $targetFolder))
    {
        mkdir $targetFolder
    }
    $shellApp = New-Object -ComObject Shell.Application
    $files = $shellApp.NameSpace($souceFile).Items()
    #下面这句会删除已解压的，但不会影响目录内其它不相干的文件      
    $files|%{if (Test-Path ("$targetFolder/{0}" -f  $_.name )){Remove-Item ("$targetFolder/{0}" -f  $_.name) -Force -Recurse}}
    $shellApp.NameSpace($targetFolder).CopyHere($files)
}

# 针对windows 2012 Disable Network Level Authentication 否则会提示安全漏洞
(Get-WmiObject -class Win32_TSGeneralSetting -Namespace root\cimv2\terminalservices -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0)

$url = "http://10.2.32.9/soft/win-virtio/from_redhat_signed/1.9.3/Balloon.zip"
(new-object System.Net.WebClient).DownloadFile($url, "C:\Windows\Temp\Balloon.zip")

# 下载串口驱动
$url = "http://10.2.32.9/soft/win-virtio/from_redhat_signed/1.9.3/vioserial.zip"
(new-object System.Net.WebClient).DownloadFile($url, "C:\Windows\Temp\vioserial.zip")

## 下载串口ddl
$url = "http://10.2.32.9/soft/win-virtio/from_redhat_signed/1.9.3/dlls.zip"
(new-object System.Net.WebClient).DownloadFile($url, "C:\Windows\Temp\dlls.zip")
UnzipFile "C:\Windows\Temp\dlls.zip" "C:\Windows\Temp\"

Move-Item -Path "C:\Windows\Temp\dlls\*" -Destination "C:\Windows\System32\"

# 安装驱动
UnzipFile "C:\Windows\Temp\Balloon.zip" "C:\Windows\Temp\"
PnPutil.exe -i -a "C:\Windows\Temp\Balloon\2k8R2\amd64\balloon.inf"

UnzipFile "C:\Windows\Temp\vioserial.zip" "C:\Windows\Temp\"
PnPutil.exe -i -a "C:\Windows\Temp\vioserial\2k8R2\amd64\vioser.inf"

# 安装Qga
$url = "http://10.2.32.9/soft/win-virtio/from_redhat_signed/1.9.3/qemu-ga-x64.msi"
(new-object System.Net.WebClient).DownloadFile($url, "C:\Windows\Temp\qemu-ga-x64.msi")
Start-Process C:\Windows\Temp\qemu-ga-x64.msi /qn -Wait

# 自动联机
"SAN Policy=OnlineAll" | diskpart

# 配置SNMP
#Powershell Script To Install SNMP Services (SNMP Service, SNMP WMI Provider)

#Import ServerManger Module
#Import-Module ServerManager

#Check If SNMP Services Are Already Installed
#$check = Get-WindowsFeature | Where-Object {$_.Name -eq "SNMP-Services"}
#If ($check.Installed -ne "True") {
#	#Install/Enable SNMP Services
#	Add-WindowsFeature SNMP-Services | Out-Null
#}

#Set-ItemProperty -Path HKLM:\SYSTEM\CurrentControlSet\Control\Terminal*Server\WinStations\RDP-TCP\ -Name PortNumber -Value 33899

# Paste this line first
 
# Paste these two lines next
#Set-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server\WinStations\RDP-TCP\" -Name PortNumber -Value 33899
 
#Write-host "port number is $RDPPORT" -ForegroundColor Magenta
#Write-host "Launch RDP with IP:$RDPORT or cmdline MSTSC /V [ip]:$RDPORT"

#netsh advfirewall firewall add rule name="RDP 33899" dir=in action=allow protocol=TCP localport=33899
#netsh advfirewall firewall add rule name="SNMP UDP" dir=in action=allow protocol=UDP localport=161
#netsh advfirewall firewall add rule name="ICMP Allow incoming V4 echo request" protocol=icmpv4:8,any dir=in action=allow
#netsh advfirewall firewall add rule name="ICMP Allow incoming V6 echo request" protocol=icmpv6:8,any dir=in action=allow
