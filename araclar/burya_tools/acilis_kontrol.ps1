# acilis_kontrol.ps1 -- EKRAN GORUNTUSU ALMAZ. Tam ekran acar, harita yuklenene
# kadar hata kutusu + log denetler. -Kapat verilirse sonunda oyunu kapatir.
param([switch]$Kapat)
$r = 'F:\Activision\Call of Duty 2'
$o = Get-Content "$r\burya_tools\oyna.ps1" -Raw
$a = $o.IndexOf("if (-not ([System.Management.Automation.PSTypeName]'KrDiyalog').Type) {")
$b = $o.IndexOf('"@', $a) + 5
Invoke-Expression $o.Substring($a, $b - $a)
Get-Process CoD2SP_s -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
Remove-Item "$r\main\console.log" -ErrorAction SilentlyContinue
$arg = '+set r_fullscreen 0 +set r_mode 1280x720 +set r_aaSamples 1 +set r_anisotropy 16 +set r_picmip 0 +set r_picmip_bump 0 +set r_picmip_spec 0 +set r_picmip_manual 1 +set r_glow 1 +set developer 1 +set logfile 2 +set thereisacow 1337 +set com_introplayed 1 +set snd_volume 0 +set mus_volume 0 +devmap burya'
if (-not ([System.Management.Automation.PSTypeName]'KrPencere').Type) {
Add-Type @"
using System; using System.Runtime.InteropServices;
public class KrPencere {
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hh, bool r);
}
"@
}
# oyun penceresi ikinci ekrana (birinci ekranda kullanici film izliyor)
function Ikinci-Ekran($proc) {
    for ($i = 0; $i -lt 60; $i++) {
        $proc.Refresh()
        if ($proc.MainWindowHandle -ne [IntPtr]::Zero) { [KrPencere]::MoveWindow($proc.MainWindowHandle, 2220, 160, 1296, 758, $true) | Out-Null; return }
        Start-Sleep -Milliseconds 250
    }
}
$p = Start-Process -FilePath "$r\CoD2SP_s.exe" -WorkingDirectory $r -ArgumentList $arg -PassThru
Ikinci-Ekran $p
$log = "$r\main\console.log"; $t = 0; $durum = "ZAMAN ASIMI"
while ($t -lt 180) {
    Start-Sleep 2; $t += 2
    if ($p.HasExited) { $durum = "OYUN KAPANDI"; break }
    $k = [KrDiyalog]::Oku($p.Id)
    if ($k) { $durum = "HATA KUTUSU: $k"; break }
    if ((Test-Path $log) -and (Select-String $log -Pattern 'ui_campaign russian' -Quiet)) { Start-Sleep 8; $durum = "YUKLENDI"; break }
}
$k = [KrDiyalog]::Oku($p.Id); if ($k) { $durum = "HATA KUTUSU: $k" }
"durum: $durum ($t sn)"
$L = Get-Content $log
"betik hatasi: " + ($L | Select-String 'script runtime error|script compile error').Count
$L | Select-String -Pattern 'script (runtime|compile) error' -Context 0,12 | Select-Object -First 2 | ForEach-Object { $_.Line; $_.Context.PostContext }
if ($Kapat) {
    Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
    Start-Sleep 2
    Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
    "oyun kapatildi"
}
