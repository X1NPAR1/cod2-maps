# derle.ps1 -- main\ klasorunu haritalar.zip olarak paketler ve Kurulum.cs'yi
# Windows'un kendi .NET 4 derleyicisiyle tek dosyalik CoD2_Haritalar_Kurulum.exe yapar.
# Cikti: kurulum\cikti\CoD2_Haritalar_Kurulum.exe (git'e eklenmez)
$ErrorActionPreference = 'Stop'
$burasi = Split-Path -Parent $MyInvocation.MyCommand.Path
$depo = Split-Path -Parent $burasi
$cikti = Join-Path $burasi 'cikti'
New-Item -ItemType Directory -Force $cikti | Out-Null
$zip = Join-Path $cikti 'haritalar.zip'
if (Test-Path $zip) { Remove-Item $zip }
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::CreateFromDirectory((Join-Path $depo 'main'), $zip, [System.IO.Compression.CompressionLevel]::Optimal, $false)
$net = 'C:\Windows\Microsoft.NET\Framework64\v4.0.30319'
$exe = Join-Path $cikti 'CoD2_Haritalar_Kurulum.exe'
& "$net\csc.exe" /nologo /target:winexe /optimize+ /out:$exe /resource:"$zip,haritalar.zip" `
    /r:System.dll /r:System.Drawing.dll /r:System.Windows.Forms.dll /r:Microsoft.CSharp.dll /r:System.Core.dll `
    /r:"$net\System.IO.Compression.dll" /r:"$net\System.IO.Compression.FileSystem.dll" (Join-Path $burasi 'Kurulum.cs')
if ($LASTEXITCODE -ne 0) { throw "derleme basarisiz" }
Remove-Item $zip
"{0}  {1:N1} MB" -f $exe, ((Get-Item $exe).Length / 1MB)
