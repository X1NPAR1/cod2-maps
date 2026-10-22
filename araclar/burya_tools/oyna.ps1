# oyna.ps1 <onek> <sure_sn> -- haritayi NORMAL acar (tur yok), tiklar, araliklarla
# ekran alir; sonunda log denetimi. Oyuncuya dokunmaz (god/noclip yok).
param([string]$Onek = "oyun", [int]$Sure = 90, [int]$Aralik = 15, [string]$Ek = "")
$r = 'F:\Activision\Call of Duty 2'
Add-Type -AssemblyName System.Drawing
if (-not ([System.Management.Automation.PSTypeName]'KrFare').Type) {
Add-Type @"
using System; using System.Runtime.InteropServices;
public class KrFare {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool GetClientRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref POINT p);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int f, int x, int y, int d, int e);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte sc, int f, int e);
  public struct RECT { public int L, T, R, B; }
  public struct POINT { public int X, Y; }
  public static void Tikla(IntPtr h) {
    RECT r; GetWindowRect(h, out r); SetForegroundWindow(h);
    SetCursorPos((r.L + r.R) / 2, (r.T + r.B) / 2);
    mouse_event(2, 0, 0, 0, 0); System.Threading.Thread.Sleep(60); mouse_event(4, 0, 0, 0, 0);
  }
  public static int[] Istemci(IntPtr h) {
    RECT c; GetClientRect(h, out c); POINT p = new POINT(); ClientToScreen(h, ref p);
    return new int[] { p.X, p.Y, c.R - c.L, c.B - c.T };
  }
}
"@
}

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
function Yakala($h, $yol) {
    $a = [KrFare]::Istemci($h)
    $bmp = New-Object System.Drawing.Bitmap $a[2], $a[3]
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($a[0], $a[1], 0, 0, $bmp.Size)
    $bmp.Save($yol, [System.Drawing.Imaging.ImageFormat]::Png); $g.Dispose(); $bmp.Dispose()
}
Get-Process CoD2SP_s -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1
Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
Remove-Item "$r\main\console.log" -ErrorAction SilentlyContinue
$arg = "+set r_fullscreen 0 +set r_mode 1280x720 +set developer 1 +set logfile 2 +set thereisacow 1337 +set com_introplayed 1 $Ek +devmap burya"
$p = Start-Process -FilePath "$r\CoD2SP_s.exe" -WorkingDirectory $r -ArgumentList $arg -PassThru
$log = "$r\main\console.log"
$global:DIYALOG = $null
function HataVar() {
    $d = [KrDiyalog]::Oku($p.Id)
    if ($d) { $global:DIYALOG = $d; return $true }   # olumcul hata loga DUSMEZ (olculdu) -> kutudan oku
    (Test-Path $log) -and (Select-String $log -Pattern 'script runtime error|script compile error' -Quiet)
}
function TamEkran($yol) { & "$r\burya_tools\ekran.ps1" $yol | Out-Null }
# yukleme: 3 sn'de bir tikla; ILK tiktan 3 sn sonra ekran al (kullanici istegi)
$t = 0; $ilk = $false; $hata = $false
while ($t -lt 150) {
    Start-Sleep 1; $t++
    if (HataVar) { Start-Sleep 1; TamEkran "$r\burya_tools\ekran\${Onek}_HATA.png"; $hata = $true; "HATA YAKALANDI ($t sn) -> ${Onek}_HATA.png"; break }
    if ($p.HasExited) { "OYUN KAPANDI ($t sn)"; break }
    if ($t -gt 12 -and ($t % 3 -eq 0)) {
        $p.Refresh()
        if ($p.MainWindowHandle -ne [IntPtr]::Zero) {
            [KrFare]::Tikla($p.MainWindowHandle)
            if (-not $ilk) { $ilk = $true; Start-Sleep 3; TamEkran "$r\burya_tools\ekran\${Onek}_tik3sn.png"; "tik +3 sn ekran alindi" }
        }
    }
    if ($ilk -and $t -gt 30) { break }
}
"yuklendi ~$t sn"
$i = 0
if (-not $hata) {
  for ($s = 0; $s -lt $Sure; $s += 1) {
    if (HataVar) { Start-Sleep 1; TamEkran "$r\burya_tools\ekran\${Onek}_HATA.png"; "HATA YAKALANDI -> ${Onek}_HATA.png"; break }
    if ($p.HasExited) { "OYUN KAPANDI"; break }
    if ($s % $Aralik -eq 0) { $i++; $p.Refresh(); Yakala $p.MainWindowHandle ("$r\burya_tools\ekran\{0}_{1}.png" -f $Onek, $i) }
    Start-Sleep 1
  }
}
$L = Get-Content $log
"--- denetim ---"
if ($global:DIYALOG) { "HATA KUTUSU: " + $global:DIYALOG }
"betik hatasi   : " + ($L | Select-String 'script compile error|script runtime error|Error:').Count
"bilinmeyen ses : " + ($L | Select-String -SimpleMatch 'unknown sound alias').Count
$L | Select-String 'script compile error|script runtime error|Error:|unknown sound|Could not find sound|undefined|not an entity' |
    Select-Object -First 25 | ForEach-Object Line
"--- HATA BLOKLARI ---"
$L | Select-String -Pattern 'script (runtime|compile) error' -Context 0,16 | Select-Object -First 3 | ForEach-Object { $_.Line; $_.Context.PostContext }
Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
Start-Sleep 1
Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
"bitti"
