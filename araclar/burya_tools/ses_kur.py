# -*- coding: utf-8 -*-
"""
ses_kur.py -- burya ses alias'lari + gorev metinleri.

Krasnoye dersi ("unknown sound alias" iki kez oyunu durdurdu): stok alias'lar
loadspec ile kendi bolumlerine kisitli. Bu arac:
  1) Leonov/asker/muzik alias'larini loadspec 'metel' kopyasi olarak yazar,
  2) metel*.gsc + kullanilan stok betiklerdeki (_mortar) TUM ses adlarini tarar;
     her biri ya bizim csv'de ya da stokta loadspec'i BOS olmali -> degilse kopyalar,
  3) her wav/mp3'un iwd'de, her altyazi referansinin subtitle.str'de oldugunu dogrular.
Leonov'un sesi krasnoye ile ayni: Tegmen Volsky (stok, Turkce altyazili).
"""
import csv, io, os, re, zipfile, glob

ANA = r'F:\Activision\Call of Duty 2\main'
HAM = r'F:\Activision\cod2_analiz\ham'
HARITA = 'burya'

LEONOV = {   # replik -> stok alias (Turkce altyazili; null.wav OLMAZ -- olculdu: sessiz kaliyordu)
    'giris':     'downtownassault_volsky_movein',             # Hadi yurttaslar! Bize kesin sonuc gerek!
    'pusu':      'downtownassault_volsky_takecover',          # Siper alin!
    'ilerle':    'downtownsniper_volsky_letsmoveon',          # Ilerleyelim
    'kamp':      'downtownassault_volsky_germanhardpoint',    # Alman mevzisi
    'mg':        'downtownsniper_volsky_mg42frontlinesloud',  # MG42 kullanimina gectiler
    'savun':     'cityhall_vsk_wemusthold',                   # Dayanmaliyiz
    'saldiri':   'downtownsniper_volsky_preparecounter',      # Karsi atagini puskurtmeliyiz! Savunma pozisyonuna!
    'geliyorlar': 'downtownsniper_volsky_startingattackloud', # Saldiri baslatiyorlar!
    'temizle':   'downtownassault_volsky_clearapt1',          # Bina temizlenmeli! Kattan kata!
    'geri':      'downtownsniper_volsky_enemyretreating',     # Dusman geri cekiliyor!
    'kamp_bizde': 'downtownassault_volsky_backinsoviethands', # Yeniden Sovyet elinde
    'bomba':     'demolition_rs1_helpusout',                  # bomba al, guzel bir surpriz ayarla
    'final1':    'cityhall_vsk_takenit',                      # Onu aldik! Tebrikler
    'final2':    'cityhall_vsk_tomorrow',                     # Yarin ...
}
ASKER = {
    'vuruldu':   'demolition_rs4_getdownnn',                  # Yere yatin!
    'takviye':   'downtownsniper_rs1_reinforcementscoming1',  # Takviye geliyor
    'kac1':      'demolition_rs4_safedistance',               # Guvenli mesafeye
    'kac2':      'demolition_rs1_abouttoblow',                # Patlamak uzere
    'kac3':      'demolition_rs4_moveitrun',                  # Kosun!
    'kac4':      'demolition_rs3_letsgoletsgo',               # Haydi haydi
    'oksur1':    'demolition_rs1_coughing',
    'oksur2':    'demolition_rs4_coughing',
    'oksur3':    'demolition_rs3_coughing',
}
MUZIK = {   # burya_muzik_X -> stok alias ; TEK_SEFER disindakiler dongude
    'giris':    'soviet_datestamp_ominous01',
    'yolculuk': 'soviet_tension_light01',
    'pusu':     'soviet_tension_medium01',
    'kamp':     'soviet_charge01',
    'savunma':  'soviet_holdline_soft',
    'bomba':    'soviet_cresc01',
    'final':    'soviet_victory_serious01',
}
TEK_SEFER = ('giris', 'bomba')
GOREV = [
    ('OBJ_KONVOY', "Konvoyla birlikte ilerle ve Alman karakoluna ulaş."),
    ('OBJ_PUSU', "Siper alın! Alman saldırısını püskürt."),
    ('OBJ_KAMP', "Alman kampına ilerle."),
    ('OBJ_GIRIS', "Kamp girişindeki Almanları baskı altında tut: Sovyet takviyeleri gelene kadar dayan."),
    ('OBJ_SAVUN', "Alman karşı saldırısını püskürt! Kampı savun."),
    ('OBJ_ELE', "Takviyelerle birlikte kampa bastır: binaları ve karakolu temizle."),
    ('OBJ_BEKLE', "Kamp kontrol altında. Leonov'un emirlerini bekle."),
    ('OBJ_BOMBA', "Kampa üç patlayıcı yerleştir: merkez bina, depo, baraka."),
    ('OBJ_KAC', "Patlamadan önce kamptan uzaklaş!"),
    ('OBJ_LEONOV', "Leonov'un yanına git."),
    ('MSG_TAKVIYE', "Sovyet takviyeleri geldi!"),
    ('BITTI', "Kar Fırtınası Harekatı tamamlandı."),
    ('INTRO_TITLE', '"Operation Snowstorm"'),
    ('INTRO_PLACE', "Kotelnikovo Kuzeyi, Don Cephesi, S.S.C.B."),
    ('INTRO_DATE', "2 Şubat 1943"),
    ('INTRO_INFO', "3. Muhafız Ordusu, Leonov Takımı, Saat 07:40"),
]

