# ekran.ps1 <cikti.png> -- tum ekrani (birincil monitor) yakalar.
param([string]$Cikti = "F:\Activision\Call of Duty 2\krasnoye_tools\ekran\son.png")
Add-Type -AssemblyName System.Windows.Forms, System.Drawing
$d = Split-Path $Cikti
if (-not (Test-Path $d)) { New-Item -ItemType Directory -Force $d | Out-Null }
$s = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap $s.Width, $s.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($s.Location, [System.Drawing.Point]::Empty, $s.Size)
$bmp.Save($Cikti, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
"kaydedildi: $Cikti ($($s.Width)x$($s.Height))"
