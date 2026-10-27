// Kurulum.cs -- CoD2 tek oyunculu haritalar kurulum programi.
// Gomulu haritalar.zip'i secilen Call of Duty 2 klasorunun main\ altina acar,
// masaustune dogrudan krasnoye ile baslayan bir kisayol koyar.
// Derleme: kurulum\derle.ps1
using System;
using System.Collections.Generic;
using System.Drawing;
using System.IO;
using System.IO.Compression;
using System.Reflection;
using System.Windows.Forms;
using Microsoft.Win32;

class Kurulum : Form
{
    const string BASLIK = "CoD2 Haritalar - Kurulum";
    const string ILK_HARITA = "krasnoye";
    const string KAYIT = "cod2_haritalar_kurulum.txt";   // main\ altinda kurulan dosyalarin listesi
    TextBox yolKutu;
    Label durum;
    ProgressBar ilerleme;
    Button kurDugme, kaldirDugme;
    CheckBox kisayolKutu;

    [STAThread]
    static void Main()
    {
        Application.EnableVisualStyles();
        Application.Run(new Kurulum());
    }

    Kurulum()
    {
        Text = BASLIK;
        FormBorderStyle = FormBorderStyle.FixedDialog;
        MaximizeBox = false;
        StartPosition = FormStartPosition.CenterScreen;
        ClientSize = new Size(560, 330);
        Font = new Font("Segoe UI", 9.5f);

        var baslik = new Label {
            Text = "Call of Duty 2 - Tek Oyunculu Haritalar",
            Font = new Font("Segoe UI", 13f, FontStyle.Bold),
            Location = new Point(20, 16), AutoSize = true };
        var aciklama = new Label {
            Text = "Alti bolum sirayla oynanir:\r\n" +
                   "krasnoye > metel > burya > kumtepe > kasrelbab > sidirezegh > jenerik\r\n\r\n" +
                   "Call of Duty 2'nin kurulu oldugu ana klasoru secin (icinde CoD2SP_s.exe olan klasor).",
            Location = new Point(22, 50), Size = new Size(520, 80) };
        yolKutu = new TextBox { Location = new Point(22, 136), Width = 420, Text = KlasorBul() };
        var gozat = new Button { Text = "Gozat...", Location = new Point(450, 134), Width = 88 };
        gozat.Click += delegate { Gozat(); };
        kisayolKutu = new CheckBox {
            Text = "Masaustune \"CoD2 Haritalar\" kisayolu olustur (dogrudan ilk bolumu baslatir)",
            Location = new Point(22, 170), AutoSize = true, Checked = true };
        ilerleme = new ProgressBar { Location = new Point(22, 205), Width = 516, Height = 18 };
        durum = new Label { Location = new Point(22, 230), Size = new Size(516, 44) };
        kurDugme = new Button { Text = "Kur", Location = new Point(352, 282), Width = 90, Height = 30 };
        kurDugme.Click += delegate { Kur(); };
        kaldirDugme = new Button { Text = "Kaldir", Location = new Point(448, 282), Width = 90, Height = 30 };
        kaldirDugme.Click += delegate { Kaldir(); };
        Controls.AddRange(new Control[] { baslik, aciklama, yolKutu, gozat, kisayolKutu, ilerleme, durum, kurDugme, kaldirDugme });
    }

    // kayit defteri ve bilinen yerlerden CoD2 klasorunu tahmin et
    static string KlasorBul()
    {
        string[] anahtarlar = {
            @"SOFTWARE\WOW6432Node\Activision\Call of Duty 2",
            @"SOFTWARE\Activision\Call of Duty 2" };
        foreach (var a in anahtarlar)
        {
            try
            {
                using (var k = Registry.LocalMachine.OpenSubKey(a))
                {
                    if (k == null) continue;
                    var y = k.GetValue("InstallPath") as string;
                    if (y != null && GecerliMi(y)) return y;
                }
            }
            catch { }
        }
        var adaylar = new List<string> {
            @"C:\Program Files (x86)\Activision\Call of Duty 2",
            @"C:\Program Files\Activision\Call of Duty 2",
            @"C:\Program Files (x86)\Steam\steamapps\common\Call of Duty 2" };
        foreach (var d in DriveInfo.GetDrives())
        {
            if (d.DriveType != DriveType.Fixed) continue;
            adaylar.Add(Path.Combine(d.Name, @"Activision\Call of Duty 2"));
            adaylar.Add(Path.Combine(d.Name, @"Games\Call of Duty 2"));
            adaylar.Add(Path.Combine(d.Name, @"SteamLibrary\steamapps\common\Call of Duty 2"));
        }
        foreach (var y in adaylar)
            if (GecerliMi(y)) return y;
        return "";
    }

    static bool GecerliMi(string y)
    {
        try
        {
            return !string.IsNullOrEmpty(y) && File.Exists(Path.Combine(y, "CoD2SP_s.exe"))
                   && Directory.Exists(Path.Combine(y, "main"));
        }
        catch { return false; }
    }

    void Gozat()
    {
        using (var f = new FolderBrowserDialog())
        {
            f.Description = "Call of Duty 2 ana klasorunu secin (CoD2SP_s.exe'nin oldugu klasor)";
            if (Directory.Exists(yolKutu.Text)) f.SelectedPath = yolKutu.Text;
            if (f.ShowDialog(this) == DialogResult.OK) yolKutu.Text = f.SelectedPath;
        }
    }

