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
HARITA = 'sidirezegh'

LEONOV = {   # Cpt. Price replikleri (stok, Turkce altyazili; kumtepe'de oyunda dogrulandi)
    'giris':     'decoytrench_pri_bloodyhardfight',       # Cetin bir catismanin icindeyiz beyler!
    'savun':     'decoytown_pri_takeuppositions',         # Cevre boyunca pozisyonlara gecin!
    'kuzey':     'matmata_pri_jerriesonnorthwall',        # Almanlar kuzey duvarinda!
    'guney':     'matmata_pri_jerriesonsouthwall',        # Almanlar guney duvarinda!
    'dogu':      'matmata_pri_jerriestoeast',             # Almanlar dogudalar!
    'hucum':     'toujaneride_pri_pushingrally',          # Saldiriyi surdurelim! Gelin!
    'final1':    'matmata_pri_ending',                    # Tebrikler cocuklar! ...
    'final2':    'toujaneride_price_notbadsergeant',      # Fena degil Cavus!
    'kamyon':    'beltot_price_alrightchaps',             # Kamyon burada! Yuklemeye baslayin!
}
ASKER = {
    'panzer':    'alamein_bs3_panzertank',                # Panzer tank!
    'tamam':     'toujaneride_mcg_considerdone',
    'bizim':     'toujane_macgregor_oiourtanks',          # Onlar bizim ...!
}
MUZIK = {
    'giris':    'eldaba_intro_music',
    'savunma':  'matmata_antiaircraft',
    'tank':     'tank_closeinandduel_01',
    'kurtulus': 'relief_happy_01',
    'final':    'victory_seaofsand_01',
}
TEK_SEFER = ('giris', 'kurtulus', 'final')
GOREV = [
    ('OBJ_SAVUN', "Karargahı Alman saldırısına karşı savun."),
    ('OBJ_DALGA2', "İkinci dalga: zırhlı araçla geliyorlar!"),
    ('OBJ_DALGA3', "Üçüncü dalga: Panzer geliyor!"),
    ('OBJ_SCHRECK', "Karargahtaki Panzerschreck'i al."),
    ('OBJ_PANZER', "Panzer'i Panzerschreck ile yok et."),
    ('OBJ_PRICE', "Yüzbaşı Price'ın yanına git."),
    ('MSG_KURTARMA', "8. Ordu takviyesi geldi!"),
    ('OBJ_KAMYON', "Kamyonun kasasına bin."),
    ('INTRO_TITLE', '"Operation Last Bastion"'),
    ('INTRO_PLACE', "Sidi Rezegh yakınları, Libya"),
    ('INTRO_DATE', "23 Kasım 1941"),
    ('INTRO_INFO', "8. Ordu, Yüzbaşı Price'ın mangası, saat 17:40"),
]
PLATFORM = []

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
        if not all((r.get('sequence') or '').strip() for r in kaynak):
            kaynak = kaynak[:1]                 # sekanssiz cok satir = duplicate alias (olculdu: arac motor sesleri)
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
        ekle(HARITA + '_price_' + ad, stok[src])          # stok kaydin kendi altyazisi
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
    # arac motor sesleri (vehicles/<tur> dosyasindaki Snd alanlari; stokta loadspec kisitli -> kullanici: crusader sessizdi)
    for t_ in ('crusader', 'panzer2', 'truck', 'halftrack'):
        adaylar |= {t_ + '_idle_low', t_ + '_idle_high', t_ + '_engine_low', t_ + '_engine_high'}
    adaylar |= {'crusader_turret_spin', 'crusader_turret_stop', 'panzer2_turret_spin', 'panzer2_turret_stop'}
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
        if r['name'].lower().startswith(HARITA + '_price_') and (r['file'].lower().endswith('null.wav') or not r.get('subtitle')):
            sorun.append('PRICE SESSIZ/ALTYAZISIZ: %s %s' % (r['name'], r['file']))
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
        ('TELSIZ', "Tuşa BAS: [&&1] Telsizle karargâha bilgi ver."),
        ('PATLAYICI', "Tuşa BAS: [&&1] Patlayıcıyı yerleştir."),
        ('KAMYON', "Tuşa BAS: [&&1] Kamyonun kasasına bin."),
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
