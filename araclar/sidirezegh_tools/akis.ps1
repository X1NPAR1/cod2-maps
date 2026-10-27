# akis.ps1 -- kr_tur 2 gorev akisi testi: oyunu acar, yukleme sonrasi tek sol tik
$r = 'F:\Activision\Call of Duty 2'
Add-Type @"
using System; using System.Runtime.InteropServices;
public class KrTik {
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int f, int x, int y, int d, int e);
  public struct RECT { public int L, T, R, B; }
  public static void Tikla(IntPtr h) { RECT r; GetWindowRect(h, out r); SetForegroundWindow(h);
    SetCursorPos((r.L + r.R) / 2, (r.T + r.B) / 2); mouse_event(2,0,0,0,0); System.Threading.Thread.Sleep(60); mouse_event(4,0,0,0,0); }
}
"@
Get-Process CoD2SP_s -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep 1
Remove-Item "$r\__CoD2SP_s" -Force -ErrorAction SilentlyContinue
Remove-Item "$r\main\console.log" -ErrorAction SilentlyContinue
$p = Start-Process -FilePath "$r\CoD2SP_s.exe" -WorkingDirectory $r -PassThru -ArgumentList '+set r_fullscreen 0 +set r_mode 1280x720 +set developer 1 +set logfile 2 +set snd_volume 0 +set mus_volume 0 +set thereisacow 1337 +set com_introplayed 1 +set kr_tur 2 +devmap sidirezegh'
for ($i = 0; $i -lt 240; $i++) {
  Start-Sleep 1
  if ((Test-Path "$r\main\console.log") -and (Select-String -Path "$r\main\console.log" -Pattern 'Load time' -Quiet)) { break }
}
Start-Sleep 3
$p.Refresh(); [KrTik]::Tikla($p.MainWindowHandle)
"tiklandi"