    bool KlasorDenetle(string y)
    {
        if (GecerliMi(y)) return true;
        MessageBox.Show(this, "Secilen klasorde CoD2SP_s.exe ve main klasoru bulunamadi.\r\n" +
            "Lutfen Call of Duty 2'nin ana klasorunu secin.", BASLIK, MessageBoxButtons.OK, MessageBoxIcon.Warning);
        return false;
    }

    void Kur()
    {
        string y = yolKutu.Text.Trim();
        if (!KlasorDenetle(y)) return;
        string main = Path.Combine(y, "main");
        kurDugme.Enabled = kaldirDugme.Enabled = false;
        try
        {
            var kurulan = new List<string>();
            using (var akis = Assembly.GetExecutingAssembly().GetManifestResourceStream("haritalar.zip"))
            using (var zip = new ZipArchive(akis, ZipArchiveMode.Read))
            {
                ilerleme.Maximum = zip.Entries.Count;
                ilerleme.Value = 0;
                foreach (var e in zip.Entries)
                {
                    ilerleme.Value++;
                    if (string.IsNullOrEmpty(e.Name)) continue;           // klasor girdisi
                    string hedef = Path.GetFullPath(Path.Combine(main, e.FullName));
                    if (!hedef.StartsWith(Path.GetFullPath(main), StringComparison.OrdinalIgnoreCase))
                        continue;                                          // klasor disina yazma yok
                    Directory.CreateDirectory(Path.GetDirectoryName(hedef));
                    durum.Text = "Kopyalaniyor: " + e.FullName;
                    Application.DoEvents();
                    e.ExtractToFile(hedef, true);
                    kurulan.Add(e.FullName);
                }
            }
            File.WriteAllLines(Path.Combine(main, KAYIT), kurulan.ToArray());
            if (kisayolKutu.Checked)
                KisayolYap(y);
            durum.Text = "Kurulum tamamlandi (" + kurulan.Count + " dosya).";
            MessageBox.Show(this,
                "Kurulum tamamlandi.\r\n\r\n" +
                (kisayolKutu.Checked ? "Masaustundeki \"CoD2 Haritalar\" kisayoluyla dogrudan baslayabilirsiniz.\r\n\r\n" : "") +
                "Ya da oyunda konsolu (~) acip sunu yazin:\r\n    devmap " + ILK_HARITA + "\r\n\r\n" +
                "Diger bolumler sirayla kendiliginden gelir.",
                BASLIK, MessageBoxButtons.OK, MessageBoxIcon.Information);
        }
        catch (UnauthorizedAccessException)
        {
            durum.Text = "Yazma izni yok.";
            MessageBox.Show(this, "Bu klasore yazma izni yok. Kurulumu sag tik > \"Yonetici olarak calistir\" ile tekrar deneyin.",
                BASLIK, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
        catch (Exception ex)
        {
            durum.Text = "Hata: " + ex.Message;
            MessageBox.Show(this, "Kurulum basarisiz:\r\n" + ex.Message, BASLIK, MessageBoxButtons.OK, MessageBoxIcon.Error);
        }
        finally
        {
            kurDugme.Enabled = kaldirDugme.Enabled = true;
        }
    }

    // masaustu kisayolu: konsol acik, gelistirici haritasi olarak ilk bolum
    static void KisayolYap(string y)
    {
        string masaustu = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
        string lnk = Path.Combine(masaustu, "CoD2 Haritalar.lnk");
        Type t = Type.GetTypeFromProgID("WScript.Shell");
        dynamic sh = Activator.CreateInstance(t);
        dynamic k = sh.CreateShortcut(lnk);
        k.TargetPath = Path.Combine(y, "CoD2SP_s.exe");
        k.Arguments = "+set monkeytoy 0 +set thereisacow 1337 +devmap " + ILK_HARITA;
        k.WorkingDirectory = y;
        k.IconLocation = Path.Combine(y, "CoD2SP_s.exe") + ",0";
        k.Description = "Call of Duty 2 - Tek Oyunculu Haritalar";
        k.Save();
    }

    void Kaldir()
    {
        string y = yolKutu.Text.Trim();
        if (!KlasorDenetle(y)) return;
        string main = Path.Combine(y, "main");
        string kayit = Path.Combine(main, KAYIT);
        if (!File.Exists(kayit))
        {
            MessageBox.Show(this, "Bu klasorde kurulum kaydi bulunamadi.", BASLIK, MessageBoxButtons.OK, MessageBoxIcon.Information);
            return;
        }
        if (MessageBox.Show(this, "Kurulan harita dosyalari silinsin mi? (Oyunun kendi dosyalarina dokunulmaz.)",
                BASLIK, MessageBoxButtons.YesNo, MessageBoxIcon.Question) != DialogResult.Yes)
            return;
        int n = 0;
        foreach (var g in File.ReadAllLines(kayit))
        {
            string f = Path.GetFullPath(Path.Combine(main, g));
            if (f.StartsWith(Path.GetFullPath(main), StringComparison.OrdinalIgnoreCase) && File.Exists(f))
            {
                File.Delete(f);
                n++;
            }
        }
        File.Delete(kayit);
        string lnk = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory), "CoD2 Haritalar.lnk");
        if (File.Exists(lnk)) File.Delete(lnk);
        durum.Text = n + " dosya kaldirildi.";
        MessageBox.Show(this, "Haritalar kaldirildi (" + n + " dosya).", BASLIK, MessageBoxButtons.OK, MessageBoxIcon.Information);
    }
}
