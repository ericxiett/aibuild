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

# 针对windows 2008 Disable Network Level Authentication 否则会提示安全漏洞
(Get-WmiObject -class Win32_TSGeneralSetting -Namespace root\cimv2\terminalservices -Filter "TerminalName='RDP-tcp'").SetUserAuthenticationRequired(0)


certutil.exe -addstore -f "TrustedPublisher" "a:\redhat.cer"
$url = "http://10.2.32.9/soft/cloud_init/2018/windows/2k8R2/Balloon.zip"
(new-object System.Net.WebClient).DownloadFile($url, "C:\Windows\Temp\Balloon.zip")

# 下载串口驱动
$url = "http://10.2.32.9/soft/cloud_init/2018/windows/2k8R2/vioserial.zip"
(new-object System.Net.WebClient).DownloadFile($url, "C:\Windows\Temp\vioserial.zip")

## 下载串口ddl
$url = "http://10.2.32.9/soft/cloud_init/2018/windows/dlls.zip"
(new-object System.Net.WebClient).DownloadFile($url, "C:\Windows\Temp\dlls.zip")
UnzipFile "C:\Windows\Temp\dlls.zip" "C:\Windows\Temp\"

Move-Item -Path "C:\Windows\Temp\dlls\*" -Destination "C:\Windows\System32\"

# 安装驱动
UnzipFile "C:\Windows\Temp\Balloon.zip" "C:\Windows\Temp\"
PnPutil.exe -i -a "C:\Windows\Temp\Balloon\2k8R2\amd64\balloon.inf"

UnzipFile "C:\Windows\Temp\vioserial.zip" "C:\Windows\Temp\"
PnPutil.exe -i -a "C:\Windows\Temp\vioserial\2k8R2\amd64\vioser.inf"

# 安装Qga
$url = "http://10.2.32.9/soft/qga/windows/qemu-ga-x64.msi"
(new-object System.Net.WebClient).DownloadFile($url, "C:\Windows\Temp\qemu-ga-x64.msi")
Start-Process C:\Windows\Temp\qemu-ga-x64.msi /qn -Wait
