# oturum_izle.ps1 -- her 60 sn'de Claude 5 saatlik oturum blogunu olcer (ccusage,
# yerel kayitlardan). Yuzde = aktif blok token / gecmisteki en yuksek blok token
# (gercek hesap limiti yerel kayitlarda yok; bu bir TAHMINDIR).
# Saat $Bitis'e gelince ya da yuzde >= $Esik olunca 'DUR' dosyasini yazar.
param([string]$Bitis = "05:46", [int]$Esik = 80)
$kok = 'F:\Activision\Call of Duty 2\burya_tools'
$durum = Join-Path $kok 'oturum_durum.txt'
$dur = Join-Path $kok 'DUR'
Remove-Item $dur -ErrorAction SilentlyContinue
while ($true) {
    $simdi = Get-Date
    $yuzde = -1
    try {
        $tum = (npx -y ccusage@latest blocks --json 2>$null | Out-String | ConvertFrom-Json).blocks
        $gercek = $tum | Where-Object { -not $_.isGap }
        $aktif = $gercek | Where-Object { $_.isActive } | Select-Object -First 1
        $enfazla = ($gercek | Where-Object { -not $_.isActive } | Measure-Object -Property totalTokens -Maximum).Maximum
        if ($aktif -and $enfazla -gt 0) { $yuzde = [math]::Round(100.0 * $aktif.totalTokens / $enfazla, 1) }
        $satir = "{0:HH:mm:ss} aktif={1} enfazla={2} yuzde~{3}" -f $simdi, $aktif.totalTokens, $enfazla, $yuzde
    } catch { $satir = "{0:HH:mm:ss} olcum hatasi" -f $simdi }
    Set-Content -Path $durum -Value $satir -Encoding utf8
    if ($simdi.ToString("HH:mm") -ge $Bitis -or ($yuzde -ge $Esik)) {
        Set-Content -Path $dur -Value $satir -Encoding utf8
        break
    }
    Start-Sleep 60
}
