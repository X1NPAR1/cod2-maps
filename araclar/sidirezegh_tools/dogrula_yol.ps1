# dogrula.ps1 -- derle + yol bagla (g_connectpaths 2) + log denetimi.
# Cikti: LEAK, "in solid", "no connections", betik hatalari sayilari.
$r = 'F:\Activision\Call of Duty 2'
Set-Location "$r\sidirezegh_tools"
& .\derle.bat sidirezegh | Out-Null
$bsp = Get-Content .\log\sidirezegh_bsp.log
"LEAK/ERROR (bsp): " + ($bsp | Select-String 'LEAK|ERROR').Count
Get-Process CoD2SP_s -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1
Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
Remove-Item "$r\main\console.log" -ErrorAction SilentlyContinue
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
$p = Start-Process -FilePath "$r\CoD2SP_s.exe" -WorkingDirectory $r -PassThru -ArgumentList `
  '+set r_fullscreen 0 +set r_mode 1280x720 +set developer 1 +set logfile 2 +set snd_volume 0 +set mus_volume 0 +set r_displayRefresh 165 +set vid_xpos 0 +set vid_ypos 0 +set thereisacow 1337 +set com_introplayed 1 +set g_connectpaths 2 +devmap sidirezegh'
if (-not ([System.Management.Automation.PSTypeName]'KrDiyalog').Type) {
Add-Type @"
using System; using System.Text; using System.Collections.Generic; using System.Runtime.InteropServices;
public class KrDiyalog {
  delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumWindows(EnumProc f, IntPtr l);
  [DllImport("user32.dll")] static extern bool EnumChildWindows(IntPtr p, EnumProc f, IntPtr l);
  [DllImport("user32.dll")] static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
  [DllImport("user32.dll")] static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] static extern bool IsWindowVisible(IntPtr h);
  // Surece ait gorunur #32770 (mesaj kutusu) metnini dondurur; yoksa null.
  public static string Oku(int pid) {
    string sonuc = null;
    EnumWindows(delegate(IntPtr h, IntPtr l) {
      uint p; GetWindowThreadProcessId(h, out p);
      if (p != (uint)pid || !IsWindowVisible(h)) return true;
      StringBuilder c = new StringBuilder(64); GetClassName(h, c, 64);
      if (c.ToString() != "#32770") return true;
      StringBuilder t = new StringBuilder(256); GetWindowText(h, t, 256);
      List<string> parca = new List<string>(); parca.Add("[" + t.ToString() + "]");
      EnumChildWindows(h, delegate(IntPtr k, IntPtr l2) {
        StringBuilder x = new StringBuilder(2048); GetWindowText(k, x, 2048);
        if (x.Length > 0) parca.Add(x.ToString()); return true; }, IntPtr.Zero);
      sonuc = string.Join(" | ", parca.ToArray()); return false;
    }, IntPtr.Zero);
    return sonuc;
  }
}
"@
}

$t = 0
while (-not $p.HasExited -and $t -lt 900) {
    Start-Sleep 2; $t += 2
    $k = [KrDiyalog]::Oku($p.Id)
    if ($k) { "HATA KUTUSU (yol baglama): $k"; Stop-Process -Id $p.Id -Force; break }
}
if (-not $p.HasExited) { Stop-Process -Id $p.Id -Force; "ZAMAN ASIMI" }
Start-Sleep 1
Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
$L = Get-Content "$r\main\console.log"
"in solid       : " + ($L | Select-String 'in solid').Count
"no connections : " + ($L | Select-String 'no connections').Count
$L | Select-String 'in solid|no connections|bad node|script compile|runtime error|Error:' |
    Select-Object -First 20 | ForEach-Object Line
"yol kaydi      : " + (($L | Select-String 'Saving paths done').Count -gt 0)
