# acilis_kontrol.ps1 -- EKRAN GORUNTUSU ALMAZ. Tam ekran acar, harita yuklenene
# kadar hata kutusu + log denetler. -Kapat verilirse sonunda oyunu kapatir.
param([switch]$Kapat)
$r = 'F:\Activision\Call of Duty 2'
$o = Get-Content "$r\metel_tools\oyna.ps1" -Raw
$a = $o.IndexOf("if (-not ([System.Management.Automation.PSTypeName]'KrDiyalog').Type) {")
$b = $o.IndexOf('"@', $a) + 5
Invoke-Expression $o.Substring($a, $b - $a)
Get-Process CoD2SP_s -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 2
Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
Remove-Item "$r\main\console.log" -ErrorAction SilentlyContinue
$arg = '+set r_fullscreen 1 +set r_mode 1920x1080 +set r_aaSamples 1 +set r_anisotropy 16 +set r_picmip 0 +set r_picmip_bump 0 +set r_picmip_spec 0 +set r_picmip_manual 1 +set r_glow 1 +set developer 1 +set logfile 2 +set thereisacow 1337 +set com_introplayed 1 +devmap metel'
$p = Start-Process -FilePath "$r\CoD2SP_s.exe" -WorkingDirectory $r -ArgumentList $arg -PassThru
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
