# tur.ps1 <onek> -- haritayi kr_tur 1 ile acar, her bakis noktasinda oyun
# penceresinin goruntusunu alir. Yuklemeden sonra sol tik (devam), 2 sn sonra
# N (noclip -- kullanicinin bind'i).
param([int]$Sure = 480, [string]$Test = "1")
$r = 'F:\Activision\Call of Duty 2'
Add-Type -AssemblyName System.Drawing
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
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hh, bool r);
  [DllImport("user32.dll")] public static extern bool GetCursorPos(out POINT p);
  // Oyun penceresi IKINCI ekrana (x=1920) tasinir; tiklamadan sonra odak ve imlec
  // kullanicinin onceki penceresine (birinci ekranda film) geri verilir.
  public static void Tasi(IntPtr h) { MoveWindow(h, 1920 + 300, 160, 1296, 758, true); }
  public static void Tikla(IntPtr h) {
    IntPtr onceki = GetForegroundWindow(); POINT eski; GetCursorPos(out eski);
    RECT r; GetWindowRect(h, out r); SetForegroundWindow(h);
    SetCursorPos((r.L + r.R) / 2, (r.T + r.B) / 2);
    mouse_event(2, 0, 0, 0, 0); System.Threading.Thread.Sleep(60); mouse_event(4, 0, 0, 0, 0);
    System.Threading.Thread.Sleep(2000);
    // kullanici: hem N hem G (noclip + god)
    keybd_event(0x4E, 0, 0, 0); System.Threading.Thread.Sleep(80); keybd_event(0x4E, 0, 2, 0);
    System.Threading.Thread.Sleep(300);
    keybd_event(0x47, 0, 0, 0); System.Threading.Thread.Sleep(80); keybd_event(0x47, 0, 2, 0);
    System.Threading.Thread.Sleep(300);
    if (onceki != IntPtr.Zero && onceki != h) SetForegroundWindow(onceki);
    SetCursorPos(eski.X, eski.Y);
  }
  public static void Tus(IntPtr h, byte vk) {
    SetForegroundWindow(h);
    keybd_event(vk, 0, 0, 0); System.Threading.Thread.Sleep(80); keybd_event(vk, 0, 2, 0);
  }
  public static int[] Istemci(IntPtr h) {
    RECT c; GetClientRect(h, out c); POINT p = new POINT(); ClientToScreen(h, ref p);
    return new int[] { p.X, p.Y, c.R - c.L, c.B - c.T };
  }
}
"@
function Yakala($h, $yol) {
    $a = [KrFare]::Istemci($h)
    $bmp = New-Object System.Drawing.Bitmap $a[2], $a[3]
    $g = [System.Drawing.Graphics]::FromImage($bmp)
    $g.CopyFromScreen($a[0], $a[1], 0, 0, $bmp.Size)
    $bmp.Save($yol, [System.Drawing.Imaging.ImageFormat]::Png)
    $g.Dispose(); $bmp.Dispose()
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

Get-Process CoD2SP_s -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1
# SAFE MODE TUZAGI: zorla kapatilan oyun __CoD2SP_s isaretini birakir (olculdu).
Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
Remove-Item "$r\main\console.log" -ErrorAction SilentlyContinue
$arg = "+set r_fullscreen 0 +set r_mode 1280x720 +set developer 1 +set logfile 2 +set snd_volume 0.7 +set r_displayRefresh 165 +set vid_xpos 0 +set vid_ypos 0 +set thereisacow 1337 +set com_introplayed 1 +set kr_test $Test +devmap burya"
Remove-Item "$r\main\console.log" -ErrorAction SilentlyContinue
$p = Start-Process -FilePath "$r\CoD2SP_s.exe" -WorkingDirectory $r -ArgumentList $arg -PassThru
$log = "$r\main\console.log"; $t = 0; $tiklandi = $false; $durum = "ZAMAN ASIMI"
while ($t -lt $Sure) {
    Start-Sleep 1; $t++
    if ($p.HasExited) { $durum = "OYUN KAPANDI"; break }
    $k = [KrDiyalog]::Oku($p.Id)
    if ($k) { $durum = "HATA KUTUSU: $k"; break }
    if (-not $tiklandi -and (Test-Path $log) -and (Select-String $log -Pattern 'Load time:' -Quiet)) {
        Start-Sleep 3; $p.Refresh()
        if ($p.MainWindowHandle -ne [IntPtr]::Zero) { [KrFare]::Tikla($p.MainWindowHandle); $tiklandi = $true }
    }
    if ((Test-Path $log) -and (Select-String $log -Pattern 'kr_log GOREV TAMAM' -Quiet)) { Start-Sleep 2; $durum = 'BOLUM TAMAMLANDI'; break }
}
"durum: $durum ($t sn)"
Get-Content $log | Select-String 'kr_log|script runtime error|unknown sound' | Select-Object -Last 40 | ForEach-Object Line
Get-Content $log | Select-String -Pattern 'script runtime error' -Context 0,10 | Select-Object -First 1 | ForEach-Object { $_.Context.PostContext }
Stop-Process -Id $p.Id -Force -ErrorAction SilentlyContinue
Start-Sleep 1
Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
