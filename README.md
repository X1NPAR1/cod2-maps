# Call of Duty 2 — Sovyet Tek Oyunculu Haritaları

İki bölümlük, birbirini izleyen özel tek oyunculu harita.

| Sıra | Harita | Bölüm | Tarih |
|---|---|---|---|
| 1 | `krasnoye` | Krasnoye Kolhozu — köyü temizle ve savun | 14 Aralık 1942 |
| 2 | `metel` | Operatsiya Metel — karakol ve iki havan mevzisi | 8 Ocak 1943 |

`krasnoye` bitince oyun otomatik olarak `metel` bölümünü yükler.

## Kurulum

1. `main/` klasörünün içeriğini oyunun `main/` klasörüne kopyalayın (`maps`, `soundaliases`, `localizedstrings`, `sun`).
2. Oyunu geliştirici haritası olarak başlatın: `CoD2SP_s.exe +set thereisacow 1337 +devmap krasnoye` (ya da doğrudan `+devmap metel`).

Oyunun 1.3 yamasıyla test edildi. Stok iwd dosyaları dışında başka bir şey gerekmez.

## Bölümler

**Krasnoye:** Teğmen Leonov ve 8 kişilik ekiple karlı bir kolhoz köyü temizlenir. Ardından kamyon, yarı paletli ve Panzer II saldırısı püskürtülür; tank yapışkan bombayla imha edilir.

**Metel:**
1. Önce A, iki katlı Alman karakolu ele geçirilir.
2. Sonra B ve C havan mevzileri, istenen sırayla temizlenir.
3. Ardından karakol 50 piyade, bir kamyon ve iki yarı paletliye karşı savunulur.
4. En sonda ekip avluda Leonov'un etrafında toplanır.

## Kaynak ve araçlar

- `map_source/*.map`: Üretilmiş Radiant kaynakları (`iwmap 4`).
- `araclar/<harita>_tools/`: Haritayı sıfırdan üreten Python üreticileri, derleme ve doğrulama betikleri.
  - `gen_*.py` + `ent_*.py`: geometri ve yerleşim.
  - `ses_kur.py`: ses alias'ları ve görev metinleri.
  - `derle.bat` / `dogrula.ps1`: derleme ve AI yol bağlama.
  - `yol_denetim.py`: Derlenmiş haritadaki AI yol ağını çözer, başlangıçtan ulaşılamayan noktaları raporlar.

Yollar betiklerde `F:\Activision\Call of Duty 2` olarak sabit yazılıdır; başka bir kurulumda düzenleyin.
