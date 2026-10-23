# Call of Duty 2 — Tek Oyunculu Haritalar

Birbirini izleyen özel tek oyunculu haritalar: üç Sovyet bölümü ve iki İngiliz bölümü.

| Sıra | Harita | Bölüm | Tarih |
|---|---|---|---|
| 1 | `krasnoye` | Krasnoye Kolhozu — köyü temizle ve savun | 14 Aralık 1942 |
| 2 | `metel` | Operatsiya Metel — karakol ve iki havan mevzisi | 8 Ocak 1943 |
| 3 | `burya` | Operation Snowstorm (Kar Fırtınası) — konvoy pususu, Alman kampı, üç patlayıcı | 2 Şubat 1943 |
| 4 | `kumtepe` | Operation Sandstorm — çöl köyü, Panzer saldırısı, Crusader kurtarması (İngiliz) | 24 Ekim 1942 |
| 5 | `kasrelbab` | Operation Silent Dawn — gizlenme, telsiz, surlu kasaba baskını, flak imhası (İngiliz) | 2 Kasım 1942 |

Bölümler sırayla yüklenir: `krasnoye` → `metel` → `burya` → `kumtepe` → `kasrelbab` → jenerik.

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

**Burya:**
1. Oyuncu Leonov'un kamyonunun kasasında konvoyla ilerler; arkadaki kamyon köprüde mayına basar, geri dönüş kapanır, 10 Alman pusuya düşürür.
2. Kamp girişindeki 10 Alman ve iki kuledeki MG42'ler, takviye kamyonu gelene kadar görünmeyen yerlerden yeniden doğar; takviye (9 kişi) gelince ya da oyuncu kampa girince herkes içeri hücum eder.
3. Kamp içi ve binalar temizlenir; ardından ormanın her yönünden 50 Almanlık karşı saldırı gelir. Sovyetler karakol binasının pencerelerine, iki kişi el merdiveniyle kulelere, biri üst kat MG'sine geçer; bomba evinde 7 Sovyet savunur.
4. Üç patlayıcı kurulur, 20 sn'lik sayaç başlar; Sovyetler kamptan çekilip çömelerek izler, oyuncu çıkınca binalarda Almanlar belirir.
5. Ardışık patlamalarda binalar çöker, kuleler devrilir, kamp kamyonu yanar; Leonov'un sözleriyle bölüm biter.

**Kumtepe (İngiliz, El Alamein):**
1. Akşam, kumlu ve sisli çölde Cpt. Price ve 7 İngilizle kamyonun kasasında köye gelinir; yolda bir Stuka yola dalıp ateş eder.
2. Dört binalı köydeki 15 Alman temizlenir; ardından 30 sn'de bir 10'arlı dalgalar ve dört yönden yarı paletliler gelir.
3. Dört Panzer II batı vadisinden gelir; bir Stuka kapalı evin köşesini bombalar, Panzer'ler iki katlı evi iki atışta yıkar.
4. Telsizle yardım istenir; Crusader'lar gelir, biri vurulur, diğerleri Panzer'leri patlatır; 15 İngiliz köye dağılır.
5. Price meydanda askerlerin oluşturduğu halkada zafer konuşmasını yapar.

**Kasr el-Bab (İngiliz, Mısır, şafak):**
1. Oyuncu sırttaki çalılıkta yatarak gizlenir; Alman konvoyu (2 Blitz, yarı paletli, Panzer II) önünden geçer. Ayağa kalkarsa ya da çalıdan çıkarsa fark edilir.
2. Kulübedeki telsizciyi öldürür, telsizle yardım çağırır; 20 sn sonra Price ve 12 İngiliz, ardından 5 Crusader gelir.
3. Price'la buluşulur, ekip Crusader hattına gider; oyuncu kapıya yaklaşınca Crusader sur MG'lerini ve büyük kapıyı vurur, kanatlar yere devrilir, herkes kasabaya dalar.
4. Kasaba temizlenir; üç flak 88 TNT ile istenen sırayla patlatılır.
5. Doğudan 10 Alman saldırır, ardından gelen Panzer II'ye yapışkan bomba yapıştırılır (140 sn içinde patlatılmazsa iki İngiliz tırmanıp patlatır).
6. Price kamyonu kontrol edip sürücü koltuğuna geçer, iki asker kasaya atlar; kamyon batı kapısından çıkar ve bölüm biter.

## Kaynak ve araçlar

- `map_source/*.map`: Üretilmiş Radiant kaynakları (`iwmap 4`).
- `araclar/<harita>_tools/`: Haritayı sıfırdan üreten Python üreticileri, derleme ve doğrulama betikleri.
  - `gen_*.py` + `ent_*.py`: geometri ve yerleşim.
  - `ses_kur.py`: ses alias'ları ve görev metinleri.
  - `derle.bat` / `dogrula.ps1`: derleme ve AI yol bağlama.
  - `yol_denetim.py`: Derlenmiş haritadaki AI yol ağını çözer, başlangıçtan ulaşılamayan noktaları raporlar.

Yollar betiklerde `F:\Activision\Call of Duty 2` olarak sabit yazılıdır; başka bir kurulumda düzenleyin.