def tr(s):
    for a, b in (('ş', 's'), ('Ş', 'S'), ('ğ', 'g'), ('Ğ', 'G'), ('ı', 'i'), ('İ', 'I')):
        s = s.replace(a, b)
    return s

def alias_oku(dosya):
    rows = list(csv.reader(io.open(os.path.join(HAM, 'soundaliases', dosya), encoding='latin-1')))
    hdr, d = None, {}
    for r in rows:
        if not r or r[0].startswith('#'):
            continue
        if r[0] == 'name':
            hdr = r; continue
        if hdr:
            d.setdefault(r[0].lower(), []).append(dict(zip(hdr, r)))
    return hdr, d

def main():
    hdr = None; stok = {}
    for f in sorted(glob.glob(os.path.join(HAM, 'soundaliases', '*.csv'))):
        h, d = alias_oku(os.path.basename(f))
        if h and 'loadspec' in h:
            hdr = hdr or h
            for k, v in d.items():
                stok.setdefault(k, []).extend(v)
    satir = [','.join(hdr)]
    yazilan = set()
    def ekle(yeni, kaynak, ek=None):
        gorulen = set()
        for row in kaynak:                      # sekans korunur; ayni dosyanin
            if row.get('file', '').lower() in gorulen:   # farkli loadspec satirlari tekrar YAZILMAZ
                continue                                 # (olculen: duplicate alias hatasi)
            gorulen.add(row.get('file', '').lower())
            a = dict(row); a['name'] = yeni; a['loadspec'] = HARITA
            if ek: a.update(ek)
            satir.append(','.join(a.get(k, '') for k in hdr))
        yazilan.add(yeni.lower())
    eksik = []
    for ad, src in LEONOV.items():
        if src not in stok: eksik.append(src); continue
        ekle(HARITA + '_leonov_' + ad, stok[src])          # stok kaydin kendi altyazisi
    for ad, src in ASKER.items():
        if src not in stok: eksik.append(src); continue
        ekle(HARITA + '_asker_' + ad, stok[src])
    for ad, src in MUZIK.items():
        if src not in stok: eksik.append(src); continue
        ekle(HARITA + '_muzik_' + ad, stok[src], None if ad in TEK_SEFER else {'loop': 'looping'})
    if eksik:
        raise SystemExit('STOK ALIAS YOK: %s' % eksik)

    # betiklerde gecen TUM ses adlari
    kod = ''
    for f in glob.glob(os.path.join(ANA, 'maps', HARITA + '*.gsc')):
        kod += open(f, encoding='latin-1').read()
    kod += open(os.path.join(HAM, 'maps', '_mortar.gsc'), encoding='latin-1').read()
    adaylar = set(re.findall(r'(?:playsound|playloopsound|musicplay|playSoundOnTag|scrsound\[[^\]]*\]\[[^\]]*\]\s*=)\s*\(?\s*"([A-Za-z0-9_]+)"', kod, re.I))
    adaylar |= set(re.findall(r'"(mortar_(?:incoming|explosion)\d)"', kod))
    adaylar |= {'mortar_incoming%d' % i for i in range(1, 4)} | {'mortar_explosion%d' % i for i in range(1, 6)}
    kopya = []
    for a in sorted(adaylar):
        al = a.lower()
        if al in yazilan or al.startswith(HARITA + '_'):
            continue
        if al not in stok:
            raise SystemExit('BETIKTE BILINMEYEN SES: %s' % a)
        if any(not r.get('loadspec', '').strip() for r in stok[al]):
            continue                            # stokta her haritada gecerli
        ekle(a, stok[al]); kopya.append(a)

    # ikincil alias'lar (secondaryaliasname) da ayni kurala tabi
    degisti = True
    while degisti:
        degisti = False
        for s_ in list(satir[1:]):
            r = dict(zip(hdr, next(csv.reader([s_]))))
            ik = (r.get('secondaryaliasname') or '').strip().lower()
            if not ik or ik in yazilan:
                continue
            if ik not in stok:
                raise SystemExit('IKINCIL ALIAS YOK: %s' % ik)
            if any(not x.get('loadspec', '').strip() for x in stok[ik]):
                yazilan.add(ik); continue
            ekle(ik, stok[ik]); kopya.append(ik); degisti = True

    # dogrulama: dosyalar ve altyazilar
    var = set(); alt = set()
    for p in glob.glob(os.path.join(ANA, '*.iwd')):
        z = zipfile.ZipFile(p)
        for n in z.namelist():
            var.add(n.lower())
            if n.lower().endswith('subtitle.str'):
                for m in re.finditer(r'REFERENCE\s+(\S+)', z.read(n).decode('latin-1')):
                    alt.add('SUBTITLE_' + m.group(1).upper())
    sorun = []
    for s_ in satir[1:]:
        r = dict(zip(hdr, next(csv.reader([s_]))))
        if r['name'].lower().startswith(HARITA + '_leonov_') and (r['file'].lower().endswith('null.wav') or not r.get('subtitle')):
            sorun.append('LEONOV SESSIZ/ALTYAZISIZ: %s %s' % (r['name'], r['file']))
        if r['file'] and ('sound/' + r['file']).lower() not in var:
            sorun.append('DOSYA YOK: %s %s' % (r['name'], r['file']))
        if r.get('subtitle') and r['subtitle'].upper() not in alt:
            sorun.append('ALTYAZI YOK: %s %s' % (r['name'], r['subtitle']))
    if sorun:
        raise SystemExit('\n'.join(sorun))

    with open(os.path.join(ANA, 'soundaliases', HARITA + '.csv'), 'w', encoding='latin-1', newline='\r\n') as f:
        f.write('\n'.join(satir) + '\n')
    o = ['VERSION             "1"', 'CONFIG              "C:\\trees\\cod2\\bin\\StringEd.cfg"',
         'FILENOTES           "%s"' % HARITA, '']
    for ref, t in GOREV:
        o += ['REFERENCE           %s' % ref, 'LANG_ENGLISH        "%s"' % tr(t), '']
    o.append('ENDMARKER')
    with open(os.path.join(ANA, 'localizedstrings', HARITA + '.str'), 'wb') as f:
        f.write('\r\n'.join(o).encode('cp1254') + b'\r\n')
    # Tus adi ([[{+activate}]]) yalniz *_platform.str metinlerinde cozulur
    # (stok tankhunt_platform.str gibi; olculdu: normal str'de ham gorundu)
    PLATFORM = [
        ('BOMBA_KUR', "Tuşa BAS: [&&1] Patlayıcıyı yerleştir."),
    ]
    o = ['VERSION             "1"', 'CONFIG              "C:\\trees\\cod2\\bin\\StringEd.cfg"',
         'FILENOTES           "%s platform"' % HARITA, '']
    for ref, t_ in PLATFORM:
        o += ['REFERENCE           %s' % ref, 'LANG_ENGLISH        "%s"' % tr(t_), '']
    o.append('ENDMARKER')
    with open(os.path.join(ANA, 'localizedstrings', HARITA + '_platform.str'), 'wb') as f:
        f.write('\r\n'.join(o).encode('cp1254') + b'\r\n')
    print('alias satiri: %d  stok kopya: %s  gorev metni: %d' % (len(satir) - 1, kopya, len(GOREV)))

if __name__ == '__main__':
    main()
